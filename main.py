import os
import io
import json
import time
import logging
import base64
from typing import Optional

import pdfplumber
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.file_handler import read_admin_data
from admin_routes import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    handlers=[logging.FileHandler("scanno_ai.log"), logging.StreamHandler()],
)

app = FastAPI(title="Scanno AI - Vehicle Inspection Analyzer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

def get_openai_client() -> OpenAI:
    data = read_admin_data()
    key = data.get("openai_api_key")
    if not key:
        raise HTTPException(status_code=500, detail="OpenAI key not configured by admin.")
    return OpenAI(api_key=key)

# PDF text extraction (for text-based PDFs)
def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip() or None
    except Exception as e:
        logging.error(f"PDF reading failed: {e}")
        return None

# GPT Vision analysis (for scanned or image PDFs)
# ---------------------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_vision(image_bytes: bytes, client: OpenAI) -> str:
    """Analyze scanned PDF or image using GPT-4o Vision."""
    logging.info("Sending image to GPT-4o Vision...")
    start = time.time()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """
You are Scanno — the official smart car inspection expert in Qatar.
You analyze vehicle inspection reports in English or Arabic.

Guidelines:
- Respond in Arabic if the report is Arabic, otherwise English.
- Be short, clear, and friendly.
- Never mention being an AI.
- Return ONLY valid JSON:

{
  "summary": "1-line car condition",
  "risk_level": "Low|Medium|High|Critical",
  "issues": ["bullet points"],
  "maintenance": ["action items"],
  "recommendation": "final advice"
}
"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this car inspection report image and respond in JSON only."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.2
        )

        elapsed = time.time() - start
        logging.info(f"GPT-4o Vision responded in {elapsed:.2f}s")
        return response.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------
# GPT Text analysis (for extractable PDF text)
# ---------------------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_text(text: str, client: OpenAI) -> str:
    logging.info("Analyzing text-based report with GPT-4o...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are Scanno — the smart car inspection expert in Qatar."
                },
                {
                    "role": "user",
                    "content": f"Analyze this inspection report text and return JSON only:\n{text}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"Text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------
# Main endpoint: analyze-report
# ---------------------------------------------------------------------
@app.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    try:
        client = get_openai_client()
        filename = file.filename.lower()
        file_bytes = await file.read()

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
            if text:
                raw_response = analyze_with_gpt_text(text, client)
            else:
                raw_response = analyze_with_gpt_vision(file_bytes, client)

        elif filename.endswith((".jpg", ".jpeg", ".png")):
            raw_response = analyze_with_gpt_vision(file_bytes, client)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        # Extract JSON from response safely
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        json_str = raw_response[start:end]
        result = json.loads(json_str)

        return {"file": filename, "report": result}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------
@app.get("/")
async def root():
    return JSONResponse({"message": "Scanno AI backend is live."})

