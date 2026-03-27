import os
from flask import Flask, request, jsonify, send_from_directory, make_response
from chat import send_to_claude
from pdf_handler import encode_pdf, build_message_with_pdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from io import BytesIO
import json
from history import save_message

app = Flask(__name__, static_folder="static")

from history import save_message, init_db

app = Flask(__name__, static_folder="static")
init_db()  # ustvari tabelo ob zagonu

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if request.content_type and "multipart/form-data" in request.content_type:
        messages = json.loads(request.form.get("messages", "[]"))
        pdf_file = request.files.get("pdf")
    else:
        data = request.get_json()
        messages = data.get("messages", [])
        pdf_file = None

    if not messages:
        return jsonify({"error": "Ni sporočil."}), 400

    if pdf_file:
        pdf_b64 = encode_pdf(pdf_file)
        messages[-1] = build_message_with_pdf(messages[-1], pdf_b64)

    response = send_to_claude(messages)

    if response.status_code != 200:
        return jsonify({"error": f"API napaka: {response.text}"}), response.status_code




    reply = response.json()["content"][0]["text"]

    session_id = request.headers.get("X-Session-ID", "unknown")
    save_message(session_id, "user", messages[-1]["content"] if isinstance(messages[-1]["content"], str) else "PDF sporočilo")
    save_message(session_id, "assistant", reply)

    return jsonify({"reply": reply})

@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()
    messages = data.get("messages", [])

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, spaceAfter=20)
    user_style = ParagraphStyle('User', parent=styles['Normal'], fontSize=10,
                                spaceAfter=6, fontName='Helvetica-Bold')
    ai_style = ParagraphStyle('AI', parent=styles['Normal'], fontSize=10, spaceAfter=12)

    story = []
    story.append(Paragraph("5WHY Analiza — Poročilo", title_style))
    story.append(Spacer(1, 0.5*cm))

    for msg in messages:
        if msg["role"] == "user":
            story.append(Paragraph("Vi:", user_style))
        else:
            story.append(Paragraph("AI:", user_style))
        story.append(Paragraph(msg["content"].replace('\n', '<br/>'), ai_style))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=5why-analiza.pdf'
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)