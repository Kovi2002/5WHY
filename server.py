"""
AI Klepetalnik — Flask strežnik za Railway deployment
API ključ ostane skrit na strežniku.
"""



from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder="static")

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"


@app.route("/")
def index():
    return send_from_directory("static", "index.html") # Strežnik pošlje index.html iz static mape


@app.route("/chat", methods=["POST"]) # Endpoint za klepet, ki sprejme sporočila in vrne odgovor od API-ja
def chat():
    if not API_KEY:
        return jsonify({"error": "API ključ ni nastavljen na strežniku."}), 500 # Preveri, če je API ključ nastavljen

    data = request.get_json()   # Prebere JSON podatke iz POST zahteve
    messages = data.get("messages", []) # Pridobi sporočila iz podatkov, privzeto prazna lista, če ni sporočil

    if not messages: # Preveri, če so sporočila prazna, in vrne napako, če ni sporočil
        return jsonify({"error": "Ni sporočil."}), 400 # Napaka 400 - Bad Request, ker ni sporočil za obdelavo

    try:
        response = requests.post(
            API_URL,
            json={
                "model": MODEL,
                "max_tokens": 1024,
                "system": "Si prijazen in pameten asistent, ki odgovarja v slovenščini, razen če te uporabnik prosi drugače. Odgovori so jasni in jedrnati.",
                "messages": messages,
            },
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
            },
            timeout=30,
        )

        if response.status_code != 200:
            return jsonify({"error": f"API napaka: {response.text}"}), response.status_code

        reply = response.json()["content"][0]["text"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
