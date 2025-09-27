import os
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List, Tuple
import PyPDF2
from docx import Document
import re
from app.config import settings

class FileHandler:
    @staticmethod
    async def save_upload_file(upload_file: UploadFile, upload_dir: str) -> str:
        """Save uploaded file to disk"""
        file_location = os.path.join(upload_dir, upload_file.filename)
        
        async with aiofiles.open(file_location, 'wb') as file:
            content = await upload_file.read()
            await file.write(content)
        
        # Reset file pointer for further processing
        await upload_file.seek(0)
        return file_location
    
    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Validate file type and size"""
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            return False
        
        # Check file size (approximate - exact check happens during save)
        if file.size > settings.MAX_FILE_SIZE:
            return False
        
        return True
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading TXT file: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str, file_extension: str) -> str:
        """Extract text based on file type"""
        if file_extension == '.pdf':
            return FileHandler.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return FileHandler.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return FileHandler.extract_text_from_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

file_handler = FileHandler()