from concurrent.futures import ThreadPoolExecutor
from typing import IO, Callable, Iterable, List, Tuple, TypeVar

import pymupdf

from core.client.base import BaseClient

# from core.client.ollama import OllamaClient
from core.client.openai import OpenAIClient
from core.extract import extract_text
from core.prompt import rewrite_prompt, rewrite_prompt_with_context
from core.summarize import summarize_doc

MIN_WORDS_TO_REWRITE = 10
DEFAULT_MAX_WORKERS = 4
I = TypeVar("I")
O = TypeVar("O")


def _map_concurrently(func: Callable[[I], O], items: Iterable[I]) -> list[O]:
    """Apply ``func`` to ``items`` concurrently while preserving order."""

    items = list(items)
    if not items:
        return []

    max_workers = min(DEFAULT_MAX_WORKERS, len(items))
    if max_workers <= 1:
        return [func(item) for item in items]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(func, items))


def _should_rewrite(text: str, threshold: int = MIN_WORDS_TO_REWRITE) -> bool:
    """Return True when the text exceeds the rewrite word threshold."""

    words = text.split()
    return len(words) > threshold


def rewrite_chunk(chunk: str, instruction: str, client: BaseClient = None) -> str:
    if client is None:
        return ""

    if not _should_rewrite(chunk):
        return chunk
    prompt = rewrite_prompt(chunk, instruction)
    resp = client.ask(prompt)
    return resp


def rewrite_chunk_with_context(
    chunk: str,
    summary: str,
    instruction: str,
    client: BaseClient = None,
) -> str:
    if client is None:
        return ""

    if not _should_rewrite(chunk):
        return chunk

    prompt = rewrite_prompt_with_context(chunk, summary, instruction)
    resp = client.ask(prompt)
    return resp


def rewrite_pdf(
    pdf_file: IO[bytes],
    config: dict,
    instruction: str,
    start_page: int,
    end_page: int,
) -> str:
    """Summarizes the document, then rewrites each chunk of text."""

    # Initialize client
    client = OpenAIClient(
        model=config["model"],
        base_url=config["base_url"],
    )

    # Summarize the document
    summary = summarize_doc(pdf_file, client)

    # Extract text chunks
    docs = extract_text(pdf_file, chunk_size=3000)

    # Rewrite each chunk of text
    def _rewrite(doc):
        rewritten_chunk = rewrite_chunk_with_context(doc, summary, instruction, client)
        if not rewritten_chunk:
            return doc
        return rewritten_chunk

    rewritten_chunks = _map_concurrently(_rewrite, docs)

    all_rewrites = "\n".join(rewritten_chunks)

    return summary, all_rewrites


def rewrite_pdf_preserve_layout(
    pdf_file: IO[bytes],
    output_path: str,
    config: dict,
    instruction: str,
    start_page: int,
    end_page: int,
    progress_callback: Callable[[int], None] | None = None,
) -> None:
    """Rewrite a PDF and write a new PDF preserving the original layout.

    Only pages within ``start_page`` and ``end_page`` (1-indexed, inclusive)
    are processed and included in the output document.
    """

    client = OpenAIClient(model=config["model"], base_url=config["base_url"])

    # Summarize the document to provide rewriting context
    summary = summarize_doc(
        pdf_file, client, progress_callback=progress_callback, progress_range=(0, 20)
    )

    # Reset the file pointer after reading during summarization
    pdf_file.seek(0)

    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    doc.select(list(range(start_page - 1, end_page)))

    # Count total blocks to rewrite
    total_blocks = 0
    for i in range(doc.page_count):
        page = doc[i]
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4]
            if text.strip():
                total_blocks += 1

    processed_blocks = 0

    for i in range(doc.page_count):
        page = doc[i]
        blocks = page.get_text("blocks")
        rects = []
        rewrites = []

        blocks_to_rewrite: List[Tuple[pymupdf.Rect, str]] = []

        for block in blocks:
            x0, y0, x1, y1, text = block[:5]
            if not text.strip():
                continue

            if _should_rewrite(text):
                rect = pymupdf.Rect(x0, y0, x1, y1)
                blocks_to_rewrite.append((rect, text))
                page.add_redact_annot(rect, fill=(1, 1, 1))

            processed_blocks += 1
            if progress_callback and total_blocks:
                progress = 20 + 80 * processed_blocks / total_blocks
                progress_callback(int(progress))

        if blocks_to_rewrite:
            texts = [text for _, text in blocks_to_rewrite]

            def _rewrite(text: str) -> str:
                rewritten = rewrite_chunk_with_context(
                    text, summary, instruction, client
                )
                return rewritten or text

            rewritten_texts = _map_concurrently(_rewrite, texts)

            for (rect, _), rewritten in zip(blocks_to_rewrite, rewritten_texts):
                rects.append(rect)
                rewrites.append(rewritten)

        # Remove only the original text
        page.apply_redactions(images=0, graphics=0, text=0)

        for rect, text in zip(rects, rewrites):
            html_text = f"""<div>{text}</div>"""
            page.insert_htmlbox(rect, html_text)

    doc.save(output_path)

    if progress_callback:
        progress_callback(100)
