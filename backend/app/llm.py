import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

def call_llm(message: str, role: str):
    prompt = f"""
You are a school assistant chatbot.
User role: {role}
Respond in the correct tone.

User message: {message}
"""

    payload = {
        "model": OLLAMA_MODEL, 
        "prompt": prompt,      
        "stream": False  # Get full response at once (not streamed)
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]
