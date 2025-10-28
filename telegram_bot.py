import os
import tempfile
# The files above is for saving the files in the temporary folder
import requests
from dotenv import load_dotenv # Loding bot token from .env files
from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from summarizer import summarizer  # Use the global summarizer instance

# --- Load environment variables --- 
load_dotenv() # For loading the .env file and getting the bot token and groq api key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


# --- Audio transcription using Groq API ---
def transcribe_with_groq(audio_path: str, model: str = "whisper-large-v3-turbo") -> str: # transcribing the audio like it was in server.py
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # async commant for starting the bot
    await update.message.reply_text(
        "👋 Hi! I can summarize different types of inputs:\n\n"
        "• 📝 Send me text — I'll summarize it\n"
        "• 🎤 Send a voice message or MP3/WAV/OGG file — I'll transcribe and summarize it\n"
        "• 📄 Send a PDF — I'll summarize its contents"
    )


# --- Handle text messages ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # Extracting text from the massage 
    text = update.message.text or "" # Checking empty text
    if not text.strip():
        await update.message.reply_text("⚠️ Please send non-empty text.")
        return # Summerizing text
    summary = summarizer.summarize_text(text) # returning the summery
    await update.message.reply_text(summary or "(Empty summary)")


# --- Handle voice messages (Telegram-native voice notes) ---
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ GROQ_API_KEY not configured.")
        return
# for checking the api key 
    voice = update.message.voice # Checking if there is a voice message
    if not voice:
        await update.message.reply_text("⚠️ No voice message found.")
        return

    file = await context.bot.get_file(voice.file_id) # Downloding the audio file
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name
        await file.download_to_drive(tmp_path)

    try:
        text = transcribe_with_groq(tmp_path) # transcribing and summerizing 
        if not text or text.startswith("Error"):
            await update.message.reply_text("❌ Sorry, I couldn’t transcribe that voice message.")
            return
        summary = summarizer.summarize_text(text)
        await update.message.reply_text(summary or text)
    finally:
        try: # removing the temp file and folders
            os.remove(tmp_path)
        except OSError:
            pass


# --- Handle audio files (MP3, WAV, OGG uploads) ---
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # Checking the api key
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ GROQ_API_KEY not configured.")
        return

    audio = update.message.audio or update.message.voice # checkin audio files
    if not audio:
        await update.message.reply_text("⚠️ Please send a valid audio file (MP3, WAV, or OGG).")
        return

    file = await context.bot.get_file(audio.file_id) # Downloading the files with the right file extentions
    ext = os.path.splitext(audio.file_name or "audio.mp3")[1] if audio.file_name else ".mp3"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp_path = tmp.name
        await file.download_to_drive(tmp_path)

    try: # Sending proccessing message to the user in bot 
        await update.message.reply_text("⏳ Transcribing and summarizing your audio...") # transcribing and summerizing 
        text = transcribe_with_groq(tmp_path)
        if not text or text.startswith("Error"):
            await update.message.reply_text("❌ Sorry, I couldn’t transcribe that audio.")
            return
        summary = summarizer.summarize_text(text)
        await update.message.reply_text(summary or text)
    finally: # Deleting the temp files and folders
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# --- Handle PDF files ---
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # Checking the pdf file 
    document = update.message.document
    if not document or not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ Please send a valid PDF file.")
        return

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp: # Downloading the pdf file 
        tmp_path = tmp.name
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(tmp_path)

    try: # summerizing
        await update.message.reply_text("⏳ Summarizing your PDF, please wait...")
        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()
        _, summary = summarizer.summarize_pdf_bytes(pdf_bytes) # Handelling the errors
        await update.message.reply_text(summary or "(Empty summary)")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error processing PDF: {e}")
    finally:
        try: # remofing the temp files 
            os.remove(tmp_path)
        except OSError:
            pass


# --- Main entry point ---
def main() -> None: # main def and deploy
    if not TELEGRAM_BOT_TOKEN: # Cheking the existence of bot token 
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN is not set in environment variables.")
# Creating a telegram app
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
# Creating different handlers for different situation 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_pdf))
# the starting message
    print("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES) # Start polling and getting files 

# Starting the main def in case of starting directly 
if __name__ == "__main__":
    main()
