from typing import IO
import io

import pymupdf
from core.client.base import BaseClient
from core.client.ollama import OllamaClient
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
    text: str,
    config: dict,
) -> bytes:
    """Insert translated text into the PDF while preserving layout.

    This function embeds a Persian-capable font in the document so that
    inserted text renders correctly. The path to the font can be configured
    via ``config['font_path']``.
    """

    doc = pymupdf.Document(pdf_file)
    font_path = config.get("font_path", "fonts/BahijNazanin-Regular.ttf")

    # Load the font and embed it in the document
    fontname = doc.insert_font(fontfile=font_path)
    doc.embed_font(fontname)

    for page in doc:
        page.insert_textbox(
            page.rect,
            text,
            fontname=fontname,
            fontsize=12,
        )

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
