# 🤖 AI Summarizer - Text, PDF & Audio Summarization

A beautiful, modern AI-powered summarization application that can summarize text, PDF documents, and audio files using advanced transformer models and Groq API.

![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🎨 Beautiful Modern UI
- **Bootstrap-inspired design** with gradient buttons and smooth animations
- **Responsive layout** that works on desktop and mobile
- **Interactive cards** and modern color scheme
- **Professional styling** with custom CSS

### 📝 Multi-Modal Summarization
- **Text**: Summarize any text input instantly
- **PDF**: Extract and summarize documents automatically
- **Audio**: Transcribe and summarize voice recordings using Groq's Whisper

### ⚙️ Advanced Configuration
- Multiple AI models (BART, PEGASUS, etc.)
- Customizable chunk size and overlap
- Configurable summary length
- Sampling and temperature controls
- Real-time settings in sidebar

### 🤖 Telegram Bot Support
- Summarize text messages
- Transcribe and summarize voice messages
- Process PDF files
- All from your Telegram chat!

---

## 📸 Screenshots

### Main Interface
The application features a beautiful, modern UI with:
- Gradient-powered buttons with hover effects
- Feature cards showcasing capabilities
- Tab-based interface for different input types
- Real-time advanced settings in the sidebar

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-summarizer.git
cd ai-summarizer
```

2. **Create a virtual environment**
```bash
python -m venv botenv
# Windows
botenv\Scripts\activate
# Linux/macOS
source botenv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here  # Optional
```

Get your Groq API key from: https://console.groq.com/

---

## 💻 Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

Open your browser to: `http://localhost:8501`

### Usage Tips

1. **Text Summarization**: 
   - Go to the "Text" tab
   - Paste or type your text
   - Click "Summarize Text"
   - View the summary instantly

2. **PDF Summarization**:
   - Go to the "PDF" tab
   - Upload your PDF file
   - Click "Summarize PDF"
   - View summary and extracted text

3. **Audio Summarization**:
   - Go to the "Audio" tab
   - Upload MP3, WAV, or OGG file
   - Click "Transcribe & Summarize"
   - View transcription and summary

4. **Adjust Settings**:
   - Use the sidebar to customize:
     - AI Model selection
     - Chunk size and overlap
     - Summary length
     - Temperature and sampling

---

## 🤖 Telegram Bot

Run the Telegram bot separately:

```bash
python telegram_bot.py
```

### Bot Commands
- `/start` - Get started with the bot
- Send text - Get it summarized
- Send voice message - Transcribe and summarize
- Send audio file - Process and summarize
- Send PDF - Extract and summarize

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t ai-summarizer .

# Run the container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  ai-summarizer
```

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:
- Streamlit app on port 8501
- Telegram bot (if token provided)

---

## 📦 Deployment to GitHub

### 1. Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: AI Summarizer with beautiful UI"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `ai-summarizer`
3. Don't initialize with README (we already have one)

### 3. Push to GitHub

```bash
git remote add origin https://github.com/yourusername/ai-summarizer.git
git branch -M main
git push -u origin main
```

### 4. Deploy with Streamlit Cloud (Free)

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Add environment variables:
   - `GROQ_API_KEY`: Your Groq API key
7. Click "Deploy"

### Alternative: Deploy to Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```
3. Deploy:
```bash
heroku create ai-summarizer
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

---

## 🔧 Configuration

### Available Models
- `facebook/bart-large-cnn` - Default, best for summaries
- `facebook/bart-large-xsum` - Extra abstract summaries
- `google/pegasus-xsum` - Alternative abstract model

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model_name` | Hugging Face model | `facebook/bart-large-cnn` |
| `max_chunk_tokens` | Maximum tokens per chunk | `900` |
| `chunk_overlap_tokens` | Overlap between chunks | `100` |
| `min_summary_tokens` | Minimum summary length | `64` |
| `max_summary_tokens` | Maximum summary length | `256` |
| `do_sample` | Enable sampling | `False` |
| `temperature` | Generation temperature | `1.0` |

---

## 🏗️ Project Structure

```
ai-summarizer/
├── app.py                 # Main Streamlit application
├── summarizer.py          # Summarization logic
├── telegram_bot.py        # Telegram bot handler
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🛠️ Technical Details

### Technologies Used
- **Streamlit**: Modern web interface
- **Transformers** (Hugging Face): AI models
- **PyPDF**: PDF text extraction
- **Groq API**: Fast audio transcription
- **Python-telegram-bot**: Telegram integration
- **Torch**: Deep learning backend

### How It Works

1. **Text Input**: Directly processed and chunked
2. **PDF Input**: Text extracted using PyPDF, then chunked
3. **Audio Input**: Transcribed via Groq API, then summarized
4. **Chunking**: Large texts split with overlap for context
5. **Summarization**: Each chunk summarized, then combined
6. **Display**: Beautiful UI shows results with timing

---

## 🔐 Security Notes

- ⚠️ **Never commit API keys** to GitHub
- ✅ Use `.env` file for local development
- ✅ Use environment variables in production
- ✅ Keep `.env` in `.gitignore`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License © 2024

---

## 👨‍💻 Author

**Soroush Eghdami**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Hugging Face for transformer models
- Groq for fast Whisper API
- Streamlit for the amazing framework
- The open-source community

---

## 📊 Stats

- ⚡ Fast summarization with transformer models
- 🎨 Beautiful modern UI
- 📱 Mobile responsive
- 🔄 Real-time configuration
- 🚀 Easy deployment

---

Made with ❤️ using AI and modern web technologies.
