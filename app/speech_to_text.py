import requests
import os
from dotenv import load_dotenv

load_dotenv()

LEMONFOX_API_KEY = os.getenv("LEMONFOX_API_KEY")
API_URL = "https://api.lemonfox.ai/v1/audio/transcriptions"

def transcribe_audio(filepath):
    with open(filepath, "rb") as audio_file:
        files = {
            "file": audio_file
        }

        data = {
            "language": "english",
            "response_format": "json"
        }

        headers = {
            "Authorization": f"Bearer {LEMONFOX_API_KEY}"
        }

        response = requests.post(API_URL, headers=headers, files=files, data=data)

        if response.status_code != 200:
            print("Error:", response.text)
            return "Transcription failed"

        return response.json()["text"]
