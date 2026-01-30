import threading
import time
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

def warm_model():
    while True:
        try:
            requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": "ping",
                    "stream": False
                },
                timeout=10
            )
        except:
            pass
        time.sleep(60)

def start_warmup():
    t = threading.Thread(target=warm_model, daemon=True)
    t.start()
