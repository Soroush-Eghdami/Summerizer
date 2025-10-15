from __future__ import annotations

import io
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pypdf import PdfReader
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


@dataclass
class SummarizationConfig:
    model_name: str = "facebook/bart-large-cnn"
    device: Optional[int] = None  # CPU by default; set 0 for CUDA if available
    max_chunk_tokens: int = 900
    chunk_overlap_tokens: int = 100
    min_summary_tokens: int = 64
    max_summary_tokens: int = 256
    do_sample: bool = False
    temperature: float = 1.0


class PdfSummarizer:
    def __init__(self, config: Optional[SummarizationConfig] = None) -> None:
        self.config = config or SummarizationConfig()

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_name)

        self.pipe = pipeline(
            task="summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.config.device if self.config.device is not None else -1,
        )

    # --- PDF utilities ---
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        reader = PdfReader(stream=io.BytesIO(pdf_bytes))
        pages_text: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
        text = "\n\n".join(pages_text)
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    # --- Chunking ---
    def _chunk_text(self, text: str) -> List[str]:
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        max_len = self.config.max_chunk_tokens
        overlap = self.config.chunk_overlap_tokens
        chunks: List[str] = []

        if len(tokens) <= max_len:
            return [text]

        start = 0
        while start < len(tokens):
            end = min(start + max_len, len(tokens))
            chunk_ids = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_ids, skip_special_tokens=True)
            chunks.append(chunk_text)
            if end == len(tokens):
                break
            start = max(0, end - overlap)
        return chunks

    # --- Summarization ---
    def _summarize_chunk(self, chunk: str) -> str:
        summary_list = self.pipe(
            chunk,
            do_sample=self.config.do_sample,
            temperature=self.config.temperature,
            min_length=self.config.min_summary_tokens,
            max_length=self.config.max_summary_tokens,
            truncation=True,
        )
        return summary_list[0]["summary_text"].strip()

    def summarize_text(self, text: str) -> str:
        chunks = self._chunk_text(text)
        if not chunks:
            return ""

        first_pass = [self._summarize_chunk(c) for c in chunks]
        joined = "\n".join(first_pass)
        if len(first_pass) > 3:
            return self._summarize_chunk(joined)
        return joined

    def summarize_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, str]:
        full_text = self.extract_text_from_pdf_bytes(pdf_bytes)
        summary = self.summarize_text(full_text)
        return full_text, summary


# --- Create default instance ---
def create_default_summarizer() -> PdfSummarizer:
    return PdfSummarizer(SummarizationConfig())


# --- Helper for Telegram Bot ---
def summarize_pdf(file_path: str) -> str:
    """
    Reads a PDF from disk and returns a summary string.
    """
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    _, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
    return summary


# Global summarizer instance for re-use
summarizer = create_default_summarizer()
