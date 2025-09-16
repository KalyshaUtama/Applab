# FastAPI app for chatbot with file upload functionality
# cmd to run:  uvicorn App:app --reload  --host 0.0.0.0 --port 8000  
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import ChatbotOrchestrator
from fastapi import FastAPI, UploadFile, File
from orchestrator import ChatbotOrchestrator
from langchain.docstore.document import Document
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
import os
from PyPDF2 import PdfReader
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment configuration with fallbacks
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.fanar.qa/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Fanar-S-1-7B")

# Validate required environment variables
if not API_KEY:
    logger.error("API_KEY environment variable is required!")
    raise ValueError("API_KEY must be set in environment variables")

# Initialize chatbot orchestrator
try:
    bot = ChatbotOrchestrator(API_KEY, BASE_URL)
    logger.info("Chatbot orchestrator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {e}")
    raise

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str


# Chat endpoint
@app.post("/chat")
async def chat_endpoint(payload: Query):
    try:
        response = await bot.chat(payload.query)
        logger.info(f"Responding with: {response}")
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {"response": "I apologize, but I'm experiencing some technical difficulties. Please try again."}

# File upload endpoint
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



