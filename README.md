# 📝 PDF Summarizer

A complete PDF summarization project with **Python**, **Streamlit**, and **Telegram Bot** support.  
This project allows you to summarize PDF documents into concise English summaries using **Hugging Face transformers** and optionally interact with the model through a Telegram bot.

---

## Features

- Summarize **PDFs** using `facebook/bart-large-cnn` or custom transformer models.
- Web interface via **Streamlit** (`app.py`).
- Telegram bot for **text, voice, and PDF summarization**.
- Dockerized for easy deployment.
- Configurable model parameters: chunk size, summary length, sampling, and temperature.
- Efficient chunking for long PDFs with overlapping token windows.

---

## Project Structure

```
Summerizer/
├── app.py # Streamlit web app
├── telegram_bot.py # Telegram bot handler
├── summarizer.py # PDF summarization logic
├── Dockerfile # Docker container definition
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt # Python dependencies
└── README.md # Project documentation
```
---

## Installation (Local)

1. **Clone the repository**

```bash
git clone https://github.com/YourUsername/PDF-summarizer.git
cd PDF-summarizer
```

2. **Create a virtual environment**

```bash
python -m venv botenv
source botenv/bin/activate   # Linux/macOS
botenv\Scripts\activate      # Windows
```
3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Set environment variables (for Telegram bot)**

Create a .env file:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

Load environment variables in Python using python-dotenv (optional).

---

## Usage
1. **Run Streamlit App**

```bash
streamlit run app.py
```
Open http://localhost:8501
 in your browser.

You can:

- Upload a PDF file.

- Configure model parameters in the sidebar.

- View extracted text and generated summary.

---

2. **Run Telegram Bot**

```bash
python telegram_bot.py
```
Your bot will:

- Summarize text messages.

- Transcribe and summarize voice messages (requires GROQ API key).

- Summarize uploaded PDF files.

---

## Docker Deployment
1. **Build and run with Docker**

```bash
docker build -t pdf-summarizer .
docker run -p 8501:8501 pdf-summarizer
```
2. **Use Docker Compose**

```bash
docker-compose up -d
```
This will start:

- pdf-summarizer service on port 8501 (Streamlit app)

- telegram-bot service running telegram_bot.py

---

## Usage Notes

- Chunking: Large PDFs are split into chunks to fit the model context window.

- Model: Default is facebook/bart-large-cnn, but you can replace with any Hugging Face summarization model.

- Telegram Bot: Ensure environment variables TELEGRAM_BOT_TOKEN and GROQ_API_KEY are set.

- Secrets: Do not commit API keys. Use environment variables or .env files.

---

## Customization

You can configure the summarizer via SummarizationConfig:

| Parameter              | Description                                | Default                   |
| ---------------------- | ------------------------------------------ | ------------------------- |
| `model_name`           | Hugging Face model for summarization       | `csebuetnlp/mT5_multilingual_XLSum` |
| `device`               | CPU by default, set GPU index if available | `None`                    |
| `max_chunk_tokens`     | Maximum tokens per chunk                   | `900`                     |
| `chunk_overlap_tokens` | Overlap between chunks                     | `100`                     |
| `min_summary_tokens`   | Minimum tokens in summary                  | `64`                      |
| `max_summary_tokens`   | Maximum tokens in summary                  | `256`                     |
| `do_sample`            | Enable sampling for diversity              | `False`                   |
| `temperature`          | Sampling temperature                       | `1.0`                     |


---

## Example

```python

from summarizer import create_default_summarizer

summarizer = create_default_summarizer()

with open("example.pdf", "rb") as f:
    pdf_bytes = f.read()

full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
print("Summary:\n", summary)
```

---

## Requirements

- Python >= 3.11

- transformers, pypdf, streamlit, torch, numpy, sentencepiece

- python-telegram-bot, requests (for Telegram integration)

---

## Docker Notes

- Streamlit app runs on port 8501.

- Model files are cached in ~/.cache/huggingface to avoid repeated downloads.

- Docker Compose allows running both Streamlit app and Telegram bot in separate services.

---

## Security

- Never commit secrets (API keys, bot tokens) to GitHub.

- Use .env files and environment variables.

- GitHub push protection will block secrets automatically.

---

## License

MIT License © Soroush Eghdami
---
