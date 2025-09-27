import uuid
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import logging

from app.models import DocumentResponse, ProcessingStatus
from app.services.document_processor import document_processor
from app.services.embedding_service import embedding_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

documents_store = {}

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    description: str = None
):
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {'.pdf', '.docx', '.txt'}

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: PDF, DOCX, TXT. Got: {file_extension}"
        )
    
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        document_id = str(uuid.uuid4())
        
        file_path = await document_processor.save_upload_file(file)
        
        file_type = document_processor._get_file_type(file.filename)
        
        documents_store[document_id] = {
            'id': document_id,
            'filename': file.filename,
            'file_type': file_type,
            'file_size': file.size,
            'upload_timestamp': datetime.now(),
            'processing_status': ProcessingStatus.UPLOADED,
            'file_path': file_path,
            'description': description
        }
        
        await _process_document_background(document_id)
        
        return DocumentResponse(
            id=document_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file.size,
            upload_timestamp=documents_store[document_id]['upload_timestamp'],
            processing_status=ProcessingStatus.PROCESSING,
            extracted_text_length=0,
            description=description
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

async def _process_document_background(document_id: str):
    try:
        doc_info = documents_store[document_id]
        doc_info['processing_status'] = ProcessingStatus.PROCESSING
        
        text = await document_processor.extract_text(doc_info['file_path'], doc_info['file_type'])
        cleaned_text = document_processor.clean_text(text)
        
        
        chunks = document_processor.chunk_text(cleaned_text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        
       
        embedding_service.store_document_chunks(document_id, chunks)
        
     
        doc_info['processing_status'] = ProcessingStatus.COMPLETED
        doc_info['extracted_text'] = cleaned_text
        doc_info['extracted_text_length'] = len(cleaned_text)
        doc_info['chunk_count'] = len(chunks)
        doc_info['processed_timestamp'] = datetime.now()
        
        logger.info(f"Successfully processed document {document_id}")
        
    except Exception as e:
        doc_info['processing_status'] = ProcessingStatus.FAILED
        doc_info['error'] = str(e)
        logger.error(f"Error processing document {document_id}: {str(e)}")

@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    
    return [
        DocumentResponse(
            id=doc_id,
            filename=doc_info['filename'],
            file_type=doc_info['file_type'],
            file_size=doc_info['file_size'],
            upload_timestamp=doc_info['upload_timestamp'],
            processing_status=doc_info['processing_status'],
            extracted_text_length=doc_info.get('extracted_text_length', 0),
            description=doc_info.get('description')
        )
        for doc_id, doc_info in documents_store.items()
    ]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents_store[document_id]
    return DocumentResponse(
        id=doc_info['id'],
        filename=doc_info['filename'],
        file_type=doc_info['file_type'],
        file_size=doc_info['file_size'],
        upload_timestamp=doc_info['upload_timestamp'],
        processing_status=doc_info['processing_status'],
        extracted_text_length=doc_info.get('extracted_text_length', 0),
        description=doc_info.get('description')
    )

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    if document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        doc_info = documents_store[document_id]
        
        if os.path.exists(doc_info['file_path']):
            os.remove(doc_info['file_path'])
        
        embedding_service.delete_document_chunks(document_id)
        
        del documents_store[document_id]
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")