import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")

def call_llm(prompt, role):
    system_prompt = (
        "You are a smart academic advisor for a school. "
        "Analyze student performance, attendance, and marks. "
        "Give personalized, positive, and practical improvement suggestions."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nUser ({role}): {prompt}",
        "stream": False  # 🚨 THIS FIXES THE HANG
    }

    try:
        res = requests.post(
            OLLAMA_URL,
            json=payload,
            

        )

        res.raise_for_status()

        data = res.json()
        return data.get("response", "No response from AI")

    
    except Exception as e:
        print("OLLAMA ERROR:", str(e))
        return "⚠️ AI service is currently unavailable."
