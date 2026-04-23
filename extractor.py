import json
import os
import re
import base64
import pdfplumber
from docx import Document
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

EXTRACTION_PROMPT = """You are a document analyst for a government office in the Philippines.
Extract the following fields from the document content below.
Return ONLY a valid JSON object with these exact keys (no markdown, no extra text):

{
  "doc_type": "one of: Memo, Letter, Invitation, Circular, Endorsement, Other",
  "doc_date": "date on the document in YYYY-MM-DD format, or empty string if not found",
  "reference_no": "official reference or control number printed on the document, or empty string",
  "sender": "name and/or office of the sender or originating agency",
  "subject": "subject line or title of the document",
  "summary": "1-2 sentence summary of the document's main content and purpose"
}

Document content:
"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON object found in Claude response")


def _extract_pdf_text(file_path: str) -> str:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _call_claude_text(text: str) -> dict:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT + text[:8000]}],
    )
    return _parse_json(msg.content[0].text)


def _call_claude_image(file_path: str, media_type: str) -> dict:
    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data},
                },
                {"type": "text", "text": EXTRACTION_PROMPT + "(analyze the image above)"},
            ],
        }],
    )
    return _parse_json(msg.content[0].text)


def extract_document_info(file_path: str, filename: str) -> dict:
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        text = _extract_pdf_text(file_path)
        return _call_claude_text(text)
    elif ext == "docx":
        text = _extract_docx_text(file_path)
        return _call_claude_text(text)
    elif ext in ("jpg", "jpeg"):
        return _call_claude_image(file_path, "image/jpeg")
    elif ext == "png":
        return _call_claude_image(file_path, "image/png")
    else:
        raise ValueError(f"Unsupported file type: .{ext}")
