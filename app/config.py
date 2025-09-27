import os
from typing import Optional, List
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Healthcare Document Chat API"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Vector Database Configuration
    CHROMA_DB_PATH: str = "./chroma_db"
    COLLECTION_NAME: str = "healthcare_documents"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Medical NER Configuration
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Hardcoded settings that don't need env variables
    @property
    def ALLOWED_FILE_TYPES(self) -> List[str]:
        return [".pdf", ".docx", ".txt"]
    
    @property
    def GEMINI_SAFETY_SETTINGS(self) -> dict:
        return {
            "HARASSMENT": "block_none",
            "HATE_SPEECH": "block_none", 
            "SEXUALLY_EXPLICIT": "block_none",
            "DANGEROUS_CONTENT": "block_none"
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)