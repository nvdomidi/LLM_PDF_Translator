import io
from typing import Optional

import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="PDF Translator (Dummy)", page_icon="📄")
st.title("📄 LLM PDF Translator")
st.caption("Upload a PDF, choose languages, select a page range, then press Translate.")


def get_pdf_page_count(file_bytes: bytes) -> Optional[int]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        return len(reader.pages)
    except Exception as e:
        st.error(f"Error: {e}")
        return None


uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"])

# Language pickers
common_langs = [
    "English",
    "Persian فارسی",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Turkish",
    "Arabic",
    "Chinese",
    "Japanese",
    "Korean",
    "Hindi",
    "Azerbaijani",
]

if uploaded_pdf:
    col1, col2 = st.columns(2)
    with col1:
        src_lang = st.selectbox("From", options=common_langs, index=0, key="src_lang")
    with col2:
        tgt_lang = st.selectbox("To", options=common_langs[1:], index=0, key="tgt_lang")


# Determine page count
page_count = None
if uploaded_pdf is not None:
    file_bytes = uploaded_pdf.getvalue()
    page_count = get_pdf_page_count(file_bytes)

    # Page range inputs
    if page_count:
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            start_page = st.number_input(
                "Pages from", min_value=1, max_value=page_count, value=1, step=1
            )
        with pcol2:
            end_page = st.number_input(
                "Pages to", min_value=1, max_value=page_count, value=page_count, step=1
            )
    else:
        st.warning(
            "Could not detect page count. You can still enter a page range manually."
        )
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            start_page = st.number_input("Pages from", min_value=1, value=1, step=1)
        with pcol2:
            end_page = st.number_input(
                "Pages to", min_value=start_page, value=start_page, step=1
            )

    # Validate inputs and translate
    translate_clicked = st.button("Translate", type="primary", use_container_width=True)

    if translate_clicked:
        # Basic validations
        if uploaded_pdf is None:
            st.error("Please upload a PDF first.")
        elif src_lang == tgt_lang and src_lang != "Auto-detect":
            st.error("Source and target languages must be different.")
        elif end_page < start_page:
            st.error("Pages to must be greater than or equal to Pages from.")
        elif page_count and (start_page < 1 or end_page > page_count):
            st.error("Selected page range is out of bounds.")
        else:
            with st.spinner("Translating..."):
                st.success("Done. This was a dummy translation call.")
