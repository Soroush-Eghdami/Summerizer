import os
import tempfile
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from summarizer import summarizer  # Use the global summarizer instance

# --- Load environment variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


# --- Audio transcription using Groq API ---
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


# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hi! I can summarize different types of inputs:\n\n"
        "• 📝 Send me text — I'll summarize it\n"
        "• 🎤 Send a voice message or MP3/WAV/OGG file — I'll transcribe and summarize it\n"
        "• 📄 Send a PDF — I'll summarize its contents"
    )


# --- Handle text messages ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text.strip():
        await update.message.reply_text("⚠️ Please send non-empty text.")
        return
    summary = summarizer.summarize_text(text)
    await update.message.reply_text(summary or "(Empty summary)")


# --- Handle voice messages (Telegram-native voice notes) ---
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ GROQ_API_KEY not configured.")
        return

    voice = update.message.voice
    if not voice:
        await update.message.reply_text("⚠️ No voice message found.")
        return

    file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
        await file.download_to_drive(tmp_path)

    try:
        text = transcribe_with_groq(tmp_path)
        if not text or text.startswith("Error"):
            await update.message.reply_text("❌ Sorry, I couldn’t transcribe that voice message.")
            return
        summary = summarizer.summarize_text(text)
        await update.message.reply_text(summary or text)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# --- Handle audio files (MP3, WAV, OGG uploads) ---
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ GROQ_API_KEY not configured.")
        return

    audio = update.message.audio or update.message.voice
    if not audio:
        await update.message.reply_text("⚠️ Please send a valid audio file (MP3, WAV, or OGG).")
        return

    file = await context.bot.get_file(audio.file_id)
    ext = os.path.splitext(audio.file_name or "audio.mp3")[1] if audio.file_name else ".mp3"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp_path = tmp.name
        await file.download_to_drive(tmp_path)

    try:
        await update.message.reply_text("⏳ Transcribing and summarizing your audio...")
        text = transcribe_with_groq(tmp_path)
        if not text or text.startswith("Error"):
            await update.message.reply_text("❌ Sorry, I couldn’t transcribe that audio.")
            return
        summary = summarizer.summarize_text(text)
        await update.message.reply_text(summary or text)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# --- Handle PDF files ---
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    if not document or not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ Please send a valid PDF file.")
        return

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(tmp_path)

    try:
        await update.message.reply_text("⏳ Summarizing your PDF, please wait...")
        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()
        _, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
        await update.message.reply_text(summary or "(Empty summary)")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error processing PDF: {e}")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# --- Main entry point ---
def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN is not set in environment variables.")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_pdf))

    print("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
