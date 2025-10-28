from flask import Flask, render_template, request, jsonify, send_from_directory # For creating web server and api
from flask_cors import CORS # For enabeling access from other domains (front-end)
import os # For working with os
import tempfile # For creating temporary files
import requests # For making requests to the api
from dotenv import load_dotenv # For reading data from .env files
from summarizer import PdfSummarizer, SummarizationConfig # For using the summarizer

# Load environment variables (.env files)
load_dotenv()

app = Flask(__name__) # Creating a flask app
CORS(app) #accepting Requesting from different domains 

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") # Loading groq api key form .env 

# Initialize summarizer
config = SummarizationConfig() # laoding the default config
summarizer = PdfSummarizer(config) # creating a summarizer instance

# Store current config
current_config = config # storing the current config

def update_summarizer_config(new_config): # updating the summarizer with new configuration
    """Update the summarizer with new configuration"""
    global current_config, summarizer # updating the global variables
    current_config = SummarizationConfig(**new_config) # updating the current config with new configuration
    summarizer = PdfSummarizer(current_config) # updating the summarizer with new configuration

# Groq API transcription 
def transcribe_with_groq(audio_path: str, model: str = "whisper-large-v3-turbo") -> str: 
    if not GROQ_API_KEY: # Checking if the groq api key exists
        return "Error: GROQ_API_KEY not configured"
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"} # sending the authorization header
    with open(audio_path, "rb") as f:
        files = {
            "file": (os.path.basename(audio_path), f, "application/octet-stream"),
            "model": (None, model),
        }
        resp = requests.post(url, headers=headers, files=files, timeout=120)
    if resp.status_code != 200:
        return f"Error: {resp.status_code} - {resp.text}"
    return resp.json().get("text", "")
# in summery it send the audio in multipart/form-data format to the groq api
# returns the answer if it was error or the text 

@app.route('/') # For rendering the index.html file in the templates folder
def index():
    return render_template('index.html')

@app.route('/api/summarize/text', methods=['POST']) # gets a POST request using JSON with "text" key and the text value
def summarize_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text.strip(): # Checking if the text is empty
            return jsonify({'error': 'No text provided'}), 400
        
        summary = summarizer.summarize_text(text) # Else it summerizes the text
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 # if there is an error it returns the error

@app.route('/api/summarize/pdf', methods=['POST']) # gets a POST request using JSON with "file" key and the file value
def summarize_pdf(): # summerizes the pdf
    try:
        if 'file' not in request.files: # Checking if the file exists
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file'] # Getting the file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400 # Checking if the file is selected
        
        pdf_bytes = file.read()
        full_text, summary = summarizer.summarize_pdf_bytes(pdf_bytes) # Else it summerizes the pdf and returns the full text and the summary
        
        return jsonify({
            'summary': summary,
            'extracted_text': full_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 # if there is an error it returns the error

@app.route('/api/summarize/audio', methods=['POST']) # gets a POST request using JSON with "file" key and the file value
def summarize_audio(): # summerizes the audio
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400 # Checking if the file exists
        
        file = request.files['file'] # Getting the file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400 # Checking if the file is selected
        
        if not GROQ_API_KEY:
            return jsonify({'error': 'GROQ_API_KEY not configured'}), 500 # Checking if the groq api key exists
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            file.save(tmp.name) # Saving the file to a temporary file
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
                return jsonify({'error': transcribed_text or 'Failed to transcribe audio'}), 500 # if there is an error it returns the error
        finally:
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except: # if there is an error it returns the error
                pass
    except Exception as e:
        return jsonify({'error': str(e)}), 500 # if there is an error it returns the error

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    if request.method == 'GET': # Sends current settings (configs)
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
            update_summarizer_config(data) # Updating the summarizer with new configuration
            return jsonify({'message': 'Configuration updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500 # if there is an error it returns the error

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    # When the app runs directly and not imported 
    # Runs the flask on a specific port 
    # after that gives all avalabe ip addresses to the app
    # debug mode is on to see the errors in the browser
