from __future__ import annotations

import io
import warnings
import torch
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pypdf import PdfReader
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


@dataclass
class SummarizationConfig:
    """Configuration for the PDF summarizer."""
    model_name: str = "csebuetnlp/mT5_multilingual_XLSum"  # Multilingual, supports Persian & general text
    device: Optional[int] = None  # Set 0 for GPU, None for auto-detect
    max_chunk_tokens: int = 512  # Optimized for mT5 context
    chunk_overlap_tokens: int = 50
    min_summary_tokens: int = 50
    max_summary_tokens: int = 150  # Shorter for focused summaries
    do_sample: bool = True
    temperature: float = 0.5  # Lower for factual accuracy


class PdfSummarizer:
    """A multilingual PDF summarizer using mT5 model with chunking for long documents."""

    def __init__(self, config: Optional[SummarizationConfig] = None) -> None:
        self.config = config or SummarizationConfig()

        # Validate config
        if self.config.max_chunk_tokens <= self.config.chunk_overlap_tokens:
            raise ValueError("max_chunk_tokens must be greater than chunk_overlap_tokens")
        if self.config.min_summary_tokens >= self.config.max_summary_tokens:
            raise ValueError("min_summary_tokens must be less than max_summary_tokens")
        if self.config.temperature < 0 or self.config.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")

        # Auto-detect device if None
        device = self.config.device
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
            print(f"Auto-detected device: {'GPU' if device == 0 else 'CPU'}")

        print(f"Loading model: {self.config.model_name} on device {device}")

        # Suppress tokenizer warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name, legacy=False)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model/tokenizer: {e}")

        self.pipe = pipeline(
            task="summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=device,
        )

    # --- PDF utilities ---
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extracts clean text from PDF bytes."""
        try:
            reader = PdfReader(stream=io.BytesIO(pdf_bytes))
            if not reader.pages:
                return ""
            pages_text: List[str] = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
            text = "\n\n".join(pages_text)
            return "\n".join(line.strip() for line in text.splitlines() if line.strip())
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

    # --- Chunking ---
    def _chunk_text(self, text: str) -> List[str]:
        """Chunks text into overlapping token-based segments."""
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        max_len = self.config.max_chunk_tokens
        overlap = self.config.chunk_overlap_tokens
        chunks: List[str] = []

        if len(tokens) <= max_len:
            return [text.strip()]

        start = 0
        while start < len(tokens):
            end = min(start + max_len, len(tokens))
            chunk_ids = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_ids, skip_special_tokens=True).strip()
            if chunk_text:  # Skip empty chunks
                chunks.append(chunk_text)
            if end == len(tokens):
                break
            start = max(0, end - overlap)
        return chunks

    # --- Summarization ---
    def _summarize_chunk(self, chunk: str, is_hierarchical: bool = False) -> str:
        """Summarizes a single chunk with enhanced prompting to minimize hallucinations."""
        if not chunk.strip():
            return ""

        # Enhanced language-aware prefix for fidelity and structure
        if self._is_persian(chunk):
            base_prefix = (
                "خلاصه‌ای دقیق، مختصر و کاملاً بر اساس متن زیر بنویس. "
                "هیچ اطلاعات جدیدی اضافه نکن و فقط به محتوای داده‌شده وفادار بمان. "
                "اگر ممکن، روی علل، اثرات و راه‌حل‌ها تمرکز کن: "
            )
            hierarchical_prefix = (
                "خلاصه کلی دقیق و یکپارچه از خلاصه‌های زیر بنویس. "
                "بدون تغییر معنا یا اضافه کردن اطلاعات، فقط بر اساس محتوای موجود: "
            )
        else:
            base_prefix = (
                "Write a precise, concise summary strictly based on the following text. "
                "Do not add any new information or external knowledge; stick only to the provided content. "
                "If applicable, focus on causes, effects, and solutions: "
            )
            hierarchical_prefix = (
                "Write an overall precise and integrated summary of the following summaries. "
                "Do not alter meanings or add new information; base it solely on the given content: "
            )

        prefix = hierarchical_prefix if is_hierarchical else base_prefix
        input_text = prefix + chunk.strip()

        try:
            summary_list = self.pipe(
                input_text,
                do_sample=self.config.do_sample,
                temperature=self.config.temperature,
                min_length=self.config.min_summary_tokens,
                max_length=self.config.max_summary_tokens,
                truncation=True,
            )
            return summary_list[0]["summary_text"].strip() if summary_list else ""
        except Exception as e:
            print(f"Warning: Failed to summarize chunk: {e}")
            return ""

    # --- Language detection (simple Persian detection) ---
    def _is_persian(self, text: str) -> bool:
        """Simple check for Persian script using Unicode range."""
        return any("\u0600" <= ch <= "\u06FF" for ch in text)

    # --- Public methods ---
    def summarize_text(self, text: str) -> str:
        """Summarizes input text, using hierarchical approach for long texts."""
        if not text.strip():
            return ""

        chunks = self._chunk_text(text)
        if not chunks:
            return ""

        first_pass = [self._summarize_chunk(c) for c in chunks]
        first_pass = [s for s in first_pass if s.strip()]  # Filter empty summaries
        if not first_pass:
            return ""

        if len(first_pass) > 4:  # Higher threshold for better coverage
            joined = "\n\n".join(first_pass)
            hierarchical_summary = self._summarize_chunk(joined, is_hierarchical=True)
            if hierarchical_summary.strip():
                return hierarchical_summary
        return "\n\n".join(first_pass)

    def summarize_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, str]:
        """Summarizes PDF bytes, returning (full_text, summary)."""
        full_text = self.extract_text_from_pdf_bytes(pdf_bytes)
        summary = self.summarize_text(full_text)
        return full_text, summary


# --- Create default instance ---
def create_default_summarizer() -> PdfSummarizer:
    """Creates a default PdfSummarizer instance."""
    return PdfSummarizer(SummarizationConfig())


# --- Helper for Telegram Bot (or other apps) ---
def summarize_pdf(file_path: str) -> str:
    """
    Reads a PDF from disk and returns a summary string.
    Note: Relies on global 'summarizer' instance for efficiency.
    For production, consider passing an instance explicitly.
    """
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        _, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
        return summary
    except FileNotFoundError:
        raise ValueError(f"PDF file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to summarize PDF: {e}")


# Global summarizer instance for reuse (initialize after class definition)
summarizer = create_default_summarizer()