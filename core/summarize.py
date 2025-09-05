from typing import IO

from langchain_ollama import ChatOllama

from core.extract import extract_text
from core.prompt import summarize_prompt


def summarize_chunk(chunk: str) -> str:
    llm = ChatOllama(
        model="gemma3:1b",
        base_url="http://ollama:11434",
    )
    prompt = summarize_prompt(chunk)
    resp = llm.invoke(prompt)
    return resp


def summarize_doc(pdf_file: IO[bytes]) -> str:
    docs = extract_text(pdf_file, chunk_size=10000)
    summaries = []
    for doc in docs:
        summary = summarize_chunk(doc)
        print(summary.content)
        summaries.append(summary.content)

    all_summaries = "\n".join(summaries)
    summary = summarize_chunk(all_summaries)

    return summary.content
