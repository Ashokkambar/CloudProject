from fastapi import APIRouter
from app.storage import document_store

router = APIRouter()

@router.post("/ask-question")
async def ask_question(query: str):

    if document_store.document_text == "":
        return {"answer": "Upload PDF first"}

    # temporary response for testing

    return {
        "answer": f"You asked: {query}"
    }