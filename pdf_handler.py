import base64

def encode_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    return base64.standard_b64encode(pdf_bytes).decode("utf-8")

def build_message_with_pdf(message, pdf_b64):
    return {
        "role": message["role"],
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_b64,
                }
            },
            {"type": "text", "text": message["content"]}
        ]
    }