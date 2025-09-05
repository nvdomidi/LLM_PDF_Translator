from typing import IO

import pymupdf
import pymupdf4llm
from langchain.text_splitter import MarkdownTextSplitter


def get_page_count(pdf_file: IO[bytes]) -> int:
    doc = pymupdf.Document(pdf_file)
    num_pages = doc.page_count
    return num_pages


def extract_layout(pdf_file: IO[bytes]):
    doc = pymupdf.Document(pdf_file)

    for page in doc:
        blist = page.get_text("blocks")
        for block in blist:
            r = pymupdf.Rect(block[:4])
            page.draw_rect(r, color=(1, 0, 0))

    doc.save("output.pdf")


def extract_text(pdf_file: IO[bytes], chunk_size: int) -> list[pymupdf.Document]:
    md_text = pymupdf4llm.to_markdown(pdf_file)

    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    docs = splitter.create_documents([md_text])

    return docs
