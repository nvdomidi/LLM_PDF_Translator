from typing import IO

import streamlit as st
from langchain_ollama import ChatOllama
from openai import OpenAI

from core.extract import extract_text
from core.prompt import translate_prompt, translate_prompt_with_context
from core.summarize import summarize_doc


def translate_chunk(chunk: str, source_lang: str, target_lang: str) -> str:
    llm = ChatOllama(
        model="gemma3:1b",
        base_url="http://ollama:11434",
    )
    prompt = translate_prompt(chunk, source_lang, target_lang)
    resp = llm.invoke(prompt)
    return resp


def translate_chunk_with_context(
    chunk: str,
    summary: str,
    source_lang: str,
    target_lang: str,
) -> str:
    # llm = ChatOllama(
    #     model="gemma3:1b",
    #     base_url="http://ollama:11434",
    # )
    prompt = translate_prompt_with_context(chunk, summary, source_lang, target_lang)
    # resp = llm.invoke(prompt)
    # return resp
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="OPENROUTER-API-KEY",
    )
    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def translate_doc(pdf_file: IO[bytes], source_lang: str, target_lang: str) -> str:
    summary = summarize_doc(pdf_file)
    st.markdown(summary)
    docs = extract_text(pdf_file, chunk_size=3000)

    translated_chunks = []

    for i, doc in enumerate(docs):
        translated_chunk = translate_chunk_with_context(
            doc, summary, source_lang, target_lang
        )

        translated_chunks.append(translated_chunk)

        print(translated_chunk)

        st.markdown(
            f"<div style='direction: rtl; text-align: right;'>{translated_chunk}</div>",
            unsafe_allow_html=True,
        )

    all_translations = "\n".join(translated_chunks)

    return all_translations
