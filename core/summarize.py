from typing import IO

from langchain_ollama import ChatOllama

from core.extract import extract_text
from core.prompt import summarize_prompt


def summarize_chunk(chunk: str) -> str:
    llm = ChatOllama(
        model="gemma3:4b",
        base_url="http://ollama:11434",
    )
    prompt = summarize_prompt(chunk)
    resp = llm.invoke(prompt)
    return resp


def summarize_doc(pdf_file: IO[bytes]) -> str:
    docs = extract_text(pdf_file)
    summaries = []
    for doc in docs:
        summary = summarize_chunk(doc)
        print(summary)
        summaries.append(summary)

        return " ".join(summaries)
