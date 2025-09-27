# Healthcare Document Chat API

A FastAPI backend service that processes healthcare documents and enables intelligent chat capabilities using Google Gemini AI with RAG (Retrieval-Augmented Generation).

## Features

### ✅ Document Processing
- **File Upload**: Support for PDF, DOCX, and TXT files
- **Text Extraction**: Automated text extraction from multiple formats
- **Intelligent Chunking**: Semantic chunking with configurable size/overlap
- **Text Cleaning**: Medical abbreviation expansion and normalization

### ✅ AI/ML Capabilities
- **Vector Embeddings**: Sentence-transformers for document embeddings
- **RAG Pipeline**: Retrieval-Augmented Generation with Google Gemini
- **Similarity Search**: ChromaDB vector database for efficient retrieval
- **Medical NER**: Extraction of medications, lab results, conditions, and vital signs

### ✅ Chat Interface
- **Session Management**: Conversation history per session
- **Context-Aware Responses**: Document-specific answers with sources
- **Confidence Scoring**: Relevance-based confidence metrics
- **Multi-Document Support**: Query across multiple uploaded documents

### ✅ API Endpoints
- **Documents**: Upload, list, view, and delete medical documents
- **Chat**: Send messages, get history, clear conversations
- **Health**: Service status and health checks

## Quick Start

### Installation
```bash
# Clone and setup
git clone <repository>
cd healthcare-chat-api

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Google API key