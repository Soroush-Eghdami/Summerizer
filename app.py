import io
import time
import tempfile
import streamlit as st

from summarizer import PdfSummarizer

# --- Page configuration ---
st.set_page_config(page_title="PDF/Text/Voice Summarizer", page_icon="📝", layout="centered")

# --- Groq transcription placeholder (replace with real API call if needed) ---
def transcribe_with_groq(audio_path: str) -> str:
    """
    Transcribe voice file to text.
    Replace this with your Groq API or Whisper logic.
    """
    # For now, return dummy text if needed
    return "Transcribed text from audio"

# --- Cache summarizer (lazy import inside) ---
@st.cache_resource(show_spinner=False)
def get_summarizer(config_hash: str) -> 'PdfSummarizer':
    from summarizer import SummarizationConfig, PdfSummarizer  # Lazy import inside function
    config = SummarizationConfig()  # Use default BART config; override if needed via hash
    return PdfSummarizer(config)

# --- Main app ---
def main() -> None:
    st.title("📝 Multi-Input Summarizer")
    st.write("Upload a PDF, type/paste text, or upload a voice message to get a summary.")

    # --- Sidebar settings (default to BART) ---
    with st.sidebar:
        st.header("Settings")
        model_name = st.text_input("Model", value="facebook/bart-large-cnn")
        max_chunk_tokens = st.slider("Max chunk tokens", min_value=256, max_value=1500, value=900, step=32)
        chunk_overlap_tokens = st.slider("Chunk overlap tokens", min_value=0, max_value=400, value=100, step=10)
        min_summary_tokens = st.slider("Min summary tokens", min_value=16, max_value=256, value=64, step=8)
        max_summary_tokens = st.slider("Max summary tokens", min_value=64, max_value=512, value=256, step=8)
        do_sample = st.checkbox("Use sampling", value=False)
        temperature = st.slider("Temperature", min_value=0.1, max_value=2.0, value=1.0, step=0.1)

    # Hash for caching (reloads summarizer if settings change)
    config_hash = f"{model_name}_{max_chunk_tokens}_{chunk_overlap_tokens}_{min_summary_tokens}_{max_summary_tokens}_{do_sample}_{temperature}"
    summarizer = get_summarizer(config_hash)

    # --- Text input ---
    text_input = st.text_area("Enter text to summarize:")

    if text_input.strip():
        with st.spinner("Generating summary for text..."):
            start = time.time()
            summary = summarizer.summarize_text(text_input)
            elapsed = time.time() - start
        st.subheader("Summary (Text)")
        st.write(summary or "(Empty summary)")
        st.success(f"Done in {elapsed:.1f}s")

    # --- PDF input ---
    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if pdf_file:
        pdf_bytes = pdf_file.read()
        with st.spinner("Extracting text and generating summary for PDF..."):
            start = time.time()
            full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
            elapsed = time.time() - start
        st.subheader("Summary (PDF)")
        st.write(summary or "(Empty summary)")
        st.success(f"Done in {elapsed:.1f}s")
        with st.expander("Show extracted text"):
            st.text_area("Extracted Text", value=full_text, height=300)

    # --- Voice input ---
    voice_file = st.file_uploader("Upload a voice file", type=["mp3", "wav", "ogg"])
    if voice_file:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(voice_file.read())
            tmp_path = tmp.name

        with st.spinner("Transcribing voice and generating summary..."):
            start = time.time()
            text = transcribe_with_groq(tmp_path)
            if text:
                summary = summarizer.summarize_text(text)
                st.subheader("Summary (Voice)")
                st.write(summary or "(Empty summary)")
            else:
                st.warning("Could not transcribe voice.")
            elapsed = time.time() - start
            st.success(f"Done in {elapsed:.1f}s")

if __name__ == "__main__":
    main()