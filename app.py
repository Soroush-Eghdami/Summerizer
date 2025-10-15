import io
import time
import streamlit as st

from summarizer import PdfSummarizer, SummarizationConfig, create_default_summarizer


st.set_page_config(page_title="PDF Summarizer", page_icon="📝", layout="centered")


@st.cache_resource(show_spinner=False)
def get_summarizer(config: SummarizationConfig) -> PdfSummarizer:
    return PdfSummarizer(config)


def main() -> None:
    st.title("📝 PDF to English Summary")
    st.write("Upload a PDF to generate a concise English summary.")

    with st.sidebar:
        st.header("Settings")
        model_name = st.text_input("Model", value="facebook/bart-large-cnn")
        max_chunk_tokens = st.slider("Max chunk tokens", min_value=256, max_value=1500, value=900, step=32)
        chunk_overlap_tokens = st.slider("Chunk overlap tokens", min_value=0, max_value=400, value=100, step=10)
        min_summary_tokens = st.slider("Min summary tokens", min_value=16, max_value=256, value=64, step=8)
        max_summary_tokens = st.slider("Max summary tokens", min_value=64, max_value=512, value=256, step=8)
        do_sample = st.checkbox("Use sampling", value=False)
        temperature = st.slider("Temperature", min_value=0.1, max_value=2.0, value=1.0, step=0.1)

    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded is not None:
        pdf_bytes: bytes = uploaded.read()

        config = SummarizationConfig(
            model_name=model_name,
            device=None,  # set to 0 manually if running on GPU
            max_chunk_tokens=max_chunk_tokens,
            chunk_overlap_tokens=chunk_overlap_tokens,
            min_summary_tokens=min_summary_tokens,
            max_summary_tokens=max_summary_tokens,
            do_sample=do_sample,
            temperature=temperature,
        )

        summarizer = get_summarizer(config)

        with st.spinner("Extracting text and generating summary..."):
            start = time.time()
            full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
            elapsed = time.time() - start

        st.success(f"Done in {elapsed:.1f}s")
        st.subheader("Summary")
        st.write(summary or "(Empty summary)")

        with st.expander("Show extracted text"):
            st.text_area("Extracted Text", value=full_text, height=300)

    else:
        st.info("Upload a PDF to begin.")


if __name__ == "__main__":
    main()


