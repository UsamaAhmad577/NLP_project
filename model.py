import pyttsx3
import os
import uuid
from datetime import datetime
import pdfplumber

# 📁 Ensure outputs directory exists
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📦 Generate a unique filename using timestamp + short UUID
def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:6]
    return f"audio_{timestamp}_{short_id}.mp3"

# 🔊 Convert story text to audio file and save to outputs/
def story_to_audio(text: str) -> str:
    if not text.strip():  # Prevent generating audio for empty text
        return None

    filename = generate_filename()
    output_path = os.path.join(OUTPUT_DIR, filename)

    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    except Exception as e:
        print("❌ pyttsx3 failed:", e)
        return None

    if os.path.exists(output_path):
        return output_path
    return None

# 📄 Extract text from PDF file
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print("❌ PDF extraction error:", e)
        return ""
