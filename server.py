from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import requests
from dotenv import load_dotenv
from summarizer import PdfSummarizer, SummarizationConfig

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize summarizer
config = SummarizationConfig()
summarizer = PdfSummarizer(config)

# Store current config
current_config = config

def update_summarizer_config(new_config):
    """Update the summarizer with new configuration"""
    global current_config, summarizer
    current_config = SummarizationConfig(**new_config)
    summarizer = PdfSummarizer(current_config)

# Groq API transcription
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summarize/text', methods=['POST'])
def summarize_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        summary = summarizer.summarize_text(text)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize/pdf', methods=['POST'])
def summarize_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_bytes = file.read()
        full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes)
        
        return jsonify({
            'summary': summary,
            'extracted_text': full_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize/audio', methods=['POST'])
def summarize_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not configured'}), 500
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # Transcribe
            transcribed_text = transcribe_with_groq(tmp_path)
            
            if transcribed_text and not transcribed_text.startswith("Error"):
                # Summarize
                summary = summarizer.summarize_text(transcribed_text)
                return jsonify({
                    'summary': summary,
                    'transcribed_text': transcribed_text
                })
            else:
                return jsonify({'error': transcribed_text or 'Failed to transcribe audio'}), 500
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except:
                pass
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET':
        return jsonify({
            'model_name': current_config.model_name,
            'max_chunk_tokens': current_config.max_chunk_tokens,
            'chunk_overlap_tokens': current_config.chunk_overlap_tokens,
            'min_summary_tokens': current_config.min_summary_tokens,
            'max_summary_tokens': current_config.max_summary_tokens,
            'do_sample': current_config.do_sample,
            'temperature': current_config.temperature
        })
    else:
        # POST - update config
        try:
            data = request.json
            update_summarizer_config(data)
            return jsonify({'message': 'Configuration updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
