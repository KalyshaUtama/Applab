# PDF Chatbot Application

A Python-based AI/ML chatbot application that enables users to upload PDF documents and interact with an intelligent assistant that answers questions based on the document content.

## 🚀 Features

- **PDF Document Upload**: Upload and process PDF documents for knowledge base
- **AI-Powered Chat**: Intelligent responses based on uploaded document content
- **Vector Search**: Efficient document retrieval using embeddings
- **Multi-language Support**: Supports English and Arabic queries
- **RESTful API**: Clean API endpoints for all functionalities
- **Web Interface**: User-friendly frontend for document upload and chat
- **Docker Support**: Containerized deployment for easy setup

## 🏗️ Architecture

```
├── App.py                 # Main FastAPI application
├── orchestrator.py        # Core business logic orchestrator
├── embeddings.py          # Vector database and document processing
├── llm.py                 # Language model integration
├── public/frontend.html   # Web user interface
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
└── .env                  # Environment variables (create this)
```

## 📋 Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- At least 4GB RAM recommended

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd pdf-chatbot
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# API Configuration
API_KEY=your_api_key_here
BASE_URL=https://api.fanar.qa/v1
MODEL_NAME=Fanar-S-1-7B

# Application Settings
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Vector Database Settings
PERSIST_DIRECTORY=chroma_agents
EMBEDDING_MODEL=BAAI/bge-m3
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

### 3. Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn App:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

### 1. Build Docker Image

```bash
docker build -t pdf-chatbot:latest .
```

### 2. Run with Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pdf-chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
      - BASE_URL=${BASE_URL}
      - MODEL_NAME=${MODEL_NAME}
    volumes:
      - ./chroma_agents:/app/chroma_agents
      - ./uploads:/app/uploads
    restart: unless-stopped

volumes:
  chroma_data:
  uploads:
```

Run with:
```bash
docker-compose up -d
```

### 3. Run Single Container

```bash
docker run -d \
  --name pdf-chatbot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/chroma_agents:/app/chroma_agents \
  pdf-chatbot:latest
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Upload PDF Document
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- uploaded_file: PDF file (required)
```

**Response:**
```json
{
  "status": "success",
  "document_id": "doc_123456",
  "filename": "document.pdf"
}
```

#### 2. Chat with Bot
```http
POST /chat
Content-Type: application/json

{
  "query": "What is the main topic of the document?"
}
```

**Response:**
```json
{
  "response": "Based on the uploaded document, the main topic is..."
}
```

## 🖥️ Frontend Usage

1. Open `http://localhost:8000/frontend.html` in your browser
2. Upload PDF documents using the file upload section
3. Ask questions in the chat interface
4. The bot will respond based on the uploaded document content

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | LLM API key | Required |
| `BASE_URL` | LLM API base URL | Required |
| `MODEL_NAME` | LLM model name | Fanar-S-1-7B |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `PERSIST_DIRECTORY` | Vector DB directory | chroma_agents |
| `EMBEDDING_MODEL` | Embedding model | BAAI/bge-m3 |
| `CHUNK_SIZE` | Text chunk size | 800 |
| `CHUNK_OVERLAP` | Text chunk overlap | 100 |

## 🚀 Production Deployment

### Cloud Deployment Options

#### Option 1: Docker on VPS/Cloud Server
```bash
# On your server
git clone <repo-url>
cd pdf-chatbot
cp .env.example .env
# Edit .env with your secrets
docker-compose up -d
```

#### Option 2: Container Registry Deployment
```bash
# Build and push to registry
docker build -t your-registry/pdf-chatbot:latest .
docker push your-registry/pdf-chatbot:latest

# Deploy on cloud platform (AWS ECS, Google Cloud Run, etc.)
```

### Reverse Proxy Setup (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📊 Monitoring & Logging

The application provides structured logging for:
- API requests and responses
- Document processing status
- Error tracking
- Performance metrics

Logs are output to stdout/stderr and can be collected using Docker logging drivers.

## 🛠️ Development

### Code Structure
- `App.py`: FastAPI application and route handlers
- `orchestrator.py`: Business logic coordination
- `embeddings.py`: Vector database operations
- `llm.py`: Language model interactions
- `frontend.html`: Web interface

### Adding New Features
1. Add new endpoints in `App.py`
2. Implement business logic in `orchestrator.py`
3. Update frontend if needed
4. Add tests and documentation

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Test specific endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?"}'
```

## 📝 Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "uploaded_file=@example.pdf"
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the summary of the document?"}'
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit API keys to version control
2. **CORS**: Configure specific origins in production
3. **File Validation**: Only accept PDF files
4. **Rate Limiting**: Consider adding rate limiting for production
5. **HTTPS**: Use SSL/TLS in production
6. **Input Validation**: Validate all user inputs

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No text content found in file"
- **Solution**: Ensure PDF is text-based, not scanned images

**Issue**: "Failed to connect to API"
- **Solution**: Check API_KEY and BASE_URL in environment variables

**Issue**: "Docker container exits immediately"
- **Solution**: Check environment variables and Docker logs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.


**Note**: This application is designed for the AppLab AI/ML Engineer position assignment. Please ensure you have proper API access before deployment.
