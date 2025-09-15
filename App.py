# FastAPI app for chatbot with
# cmd to run:  uvicorn App:app --reload  --host 0.0.0.0 --port 8000  
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import ChatbotOrchestrator
import time
from fastapi import FastAPI, UploadFile, File
from orchestrator import ChatbotOrchestrator
from langchain.docstore.document import Document
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
import sounddevice as sd
import soundfile as sf
import os
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader
from io import BytesIO
import asyncpg
import smtplib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# API_KEY = "JbLrsXw8BGH205xmRESWPK6aPnqzj33Z"
# BASE_URL = "https://api.mistral.ai/v1"

API_KEY = "hOsM7lLIu4MKMMNimQgEmDwRn0Z0xRfT"
BASE_URL = "https://api.fanar.qa/v1"
bot = ChatbotOrchestrator(API_KEY, BASE_URL)

# Allow CORS so Svelte frontend can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:5173"] in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

class Response(BaseModel):
    query: str


class TextInput(BaseModel):
    content: str
    title: str


# Pydantic models
class ChatMessage(BaseModel):
    session_id: str
    user_id: str
    role: str
    content: str



# FIXED: Corrected the chat endpoint logic
@app.post("/chat")
async def chat_endpoint(payload: Query):
    try:
        response = await bot.chat(payload.query)
        logger.info(f"Responding with: {response}")
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {"response": "I apologize, but I'm experiencing some technical difficulties. Please try again."}




@app.get("/view-all")
async def view_all():
    try:
        doc_data = await bot.retrieve_all_docs()
        if len(doc_data["ids"]) == 0:
            return {"status": "empty", "documents": []}
        print("this my doc data",doc_data)
        docs = []
        for doc_id, doc in zip(doc_data["ids"], doc_data["documents"]):
            preview = (doc[:100].replace("\n", " ") + "...") if doc else "[Empty]"
            docs.append({
                "id": doc_id,
                "preview": preview
            })
        print("this my docs",docs)
        return {"status": "success", "documents": docs}

    except Exception as e:
        logger.error(f"Error in /view-all: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")



@app.post("/upload")
async def add_documents(uploaded_file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {uploaded_file.filename} with content type: {uploaded_file.content_type}")
        
        file_text = ""

        if uploaded_file.content_type == "application/pdf":
            contents = await uploaded_file.read()
            pdf_file = BytesIO(contents)
            reader = PdfReader(pdf_file)
            file_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {uploaded_file.content_type}")

        if not file_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")

        logger.info(f"File text extracted: {file_text[:100]}...")
        clean_text = file_text.replace("\n", " ").strip()
        new_doc = Document(page_content=clean_text, metadata={"filename": uploaded_file.filename})
        doc_id = bot.add_documents([new_doc])
        
        logger.info(f"Document added with ID: {doc_id}")
        return {"status": "success", "document_id": doc_id, "filename": uploaded_file.filename}
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")



@app.delete("/delete/{doc_id}")
async def delete_file(doc_id: str):
    try:
        success, msg = bot.embedder.delete_document(doc_id)
        return {"status": success, "message": msg}
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.get("/status")
async def check_status():
    try:
        bot_status = bot.ping()
        db_status = app.state.db is not None
        return {
            "status": "healthy",
            "bot": bot_status,
            "database": db_status,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}






# #fasrAPI app for chatbot with TTS and file upload capabilities
# #cmd to run:  uvicorn App:app --reload  --host 0.0.0.0 --port 5173  
#