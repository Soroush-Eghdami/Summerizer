from __future__ import annotations

import io  # For working with pdf files (files in memory)
import tempfile # For creating temporary files
import torch # models like huggingface, pytorch, etc.
from dataclasses import dataclass # For defining setting easier in classes
from typing import List, Optional, Tuple # For using lists, optional, and tuples
from pypdf import PdfReader # For reading pdf files
from transformers import ( # Models for huggingface library (we use it for summarization)
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline,
    WhisperProcessor,
    WhisperForConditionalGeneration,
)
# For simple text we use BART
# For pdf we use a def to extract the text from it 
# For audio we use whisper

@dataclass # For defining setting easier in classes and not using __init__ method
class SummarizationConfig:
    model_name: str = "facebook/bart-large-cnn" # For simple text we use BART
    speech_model_name: str = "openai/whisper-small"  # multilingual # For audio we use whisper
    device: Optional[int] = None  # CPU by default (we can use GPU if we want)
    max_chunk_tokens: int = 900 # For chunking the text
    chunk_overlap_tokens: int = 100 # For chunking the text
    min_summary_tokens: int = 64 # For the minimum summary length
    max_summary_tokens: int = 256 # For the maximum summary length
    do_sample: bool = False # For sampling the text (randomness)
    temperature: float = 1.0 # For the temperature of the text (0.0 is the most deterministic, 1.0 is the most random)

# The main class of summerizer
class PdfSummarizer:
    def __init__(self, config: Optional[SummarizationConfig] = None) -> None:
        self.config = config or SummarizationConfig() # For using a custom configuration or the default one
        self.pipe = None # For the summarization model (BART)
        self.tokenizer = None # For the tokenizer of the model (BART)
        self.model = None # For the model (BART)
        self.asr_pipe = None  # Whisper pipeline # For the audio transcription model

    def _load_text_model(self): # For loading the text model
        if self.pipe is None: # Cheking if the pipline wasn't made before
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name) # Tokenizing the text
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_name) # Loading the model
            device = self.config.device if self.config.device is not None else -1 # For the device (CPU or GPU)
            self.pipe = pipeline( # For the summarization pipeline
                "summarization", # For the summarization task
                model=self.model, # For the model
                tokenizer=self.tokenizer, # For the tokenizer
                device=device, # For the device
            )

    def _load_asr_model(self): # For loading the audio transcription model
        if self.asr_pipe is None: # Cheking if the audio transcription pipeline wasn't made before
            device = self.config.device if self.config.device is not None else -1 # For the device (CPU or GPU)
            self.asr_pipe = pipeline( # For the audio transcription pipeline
                "automatic-speech-recognition", # For the audio transcription task
                model=self.config.speech_model_name, # For the model
                device=device, # For the device
            )

    # --- PDF utilities ---
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str: # For extracting the text from the pdf
        reader = PdfReader(stream=io.BytesIO(pdf_bytes)) # For reading the pdf
        text = "\n".join((page.extract_text() or "") for page in reader.pages) # For extracting the text from the pdf
        return "\n".join(line.strip() for line in text.splitlines() if line.strip()) # For returning the text

    # --- Audio transcription ---
    def transcribe_audio(self, audio_bytes: bytes) -> str: # For transcribing the audio
        self._load_asr_model()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp: # For creating a temporary file for the audio
            tmp.write(audio_bytes) # For writing the audio to the temporary file
            tmp.flush() # For flushing the temporary file
            result = self.asr_pipe(tmp.name) # For transcribing the audio
        return result["text"].strip()

    # --- Chunking ---
    def _chunk_text(self, text: str) -> List[str]: # Breacking the text into smaller chunks
        self._load_text_model()
        if not text.strip(): # Cheking if the text is empty
            return []
        tokens = self.tokenizer.encode(text, add_special_tokens=False) # For turning text into number
        chunks = [] # For the chunks
        max_len = self.config.max_chunk_tokens # For the maximum length of the chunks
        overlap = self.config.chunk_overlap_tokens # For the overlap of the chunks

        if len(tokens) <= max_len: # Cheking if the text is smaller than the maximum length
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
    def _summarize_chunk(self, chunk: str) -> str: # For summarizing a chunk of text
        self._load_text_model()
        summary = self.pipe( # For summarizing the chunk
            chunk,
            do_sample=self.config.do_sample, # Getting the parameters from config def
            temperature=self.config.temperature,
            min_length=self.config.min_summary_tokens,
            max_length=self.config.max_summary_tokens,
            truncation=True,
        )
        return summary[0]["summary_text"].strip() # returns a list of dictinaries # .strip() for removing spaces

    def summarize_text(self, text: str) -> str: # For summerizing all of text 
        self._load_text_model() 
        chunks = self._chunk_text(text)
        if not chunks:
            return ""
        summaries = [self._summarize_chunk(c) for c in chunks]
        joined = "\n".join(summaries)
        if len(summaries) > 3:
            return self._summarize_chunk(joined)
        return joined
    # in total it chunks the text and summerizes them and then joins them back
    # if the number of chunks is greater than 3, it summerizes the joined text again

    def summarize_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, str]: # gets a pdf and turns it into text and then summerizes it
        full_text = self.extract_text_from_pdf_bytes(pdf_bytes)
        summary = self.summarize_text(full_text)
        return full_text, summary

    def summarize_audio_bytes(self, audio_bytes: bytes) -> Tuple[str, str]: # gets an audio and turns it into text and then summerizes it
        transcript = self.transcribe_audio(audio_bytes)
        summary = self.summarize_text(transcript)
        return transcript, summary


def create_default_summarizer() -> PdfSummarizer: # Creating a default summerizer with default config
    return PdfSummarizer(SummarizationConfig())


summarizer = create_default_summarizer() # Creating a global summarizer instance for using in other files
