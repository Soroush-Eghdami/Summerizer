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
st.set_page_config(
    page_title="AI Summarizer | Text, PDF & Audio",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Bootstrap-style UI ---
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .stApp > header {
        background-color: transparent;
    }
    
    /* Custom button styling */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Card styling */
    .summary-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Input text area styling */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        background: #f8f9fa;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 3rem;
    }
    
    /* Alert boxes */
    .stSuccess {
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    
    .stWarning {
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    
    .stError {
        border-radius: 10px;
        border-left: 5px solid #dc3545;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea;
    }
    
    /* Custom title */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Feature cards */
    .feature-box {
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        background: white;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
    }
    
    .feature-box:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Progress bar */
    .progress {
        height: 10px;
        border-radius: 10px;
        background: #e9ecef;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

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
def get_summarizer(model_name: str, max_chunk: int, chunk_overlap: int, 
                   min_tokens: int, max_tokens: int, sample: bool, temp: float) -> 'PdfSummarizer':
    config = SummarizationConfig(
        model_name=model_name,
        max_chunk_tokens=max_chunk,
        chunk_overlap_tokens=chunk_overlap,
        min_summary_tokens=min_tokens,
        max_summary_tokens=max_tokens,
        do_sample=sample,
        temperature=temp
    )
    return PdfSummarizer(config)

# --- Main app ---
def main() -> None:
    # Header
    st.markdown('<h1 class="main-title">🤖 AI Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your text, PDFs, and audio into concise summaries using advanced AI</p>', unsafe_allow_html=True)
    
    # Feature boxes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📝</div>
            <h3>Text</h3>
            <p>Summarize any text instantly</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">📄</div>
            <h3>PDF</h3>
            <p>Extract and summarize documents</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-box">
            <div class="feature-icon">🎤</div>
            <h3>Audio</h3>
            <p>Transcribe and summarize voice</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar with settings
    with st.sidebar:
        st.markdown("### ⚙️ Advanced Settings")
        st.markdown("---")
        
        model_name = st.selectbox(
            "Model",
            ["facebook/bart-large-cnn", "facebook/bart-large-xsum", "google/pegasus-xsum"],
            index=0,
            help="Choose the AI model for summarization"
        )
        
        max_chunk_tokens = st.slider(
            "Max chunk tokens",
            256, 1500, 900, 32,
            help="Maximum tokens per chunk for long documents"
        )
        
        chunk_overlap_tokens = st.slider(
            "Chunk overlap tokens",
            0, 400, 100, 10,
            help="Tokens to overlap between chunks"
        )
        
        min_summary_tokens = st.slider(
            "Min summary tokens",
            16, 256, 64, 8,
            help="Minimum tokens in summary"
        )
        
        max_summary_tokens = st.slider(
            "Max summary tokens",
            64, 512, 256, 8,
            help="Maximum tokens in summary"
        )
        
        do_sample = st.checkbox("Use sampling", False, help="Enable sampling for diverse summaries")
        
        temperature = st.slider(
            "Temperature",
            0.1, 2.0, 1.0, 0.1,
            help="Temperature for generation (higher = more creative)"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Usage")
        st.info("Upload files or enter text below to get started!")

    # Get summarizer with user settings
    summarizer = get_summarizer(
        model_name=model_name,
        max_chunk=max_chunk_tokens,
        chunk_overlap=chunk_overlap_tokens,
        min_tokens=min_summary_tokens,
        max_tokens=max_summary_tokens,
        sample=do_sample,
        temp=temperature
    )

    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 Text", "📄 PDF", "🎤 Audio"])

    with tab1:
        st.markdown("### Enter your text here")
        text_input = st.text_area(
            "Paste or type the text you want to summarize:",
            height=150,
            placeholder="Enter your text here..."
        )
        
        if st.button("📊 Summarize Text", type="primary"):
            if text_input.strip():
                with st.spinner("🔄 Generating summary..."):
                    start = time.time()
                    summary = summarizer.summarize_text(text_input)
                    elapsed = time.time() - start
                    
                    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                    st.markdown("### ✨ Summary")
                    st.markdown(summary or "(Empty summary)")
                    st.markdown(f'<p style="color: #6c757d; font-size: 0.9rem; margin-top: 1rem;">⏱️ Completed in {elapsed:.1f}s</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.success(f"✅ Summary generated successfully!")
            else:
                st.warning("⚠️ Please enter some text to summarize.")

    with tab2:
        st.markdown("### Upload a PDF file")
        st.markdown("Select a PDF document to extract text and generate a summary")
        
        pdf_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF file (max 200MB)"
        )
        
        if pdf_file is not None:
            if st.button("📊 Summarize PDF", type="primary"):
                pdf_bytes = pdf_file.read()
                with st.spinner("🔄 Extracting text and generating summary..."):
                    start = time.time()
                    full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
                    elapsed = time.time() - start
                    
                    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                    st.markdown("### ✨ Summary")
                    st.markdown(summary or "(Empty summary)")
                    st.markdown(f'<p style="color: #6c757d; font-size: 0.9rem; margin-top: 1rem;">⏱️ Completed in {elapsed:.1f}s</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.expander("📖 View Extracted Text"):
                        st.text_area("Full text from PDF:", value=full_text, height=300, disabled=True)
                    
                    st.success(f"✅ PDF summarized successfully!")

    with tab3:
        st.markdown("### Upload an audio file")
        st.markdown("Upload voice recordings (MP3, WAV, OGG) to transcribe and summarize")
        
        if not GROQ_API_KEY:
            st.error("⚠️ GROQ_API_KEY not configured. Audio transcription is unavailable.")
        else:
            voice_file = st.file_uploader(
                "Choose an audio file",
                type=["mp3", "wav", "ogg"],
                help="Upload an audio file for transcription and summarization"
            )
            
            if voice_file is not None:
                if st.button("📊 Transcribe & Summarize", type="primary"):
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(voice_file.read())
                        tmp_path = tmp.name
                    
                    try:
                        with st.spinner("🔄 Transcribing audio and generating summary..."):
                            start = time.time()
                            text = transcribe_with_groq(tmp_path)
                            
                            if text and not text.startswith("Error"):
                                summary = summarizer.summarize_text(text)
                                elapsed = time.time() - start
                                
                                st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                                st.markdown("### ✨ Summary")
                                st.markdown(summary or "(Empty summary)")
                                st.markdown(f'<p style="color: #6c757d; font-size: 0.9rem; margin-top: 1rem;">⏱️ Completed in {elapsed:.1f}s</p>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                with st.expander("🎙️ View Transcribed Text"):
                                    st.text_area("Transcribed text:", value=text, height=200, disabled=True)
                                
                                st.success(f"✅ Audio transcribed and summarized successfully!")
                            else:
                                st.error(text or "❌ Could not transcribe the audio file.")
                                st.warning("Please check your GROQ_API_KEY and try again.")
                    finally:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>Built with ❤️ using Streamlit, Transformers & Groq API</p>
        <p style="font-size: 0.9rem;">Powered by AI • Fast • Reliable</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
