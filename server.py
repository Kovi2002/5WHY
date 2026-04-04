import os
import json
import reportlab
from io import BytesIO
from flask import Flask, request, jsonify, send_from_directory, make_response
from chat import send_to_claude
from pdf_handler import encode_pdf, build_message_with_pdf
from history import save_message, init_db  # ← DODAJ
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_font_dir = os.path.join(os.path.dirname(reportlab.__file__), "fonts")
pdfmetrics.registerFont(TTFont("Vera", os.path.join(_font_dir, "Vera.ttf")))
pdfmetrics.registerFont(TTFont("VeraBd", os.path.join(_font_dir, "VeraBd.ttf")))

app = Flask(__name__, static_folder="static")
init_db()  # ← DODAJ

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

    # ← DODAJ shranjevanje zgodovine
    session_id = request.headers.get("X-Session-ID", "unknown")
    if isinstance(messages[-1]["content"], str):
        user_content = messages[-1]["content"]
    else:
        text_parts = [p["text"] for p in messages[-1]["content"] if p.get("type") == "text"]
        user_content = " ".join(text_parts) if text_parts else "PDF sporočilo"

    save_message(session_id, "user", user_content)
    save_message(session_id, "assistant", reply)

    return jsonify({"reply": reply})

@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()
    diagram = data.get("diagram", {})
    problem = diagram.get("problem", "")
    whys = diagram.get("whys", [])
    rootcause = diagram.get("rootcause", "")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    title_style = ParagraphStyle('Title',
                                 fontName='VeraBd', fontSize=18, spaceAfter=6,
                                 textColor=colors.HexColor("#1a1a1a"))
    subtitle_style = ParagraphStyle('Subtitle',
                                    fontName='Vera', fontSize=10, spaceAfter=20,
                                    textColor=colors.HexColor("#888888"))
    label_style = ParagraphStyle('Label',
                                 fontName='VeraBd', fontSize=9, spaceAfter=2,
                                 textColor=colors.HexColor("#888888"))
    value_style = ParagraphStyle('Value',
                                 fontName='Vera', fontSize=11, spaceAfter=14,
                                 textColor=colors.HexColor("#1a1a1a"))
    rootcause_style = ParagraphStyle('RootCause',
                                     fontName='VeraBd', fontSize=11, spaceAfter=6,
                                     textColor=colors.white, backColor=colors.HexColor("#c0392b"),
                                     leftIndent=8, rightIndent=8, leading=16)

    story = []
    story.append(Paragraph("5WHY Analiza", title_style))
    story.append(Paragraph("Poročilo o analizi temeljnih vzrokov", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0db")))
    story.append(Spacer(1, 0.5*cm))

    if problem:
        story.append(Paragraph("PROBLEM", label_style))
        story.append(Paragraph(problem, value_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0db")))
        story.append(Spacer(1, 0.3*cm))

    for i, why in enumerate(whys):
        if why:
            story.append(Paragraph(f"WHY {i + 1}", label_style))
            story.append(Paragraph(why, value_style))

    if rootcause:
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0db")))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("TEMELJNI VZROK (ROOT CAUSE)", label_style))
        story.append(Paragraph(rootcause, rootcause_style))

    doc.build(story)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=5why-analiza.pdf'
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)