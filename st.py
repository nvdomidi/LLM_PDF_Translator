import os
import tempfile
from pathlib import Path
from typing import IO

import streamlit as st
import yaml
from dotenv import load_dotenv

from core.extract import get_page_count
from core.rewrite import rewrite_pdf_preserve_layout
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
    page_title="PDF Rewriter",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply custom styling
apply_custom_styles()

# App title and description
st.title("📄 LLM PDF Rewriter")


def validate_inputs(
    pdf_file: IO[bytes],
    prompt: str,
    start_page: int,
    end_page: int,
    page_count: int,
):
    """Validate all inputs and return list of errors."""
    errors = []

    if pdf_file is None:
        errors.append("❌ Please upload a PDF first.")
    if not prompt or not prompt.strip():
        errors.append("❌ Please provide a rewriting prompt.")
    if end_page < start_page:
        errors.append("❌ End page must be greater than or equal to start page.")
    if page_count and (start_page < 1 or end_page > page_count):
        errors.append("❌ Selected page range is out of bounds.")

    return errors


def show_completion(download_path: str):
    """Display completion message and download button."""
    st.success("Rewriting completed successfuly!")

    with open(download_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

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
    2. **Enter** a prompt that describes how you'd like the text rewritten
    3. **Choose** the page range you want to rewrite
    4. **Click** the Rewrite button to start the process

    *Ready to transform your documents with AI-powered rewriting!*
    """)


# Main app logic
def main():
    # File upload section
    uploaded_pdf = st.file_uploader(
        "Upload PDF file", type=["pdf"], help="Select a PDF file to rewrite"
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

        prompt = st.text_area(
            "Rewriting prompt",
            placeholder="e.g., Rewrite for a high school student",
            help="Describe how you want the document to be rewritten.",
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

        # Rewrite button and logic
        if st.button("✍️ Rewrite", type="primary", use_container_width=True):
            # Validate inputs
            errors = validate_inputs(
                uploaded_pdf, prompt, start_page, end_page, page_count
            )

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Perform rewriting with progress bar
                progress_bar = st.progress(0)
                with st.spinner("🔄 Rewriting your document..."):
                    config = load_config()
                    with open(pdf_file.name, "rb") as f:
                        rewrite_pdf_preserve_layout(
                            f,
                            "output.pdf",
                            config,
                            prompt,
                            start_page,
                            end_page,
                            progress_callback=progress_bar.progress,
                        )

                progress_bar.empty()

                show_completion("output.pdf")
    else:
        # Show instructions when no file uploaded
        show_instructions()


if __name__ == "__main__":
    main()
