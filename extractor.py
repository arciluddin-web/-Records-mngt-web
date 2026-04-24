import io
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
    
    # Remove markdown code block if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    
    # Find JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Claude response: {e}")
    
    raise ValueError(f"No JSON object found in Claude response. Received: {text[:200]}")


def _extract_pdf_text(file_path: str) -> str:
    pages = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                pages.append(text or "")
        extracted = "\n".join(pages).strip()
        if not extracted:
            raise ValueError("PDF extraction returned empty text")
        return extracted
    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {e}")


def _extract_docx_text(file_path: str) -> str:
    try:
        doc = Document(file_path)
        extracted = "\n".join(p.text for p in doc.paragraphs).strip()
        if not extracted:
            raise ValueError("DOCX extraction returned empty text")
        return extracted
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX: {e}")


def _call_claude_text(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Document text is empty. Unable to extract information.")
    
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT + text[:8000]}],
    )
    return _parse_json(msg.content[0].text)


def _extract_pdf_image_bytes(file_path: str) -> bytes:
    try:
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                raise ValueError("PDF has no pages")
            page = pdf.pages[0]
            page_image = page.to_image(resolution=200).original
            buffer = io.BytesIO()
            page_image.save(buffer, format="PNG")
            return buffer.getvalue()
    except Exception as e:
        raise ValueError(f"Failed to render PDF as image: {e}")


def _call_claude_image(image_source, media_type: str) -> dict:
    if isinstance(image_source, bytes):
        image_data = base64.standard_b64encode(image_source).decode("utf-8")
    else:
        with open(image_source, "rb") as f:
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
        try:
            text = _extract_pdf_text(file_path)
            return _call_claude_text(text)
        except ValueError as e:
            if "empty text" in str(e).lower() or "failed to extract pdf" in str(e).lower():
                image_bytes = _extract_pdf_image_bytes(file_path)
                return _call_claude_image(image_bytes, "image/png")
            raise
    elif ext == "docx":
        text = _extract_docx_text(file_path)
        return _call_claude_text(text)
    elif ext in ("jpg", "jpeg"):
        return _call_claude_image(file_path, "image/jpeg")
    elif ext == "png":
        return _call_claude_image(file_path, "image/png")
    else:
        raise ValueError(f"Unsupported file type: .{ext}")
