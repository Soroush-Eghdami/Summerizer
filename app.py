import io
import os
import time
import tempfile
import requests
import streamlit as st
from dotenv import load_dotenv

from summarizer import PdfSummarizer, SummarizationConfig

# Load .env file for GROQ_API_KEY
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Page configuration ---
st.set_page_config(page_title="PDF/Text/Voice Summarizer", page_icon="📝", layout="centered")

# --- Real Groq transcription ---
def transcribe_with_groq(audio_path: str, model: str = "whisper-large-v3-turbo") -> str:
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not configured"
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    with open(audio_path, "rb") as f:
        files = {
            "file": (os.path.basename(audio_path), f, "application/octet-stream"),
            "model": (None, model),
        }
        resp = requests.post(url, headers=headers, files=files, timeout=120)
    if resp.status_code != 200:
        return f"Error: {resp.status_code} - {resp.text}"
    return resp.json().get("text", "")

# --- Cache summarizer ---
@st.cache_resource(show_spinner=False)
def get_summarizer(config_hash: str) -> 'PdfSummarizer':
    config = SummarizationConfig()
    return PdfSummarizer(config)

# --- Main app ---
def main() -> None:
    st.title("📝 Multi-Input Summarizer")
    st.write("Upload a PDF, type/paste text, or upload a voice message to get a summary.")

    # --- Sidebar settings ---
    with st.sidebar:
        st.header("Settings")
        model_name = st.text_input("Model", value="facebook/bart-large-cnn")
        max_chunk_tokens = st.slider("Max chunk tokens", 256, 1500, 900, 32)
        chunk_overlap_tokens = st.slider("Chunk overlap tokens", 0, 400, 100, 10)
        min_summary_tokens = st.slider("Min summary tokens", 16, 256, 64, 8)
        max_summary_tokens = st.slider("Max summary tokens", 64, 512, 256, 8)
        do_sample = st.checkbox("Use sampling", False)
        temperature = st.slider("Temperature", 0.1, 2.0, 1.0, 0.1)

    config_hash = f"{model_name}_{max_chunk_tokens}_{chunk_overlap_tokens}_{min_summary_tokens}_{max_summary_tokens}_{do_sample}_{temperature}"
    summarizer = get_summarizer(config_hash)

    # --- Text input ---
    text_input = st.text_area("Enter text to summarize:")
    if text_input.strip():
        with st.spinner("Generating summary for text..."):
            start = time.time()
            summary = summarizer.summarize_text(text_input)
            st.subheader("Summary (Text)")
            st.write(summary or "(Empty summary)")
            st.success(f"✅ Done in {time.time() - start:.1f}s")

    # --- PDF input ---
    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if pdf_file:
        pdf_bytes = pdf_file.read()
        with st.spinner("Extracting and summarizing PDF..."):
            start = time.time()
            full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
            st.subheader("Summary (PDF)")
            st.write(summary or "(Empty summary)")
            st.success(f"✅ Done in {time.time() - start:.1f}s")
            with st.expander("Show extracted text"):
                st.text_area("Extracted Text", value=full_text, height=300)

    # --- Voice input ---
    voice_file = st.file_uploader("Upload a voice file", type=["mp3", "wav", "ogg"])
    if voice_file:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(voice_file.read())
            tmp_path = tmp.name
        with st.spinner("Transcribing and summarizing voice..."):
            start = time.time()
            text = transcribe_with_groq(tmp_path)
            if text and not text.startswith("Error"):
                summary = summarizer.summarize_text(text)
                st.subheader("Summary (Voice)")
                st.write(summary or "(Empty summary)")
                with st.expander("Show transcribed text"):
                    st.text_area("Transcribed Text", value=text, height=200)
            else:
                st.warning(text or "Could not transcribe voice.")
            st.success(f"✅ Done in {time.time() - start:.1f}s")
        try:
            os.remove(tmp_path)
        except OSError:
            pass

if __name__ == "__main__":
    main()
