"""
Models package for Healthcare Chat API.

This package contains:
- schemas.py: Pydantic models for API request/response
- database.py: Database models and vector database setup
"""

# Import only the types, not the instances to avoid circular imports
from app.models.schemas import (
    DocumentUpload,
    DocumentResponse,
    ChatMessage,
    ChatResponse,
    HealthCheck,
    ErrorResponse,
    ProcessingStatus
)

__all__ = [
    'DocumentUpload',
    'DocumentResponse', 
    'ChatMessage',
    'ChatResponse',
    'HealthCheck',
    'ErrorResponse',
    'ProcessingStatus',
]