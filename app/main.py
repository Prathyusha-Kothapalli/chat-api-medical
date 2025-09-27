from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.config import settings
from app.services.gemini_service import gemini_service

# Import routers directly to avoid circular imports
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
print(settings.GEMINI_MODEL)
print(settings.GOOGLE_API_KEY)
print("hi")
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A FastAPI-based healthcare document processing and intelligent chat service",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers directly
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])

@app.exception_handler(500)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": str(exc)}
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Healthcare Chat API...")
    
    # Check if upload directories exist
    from app.config import settings
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"ChromaDB path: {settings.CHROMA_DB_PATH}")
    
    # Initialize services with better logging
    from app.services.gemini_service import gemini_service
    # gemini_service()

    if gemini_service.enabled:
        logger.info("✅ Gemini service initialized successfully")
        logger.info(f"Gemini model: {settings.GEMINI_MODEL}")
    else:
        logger.warning("❌ Gemini service is disabled")
        logger.warning("Please set GOOGLE_API_KEY in your .env file")
    
    from app.services.medical_ner import medical_ner
    logger.info("✅ Medical NER service initialized")
    
    # Check vector database
    from app.models.database import vector_db
    logger.info("✅ Vector database initialized")
    
    # Check other services
    from app.services.document_processor import document_processor
    from app.services.embedding_service import embedding_service
    from app.services.chat_service import chat_service
    logger.info("✅ All services initialized successfully")
    
    logger.info("✅ Healthcare Chat API started successfully")
    logger.info(f"📚 API documentation available at: http://localhost:8000/api/docs")
    logger.info(f"🔍 Health check available at: http://localhost:8000/api/v1/health")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Healthcare Chat API...")

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Healthcare Chat API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )