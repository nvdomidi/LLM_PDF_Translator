from typing import IO, Callable, Tuple

from core.client.base import BaseClient
from core.extract import extract_text
from core.prompt import summarize_prompt


def summarize_chunk(chunk: str, client: BaseClient = None) -> str:
    # Client should be provided beforehand
    if client is None:
        return ""

    prompt = summarize_prompt(chunk)
    resp = client.ask(prompt)
    return resp


def summarize_doc(
    pdf_file: IO[bytes],
    client: BaseClient = None,
    progress_callback: Callable[[int], None] | None = None,
    progress_range: Tuple[int, int] = (0, 20),
) -> str:
    """Summarize a document with optional progress updates."""

    # Client should be provided beforehand
    if client is None:
        return ""

    docs = extract_text(pdf_file, chunk_size=10000)
    summaries = []

    total_chunks = len(docs)
    start, end = progress_range

    for idx, doc in enumerate(docs, start=1):
        summary = summarize_chunk(doc, client)
        print("summary:", summary)
        summaries.append(summary)

        if progress_callback and total_chunks:
            progress = start + (end - start) * idx / total_chunks
            progress_callback(int(progress))

    if not summaries:
        if progress_callback:
            progress_callback(end)
        return ""

    all_summaries = "\n".join(summaries)

    if len(summaries) > 1:
        summary = summarize_chunk(all_summaries)
    else:
        summary = all_summaries

    return summary
