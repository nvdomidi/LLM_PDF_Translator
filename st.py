import os
import tempfile
from pathlib import Path
from typing import IO

import streamlit as st
import yaml
from dotenv import load_dotenv

from core.extract import get_page_count
from core.translate import translate_pdf_preserve_layout
from styles import apply_custom_styles

CONFIG_FILE = Path("config.yaml")
ENV_FILE = Path(".env")


def load_config():
    # Load environment variables from .env into os.environ
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)

    # Start with config from YAML
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f) or {}

    # Merge in all environment variables
    for key, value in os.environ.items():
        config[key.lower()] = value

    return config


# Page configuration
st.set_page_config(
    page_title="PDF Translator",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply custom styling
apply_custom_styles()

# App title and description
st.title("📄 LLM PDF Translator")

# Language options
COMMON_LANGUAGES = [
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


def validate_inputs(
    pdf_file: IO[bytes],
    src_lang: str,
    tgt_lang: str,
    start_page: int,
    end_page: int,
    page_count: int,
):
    """Validate all inputs and return list of errors."""
    errors = []

    if pdf_file is None:
        errors.append("❌ Please upload a PDF first.")
    if src_lang == tgt_lang:
        errors.append("❌ Source and target languages must be different.")
    if end_page < start_page:
        errors.append("❌ End page must be greater than or equal to start page.")
    if page_count and (start_page < 1 or end_page > page_count):
        errors.append("❌ Selected page range is out of bounds.")

    return errors


def show_translation_summary(pdf_file, start_page, end_page, src_lang, tgt_lang):
    """Show translation summary metrics."""
    st.markdown("### Translation Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pages Translated", f"{start_page}-{end_page}")
    with col2:
        st.metric("Source Language", src_lang.split()[0])
    with col3:
        st.metric("Target Language", tgt_lang.split()[0])

    with open("output.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    # Download button
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="output.pdf",
        mime="application/pdf",
    )


def show_instructions():
    """Show usage instructions when no file is uploaded."""
    st.markdown("""
    ### 🎯 How to use:
    1. **Upload** a PDF file using the file uploader above
    2. **Select** source and target languages  
    3. **Choose** the page range you want to translate
    4. **Click** the Translate button to start the process
    
    *Ready to transform your documents with AI-powered translation!*
    """)


# Main app logic
def main():
    # File upload section
    uploaded_pdf = st.file_uploader(
        "Upload PDF file", type=["pdf"], help="Select a PDF file to translate"
    )

    if uploaded_pdf:
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            pdf_file.write(uploaded_pdf.read())

        # Show file info
        file_size_mb = len(uploaded_pdf.getvalue()) / (1024 * 1024)
        st.info(
            f"📄 **{uploaded_pdf.name}** ({file_size_mb:.2f} MB) loaded successfully!"
        )

        # Language selection
        col1, col2 = st.columns(2)
        with col1:
            src_lang = st.selectbox(
                "From", options=COMMON_LANGUAGES, index=0, key="src_lang"
            )
        with col2:
            tgt_lang = st.selectbox(
                "To", options=COMMON_LANGUAGES, index=1, key="tgt_lang"
            )

        # Get page count and set up page selection
        page_count = get_page_count(pdf_file)

        if page_count:
            st.markdown(f"**Document has {page_count} pages**")
            pcol1, pcol2 = st.columns(2)
            with pcol1:
                start_page = st.number_input(
                    "Pages from", min_value=1, max_value=page_count, value=1, step=1
                )
            with pcol2:
                end_page = st.number_input(
                    "Pages to",
                    min_value=1,
                    max_value=page_count,
                    value=page_count,
                    step=1,
                )
        else:
            st.warning(
                "Could not detect page count. You can still enter a page range manually."
            )
            pcol1, pcol2 = st.columns(2)
            with pcol1:
                start_page = st.number_input("Pages from", min_value=1, value=1, step=1)
            with pcol2:
                end_page = st.number_input("Pages to", min_value=1, value=1, step=1)

        # Translation button and logic
        if st.button("🚀 Translate", type="primary", use_container_width=True):
            # Validate inputs
            errors = validate_inputs(
                uploaded_pdf, src_lang, tgt_lang, start_page, end_page, page_count
            )

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Perform translation with progress bar
                progress_bar = st.progress(0)
                with st.spinner("🔄 Translating your document..."):
                    config = load_config()
                    with open(pdf_file.name, "rb") as f:
                        translate_pdf_preserve_layout(
                            f,
                            "output.pdf",
                            config,
                            src_lang,
                            tgt_lang,
                            start_page,
                            end_page,
                            progress_callback=progress_bar.progress,
                        )

                progress_bar.empty()
                st.success("✅ Translation completed successfully!")

                show_translation_summary(
                    pdf_file, start_page, end_page, src_lang, tgt_lang
                )
    else:
        # Show instructions when no file uploaded
        show_instructions()


if __name__ == "__main__":
    main()
