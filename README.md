# Healthcare Document Chat API

A FastAPI-based backend service that processes healthcare documents and provides intelligent chat capabilities using Google Gemini.

## Features

- Document upload and processing (PDF, DOCX, TXT)
- Text extraction and cleaning
- Vector embeddings with ChromaDB
- RAG pipeline with Google Gemini
- Medical terminology handling
- Conversation history management

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- Gemini API key

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd healthcare-chat-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key