# PDF Summarizer

PDF Summarizer is a Python-based application that extracts, summarizes, and delivers the main content of PDF documents. It offers both a web API and a Telegram bot interface for easy, automated access and summary delivery.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- Summarize PDF documents using NLP techniques.
- Web API for programmatic access (`app.py`).
- Telegram bot for chat-based summaries (`telegram_bot.py`).
- Docker and Docker Compose support for easy deployment.
- Configurable requirements via `requirements.txt`.

## Project Structure

| File/Folder         | Description                                      |
|---------------------|--------------------------------------------------|
| `app.py`            | FastAPI server providing PDF summarization API   |
| `summarizer.py`     | Core logic for extracting and summarizing PDFs   |
| `telegram_bot.py`   | Telegram bot interface for PDF summarization     |
| `requirements.txt`  | Python dependencies                              |
| `Dockerfile`        | Docker configuration for containerized runs      |
| `docker-compose.yml`| Compose file for multi-container setup           |
| `.dockerignore`     | Files ignored during Docker builds               |
| `__init__.py`       | Package initialization (empty)                   |
| `__pycache__/`      | Python bytecode cache (auto-generated)           |

## Installation

Clone the repository:
```sh
git clone https://github.com/Soroush-Eghdami/PDF-summarizer.git
cd PDF-summarizer
```

Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

### API Server

Start the FastAPI server:
```sh
python app.py
```
Visit [http://localhost:8000](http://localhost:8000) for documentation and endpoints.

### Telegram Bot

Run the bot:
```sh
python telegram_bot.py
```
Follow instructions in the bot to get PDF summaries via Telegram.

## Docker Deployment

Build and run using Docker Compose:
```sh
docker-compose up --build
```

You can also build the image manually:
```sh
docker build -t pdf-summarizer .
docker run -p 8000:8000 pdf-summarizer
```

## Contributing

Contributions are welcome! Please fork the repo, make changes, and open a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

**For more details, check the source files:**
- [app.py](https://github.com/Soroush-Eghdami/PDF-summarizer/blob/main/app.py)
- [summarizer.py](https://github.com/Soroush-Eghdami/PDF-summarizer/blob/main/summarizer.py)
- [telegram_bot.py](https://github.com/Soroush-Eghdami/PDF-summarizer/blob/main/telegram_bot.py)
