import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        res = requests.post(API_URL, headers=headers, json=body)
        res.raise_for_status()
        content = res.json()
        return content["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Gemini API Error:", e)
        return "❌ AI is sleeping right now. Try again later."
