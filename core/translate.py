# from typing import IO

from langchain_ollama import ChatOllama

# from core.extract import extract_text
from core.prompt import translate_prompt


def translate_chunk(chunk: str, source_lang: str, target_lang: str) -> str:
    llm = ChatOllama(
        model="gemma3:1b",
        base_url="http://ollama:11434",
    )
    prompt = translate_prompt(chunk, source_lang, target_lang)
    resp = llm.invoke(prompt)
    return resp


#
# def translate_doc(pdf_file: IO[bytes]) -> str:
#     docs = extract_text(pdf_file, chunk_size=10000)
#     summaries = []
#     for doc in docs:
#         summary = summarize_chunk(doc)
#         summaries.append(summary.content)
#
#     all_summaries = "\n".join(summaries)
#     summary = summarize_chunk(all_summaries)
#
#     return summary.content
