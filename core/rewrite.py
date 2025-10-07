from typing import IO, Callable

import pymupdf

from core.client.base import BaseClient
from core.client.ollama import OllamaClient
from core.extract import extract_text
from core.prompt import rewrite_prompt, rewrite_prompt_with_context
from core.summarize import summarize_doc


MIN_WORDS_TO_REWRITE = 10


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
    client = OllamaClient(
        model=config["model"],
        base_url=config["base_url"],
    )

    # Summarize the document
    summary = summarize_doc(pdf_file, client)

    # Extract text chunks
    docs = extract_text(pdf_file, chunk_size=3000)

    # Rewrite each chunk of text
    rewritten_chunks = []
    for doc in docs:
        rewritten_chunk = rewrite_chunk_with_context(doc, summary, instruction, client)
        if not rewritten_chunk:
            rewritten_chunk = doc
        rewritten_chunks.append(rewritten_chunk)

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

    client = OllamaClient(model=config["model"], base_url=config["base_url"])

    # Summarize the document to provide rewriting context
    summary = summarize_doc(
        pdf_file, client, progress_callback=progress_callback, progress_range=(0, 20)
    )

    # Reset the file pointer after reading during summarization
    pdf_file.seek(0)

    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    doc.select(list(range(start_page - 1, end_page)))

    font_file1 = "fonts/Yekan.ttf"
    css1 = (
        """@font-face {font-family: sans-serif; src: url("%s");}
    body {font-family:sans-serif;} """
        % font_file1
    )

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

        for block in blocks:
            x0, y0, x1, y1, text = block[:5]
            if not text.strip():
                continue

            if _should_rewrite(text):
                rewritten = rewrite_chunk_with_context(text, summary, instruction, client)
                if not rewritten:
                    rewritten = text

                rect = pymupdf.Rect(x0, y0, x1, y1)
                rects.append(rect)
                rewrites.append(rewritten)
                page.add_redact_annot(rect, fill=(1, 1, 1))

            processed_blocks += 1
            if progress_callback and total_blocks:
                progress = 20 + 80 * processed_blocks / total_blocks
                progress_callback(int(progress))

        # Remove only the original text
        page.apply_redactions(images=0, graphics=0, text=0)

        for rect, text in zip(rects, rewrites):
            html_text = f"""<div>{text}</div>"""
            page.insert_htmlbox(rect, html_text, css=css1)

    doc.save(output_path)

    if progress_callback:
        progress_callback(100)
