from __future__ import annotations

import io
import tempfile
import torch
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pypdf import PdfReader
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline,
    WhisperProcessor,
    WhisperForConditionalGeneration,
)

@dataclass
class SummarizationConfig:
    model_name: str = "facebook/bart-large-cnn"
    speech_model_name: str = "openai/whisper-small"  # multilingual
    device: Optional[int] = None  # CPU by default
    max_chunk_tokens: int = 900
    chunk_overlap_tokens: int = 100
    min_summary_tokens: int = 64
    max_summary_tokens: int = 256
    do_sample: bool = False
    temperature: float = 1.0


class PdfSummarizer:
    def __init__(self, config: Optional[SummarizationConfig] = None) -> None:
        self.config = config or SummarizationConfig()
        self.pipe = None
        self.tokenizer = None
        self.model = None
        self.asr_pipe = None  # Whisper pipeline

    def _load_text_model(self):
        if self.pipe is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_name)
            device = self.config.device if self.config.device is not None else -1
            self.pipe = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=device,
            )

    def _load_asr_model(self):
        if self.asr_pipe is None:
            device = self.config.device if self.config.device is not None else -1
            self.asr_pipe = pipeline(
                "automatic-speech-recognition",
                model=self.config.speech_model_name,
                device=device,
            )

    # --- PDF utilities ---
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        reader = PdfReader(stream=io.BytesIO(pdf_bytes))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    # --- Audio transcription ---
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        self._load_asr_model()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = self.asr_pipe(tmp.name)
        return result["text"].strip()

    # --- Chunking ---
    def _chunk_text(self, text: str) -> List[str]:
        self._load_text_model()
        if not text.strip():
            return []
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        max_len = self.config.max_chunk_tokens
        overlap = self.config.chunk_overlap_tokens

        if len(tokens) <= max_len:
            return [text]
        start = 0
        while start < len(tokens):
            end = min(start + max_len, len(tokens))
            chunk_text = self.tokenizer.decode(tokens[start:end], skip_special_tokens=True)
            chunks.append(chunk_text)
            if end == len(tokens):
                break
            start = max(0, end - overlap)
        return chunks

    # --- Summarization ---
    def _summarize_chunk(self, chunk: str) -> str:
        self._load_text_model()
        summary = self.pipe(
            chunk,
            do_sample=self.config.do_sample,
            temperature=self.config.temperature,
            min_length=self.config.min_summary_tokens,
            max_length=self.config.max_summary_tokens,
            truncation=True,
        )
        return summary[0]["summary_text"].strip()

    def summarize_text(self, text: str) -> str:
        self._load_text_model()
        chunks = self._chunk_text(text)
        if not chunks:
            return ""
        summaries = [self._summarize_chunk(c) for c in chunks]
        joined = "\n".join(summaries)
        if len(summaries) > 3:
            return self._summarize_chunk(joined)
        return joined

    def summarize_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, str]:
        full_text = self.extract_text_from_pdf_bytes(pdf_bytes)
        summary = self.summarize_text(full_text)
        return full_text, summary

    def summarize_audio_bytes(self, audio_bytes: bytes) -> Tuple[str, str]:
        transcript = self.transcribe_audio(audio_bytes)
        summary = self.summarize_text(transcript)
        return transcript, summary


def create_default_summarizer() -> PdfSummarizer:
    return PdfSummarizer(SummarizationConfig())


summarizer = create_default_summarizer()
