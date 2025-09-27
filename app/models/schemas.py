from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentUpload(BaseModel):
    description: Optional[str] = Field(None, description="Optional document description")

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    processing_status: ProcessingStatus
    extracted_text_length: int
    description: Optional[str] = None

class ChatMessage(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User's message")
    context_documents: Optional[List[str]] = Field(None, description="Specific documents to use as context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used for response")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the response")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    medical_disclaimer: str = Field(..., description="Medical disclaimer message")

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    code: int