from pathlib import Path
import logging
import os
import shutil

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pypdf import PdfReader
import uvicorn


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
GROQ_MODEL = "llama-3.1-8b-instant"
MAX_DOCUMENT_CHARS = 12000

stored_document_text = ""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_file() -> None:
    """Load key=value pairs from Backend/.env only."""
    if not ENV_FILE.exists():
        return

    with ENV_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip("\"'")


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


def format_groq_error(error: Exception) -> str:
    error_text = str(error)
    error_text_lower = error_text.lower()
    status_code = getattr(error, "status_code", None)

    if (
        status_code == 401
        or "401" in error_text
        or "invalid api key" in error_text_lower
        or "api key" in error_text_lower
        or "unauthorized" in error_text_lower
    ):
        return (
            "Groq API key is invalid or missing. Add a valid GROQ_API_KEY in Backend/.env "
            "and restart the backend."
        )

    if (
        status_code == 400
        or "model" in error_text_lower
        or "decommissioned" in error_text_lower
        or "not found" in error_text_lower
    ):
        return "Groq model error. Check that the selected Groq model is enabled for your account."

    if (
        status_code == 429
        or "429" in error_text
        or "resource_exhausted" in error_text_lower
        or "quota" in error_text_lower
        or "rate" in error_text_lower
    ):
        return (
            "Groq quota or rate limit reached for this API key. Wait a little and try again, "
            "or use a Groq API key with available quota."
        )

    return "Groq could not answer right now. Please try again."


load_env_file()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend running successfully"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global stored_document_text

    try:
        file_path = UPLOAD_FOLDER / file.filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        reader = PdfReader(str(file_path))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        stored_document_text = text.strip()

        if not stored_document_text:
            return {
                "error": "No readable text found in this PDF. Try a text-based PDF instead of a scanned image PDF."
            }

        return {
            "message": "PDF uploaded successfully",
            "document_text": stored_document_text,
        }

    except Exception as error:
        return {"error": f"PDF upload failed: {error}"}


@app.post("/ask-question")
async def ask_question(query: str = Form(...), document_text: str = Form("")):
    doc_text = (document_text or stored_document_text).strip()

    if not doc_text:
        return {"answer": "Upload PDF first"}

    client = get_groq_client()

    if client is None:
        return {
            "answer": (
                "Groq API key is missing. Create Backend/.env with "
                "GROQ_API_KEY=your_api_key_here, then restart the backend."
            )
        }

    trimmed_doc_text = doc_text[:MAX_DOCUMENT_CHARS]
    prompt = f"""Document text:
{trimmed_doc_text}

Question:
{query}
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions using only the provided PDF document text. "
                        "If the answer is not in the document, say that it is not available in the PDF. "
                        "Format answers in a clean structured way. When returning details, use one field per line "
                        "like 'Name: value'. Do not put the whole answer in one paragraph."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=GROQ_MODEL,
            temperature=0.2,
            max_completion_tokens=500,
        )

        answer = chat_completion.choices[0].message.content

        return {"answer": answer or "No answer received from Groq."}

    except Exception as error:
        logger.exception("Groq request failed")
        return {"answer": format_groq_error(error)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
