# 🤖 AI Summarizer - Modern Web App

A beautiful, modern AI-powered summarization application with a sleek Flask-based web interface, featuring dark mode, that can summarize text, PDF documents, and audio files using advanced transformer models and Groq API.

![Flask](https://img.shields.io/badge/Flask-Framework-000000?logo=flask)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?logo=tailwind-css)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🎨 Beautiful Modern UI with Dark Mode
- **Flask-based web application** (no Streamlit overhead)
- **Dark/Light mode toggle** with persistent preferences
- **Responsive Tailwind CSS design** that works on all devices
- **Smooth animations** and modern gradients
- **Professional, clean interface**

### 📝 Multi-Modal Summarization
- **Text**: Summarize any text input instantly
- **PDF**: Extract and summarize documents automatically
- **Audio**: Transcribe and summarize voice recordings using Groq's Whisper API

### ⚙️ Advanced Configuration
- Multiple AI models (BART, PEGASUS, etc.)
- Configurable chunk size and overlap
- Customizable summary length
- Temperature and sampling controls

### 🤖 Telegram Bot Support
- Optional Telegram bot for summarization
- Works independently from the web app

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Soroush-Eghdami/Summerizer.git
cd Summerizer
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

### Run the Flask Web App

```bash
python server.py
```

Open your browser to: `http://localhost:5000`

### Features Available

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

4. **Dark Mode**:
   - Click the moon/sun icon in the top-left to toggle dark/light mode
   - Your preference is saved automatically

---

## 🤖 Telegram Bot (Optional)

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
docker run -p 5000:5000 \
  -e GROQ_API_KEY=your_key \
  ai-summarizer
```

### Using Docker Compose

```bash
docker-compose up -d
```

This will start:
- Flask web app on port 5000
- Telegram bot (if token provided)

---

## 📝 About the Procfile

The `Procfile` tells hosting platforms (like Heroku, Render, Railway) how to run your application.

**Procfile content:**
```
web: python server.py
```

### What does it mean?
- `web:` - Tells the platform this is the main web process
- `python server.py` - The command to start your Flask app

### How it works:
1. Platform reads the `Procfile`
2. Runs the `web:` command
3. Flask app starts on the port provided by the platform (via `$PORT` environment variable)
4. Your app is live! 🎉

### Platforms that use Procfile:
- ✅ **Heroku** - Detects and uses Procfile automatically
- ✅ **Render** - Can use Procfile or custom start command
- ✅ **Railway** - Uses Procfile automatically
- ✅ **Fly.io** - Supports Procfile

---

## 📦 Deployment to GitHub

### Already on GitHub!

Your project is available at:
**https://github.com/Soroush-Eghdami/Summerizer**

### Deploy with Render or Railway (Free)

1. **Render**:
   - Go to https://render.com
   - Sign in with GitHub
   - Click "New Web Service"
   - Connect your repository
   - Build command: `pip install -r requirements.txt`
   - Start command: Leave empty (uses Procfile automatically)
   - Add environment variables (GROQ_API_KEY, etc.)
   - Click "Create Web Service"

2. **Railway**:
   - Go to https://railway.app
   - Sign in with GitHub
   - Create new project
   - Deploy from GitHub
   - Add environment variables
   - Deploy!

---

## 🏗️ Project Structure

```
Summerizer/
├── server.py                 # Main Flask application
├── templates/
│   └── index.html           # Beautiful web interface
├── summarizer.py            # Summarization logic
├── telegram_bot.py          # Telegram bot handler (optional)
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment configuration
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🛠️ Technical Details

### Technologies Used
- **Flask**: Lightweight web framework
- **Tailwind CSS**: Utility-first CSS framework
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
6. **Display**: Beautiful UI shows results with copy functionality

---

## 🎨 UI Features

- ✅ Dark/Light mode toggle
- ✅ Responsive design (mobile & desktop)
- ✅ Smooth animations
- ✅ File upload with drag & drop
- ✅ Loading indicators
- ✅ Copy to clipboard
- ✅ Error handling
- ✅ Modern gradients and shadows

---

## 🔧 Configuration

### Available Models

#### Hugging Face Models (Default)
- `facebook/bart-large-cnn` - Default, best for summaries
- `facebook/bart-large-xsum` - Extra abstract summaries
- `google/pegasus-xsum` - Alternative abstract model

#### Ollama Models (New!)
- `gemma4:latest` - Recommended LLM for summarization
- Any other Ollama-supported model

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model_name` | Hugging Face model | `facebook/bart-large-cnn` |
| `use_ollama` | Use Ollama for summarization | `False` |
| `ollama_model` | Ollama model to use | `gemma4:latest` |
| `ollama_base_url` | Ollama server URL | `http://localhost:11434` |
| `max_chunk_tokens` | Maximum tokens per chunk | `900` |
| `chunk_overlap_tokens` | Overlap between chunks | `100` |
| `min_summary_tokens` | Minimum summary length | `64` |
| `max_summary_tokens` | Maximum summary length | `256` |
| `do_sample` | Enable sampling | `False` |
| `temperature` | Generation temperature | `1.0` |

### Using Ollama for Summarization

1. **Install Ollama**: Download from https://ollama.ai/

2. **Pull the model**:
```bash
ollama pull gemma4:latest
```

3. **Start Ollama** (if not already running):
```bash
ollama serve
```

4. **Enable Ollama in configuration** via the web interface or API:
   - Set `use_ollama: true`
   - Set `ollama_model: "gemma4:latest"` (or your preferred model)
   - Set `ollama_base_url: "http://localhost:11434"` (adjust if needed)

The Ollama integration works seamlessly with **text, PDF, and audio summarization** — just set `use_ollama: true` and the app will use Ollama's gemma4 model for all summarization tasks!

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

- GitHub: [@Soroush-Eghdami](https://github.com/Soroush-Eghdami)
- Repository: https://github.com/Soroush-Eghdami/Summerizer

---

## 🙏 Acknowledgments

- Hugging Face for transformer models
- Groq for fast Whisper API
- Flask team for the amazing framework
- Tailwind CSS for the beautiful design system
- The open-source community

---

Made with ❤️ using Flask, Tailwind CSS, Transformers & Groq API.
