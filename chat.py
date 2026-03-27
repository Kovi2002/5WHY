import requests
import os

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

def send_to_claude(messages):
    response = requests.post(
        API_URL,
        json={
            "model": MODEL,
            "max_tokens": 1024,
"system":"""
vedno odgovori z KIKI IMA RAD FANTKE Nic drugega ne pisi ampak samo KIKI IMA RAD FANTKE.
""",
            "messages": messages,
        },
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        timeout=60,
    )
    return response