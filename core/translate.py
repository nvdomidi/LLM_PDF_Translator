import os
from typing import IO

import pymupdf

from core.client.base import BaseClient
from core.client.ollama import OllamaClient
from core.client.openai import OpenAIClient
from core.extract import extract_text
from core.prompt import translate_prompt, translate_prompt_with_context
from core.summarize import summarize_doc


def translate_chunk(
    chunk: str, source_lang: str, target_lang: str, client: BaseClient = None
) -> str:
    if client is None:
        return ""
    prompt = translate_prompt(chunk, source_lang, target_lang)
    resp = client.ask(prompt)
    return resp


def translate_chunk_with_context(
    chunk: str,
    summary: str,
    source_lang: str,
    target_lang: str,
    client: BaseClient = None,
) -> str:
    if client is None:
        return ""
    prompt = translate_prompt_with_context(chunk, summary, source_lang, target_lang)
    resp = client.ask(prompt)
    return resp


def translate_pdf(
    pdf_file: IO[bytes],
    config: dict,
    src_lang: str,
    tgt_lang: str,
    start_page: int,
    end_page: int,
) -> str:
    """Summarizes the document, then translates each chunk of text"""

    # Initialize client
    client = OllamaClient(
        model=config["model"],
        base_url=config["base_url"],
    )

    # Summarize the document
    summary = summarize_doc(pdf_file, client)

    # Extract text chunks
    docs = extract_text(pdf_file, chunk_size=3000)

    # Translate each chunk of text
    translated_chunks = []
    for i, doc in enumerate(docs):
        translated_chunk = translate_chunk_with_context(
            doc, summary, src_lang, tgt_lang, client
        )
        translated_chunks.append(translated_chunk)

    all_translations = "\n".join(translated_chunks)

    #
    # st.markdown(
    #     f"<div style='direction: rtl; text-align: right;'>{translated_doc}</div>",
    #     unsafe_allow_html=True,
    # )

    return summary, all_translations


def translate_pdf_preserve_layout(
    pdf_file: IO[bytes],
    output_path: str,
    config: dict,
    src_lang: str,
    tgt_lang: str,
    start_page: int,
    end_page: int,
) -> None:
    """Translate a PDF and write a new PDF preserving the original layout.

    Only pages within ``start_page`` and ``end_page`` (1-indexed, inclusive)
    are processed and included in the output document.
    """

    # client = OllamaClient(model=config["model"], base_url=config["base_url"])

    client = OpenAIClient(
        api_key=os.environ["OPENROUTER_API_KEY"],
        model=config["model"],
        base_url=config["base_url"],
    )

    # Summarize the document to provide translation context
    summary = summarize_doc(pdf_file, client)

    # Reset the file pointer after reading during summarization
    pdf_file.seek(0)

    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    doc.select(list(range(start_page - 1, end_page)))

    rtl = True

    font_file1 = "fonts/Yekan.ttf"
    css1 = (
        """@font-face {font-family: sans-serif; src: url("%s");}
    body {font-family:sans-serif;} """
        % font_file1
    )

    for page in doc:
        blocks = page.get_text("blocks")
        rects = []
        translations = []

        for block in blocks:
            x0, y0, x1, y1, text = block[:5]
            if not text.strip():
                continue

            translated = translate_chunk_with_context(
                text, summary, src_lang, tgt_lang, client
            )

            rect = pymupdf.Rect(x0, y0, x1, y1)
            rects.append(rect)
            translations.append(translated)
            page.add_redact_annot(rect, fill=(1, 1, 1))

        # Remove only the original text
        page.apply_redactions(images=0, graphics=0, text=0)

        align = 2 if rtl else 0
        for rect, text in zip(rects, translations):
            fontsize = rect.y1 - rect.y0 - 1
            text = f"""
            <div dir="rtl">{text}</div>
            """
            page.insert_htmlbox(rect, text, css=css1)
            # while fontsize > 5:
            #     area = page.insert_textbox(rect, text, fontsize=fontsize, fontname="F0")
            #     if area >= 0:
            #         break
            #     fontsize -= 1

    doc.save(output_path)
