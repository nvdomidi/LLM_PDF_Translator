from typing import IO

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


def summarize_doc(pdf_file: IO[bytes], client: BaseClient = None) -> str:
    # Client should be provided beforehand
    if client is None:
        return ""

    docs = extract_text(pdf_file, chunk_size=10000)
    summaries = []
    for doc in docs:
        summary = summarize_chunk(doc, client)
        print("summary:", summary)
        summaries.append(summary)

    all_summaries = "\n".join(summaries)

    if len(summaries) > 1:
        summary = summarize_chunk(all_summaries)
    else:
        summary = all_summaries

    return summary
