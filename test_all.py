import unittest
import os
from model import story_to_audio, extract_text_from_pdf
from fastapi.testclient import TestClient
from api import app  # ✅ Use the actual filename (without .py)
from gradio_app import text_to_speech  # rename your Gradio script to gradio_app.py

class TestModel(unittest.TestCase):

    def test_story_to_audio_valid_text(self):
        text = "This is a test story."
        path = story_to_audio(text)
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_story_to_audio_empty_text(self):
        path = story_to_audio("")
        self.assertIsNone(path)

    def test_extract_text_from_valid_pdf(self):
        # Assumes you have a simple 1-page test.pdf in your project dir with known content
        with open("test.pdf", "wb") as f:
            f.write(b"%PDF-1.4\n%Fake PDF for test\n1 0 obj\n<<>>\nendobj\nxref\n0 2\n0000000000 65535 f \n0000000010 00000 n \ntrailer\n<<>>\nstartxref\n29\n%%EOF")
        result = extract_text_from_pdf("test.pdf")
        self.assertIsInstance(result, str)
        os.remove("test.pdf")

    def test_extract_text_from_invalid_pdf(self):
        result = extract_text_from_pdf("non_existent.pdf")
        self.assertEqual(result, "")

class TestAPI(unittest.TestCase):
    client = TestClient(app)

    def test_api_generate_success(self):
        response = self.client.post("/generate", json={"story": "Testing API TTS"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("audio_url", response.json())

    def test_api_generate_empty_text(self):
        response = self.client.post("/generate", json={"story": " "})
        self.assertEqual(response.status_code, 400)

    def test_upload_pdf_no_file(self):
        response = self.client.post("/upload-pdf/")
        self.assertEqual(response.status_code, 422)  # FastAPI default for missing required file

class TestGradioFunction(unittest.TestCase):

    def test_gradio_valid(self):
        audio_path = text_to_speech("Hello from Gradio test")
        self.assertIsNotNone(audio_path)
        self.assertTrue(os.path.exists(audio_path))
        os.remove(audio_path)

    def test_gradio_blank(self):
        result = text_to_speech("")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
