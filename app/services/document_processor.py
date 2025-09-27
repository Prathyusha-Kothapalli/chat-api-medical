import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import PyPDF2
from docx import Document
import aiofiles
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile) -> str:
        file_path = self.upload_dir / file.filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return str(file_path)
    
    def _get_file_type(self, filename: str) -> str:
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Map extensions to content types
        extension_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        
        if file_extension in extension_map:
            return extension_map[file_extension]
        else:
            raise HTTPException(400, f"Unsupported file extension: {file_extension}")
    
    async def extract_text(self, file_path: str, file_type: str) -> str:
        try:
            if file_type == "application/pdf":
                return await self._extract_from_pdf(file_path)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return await self._extract_from_docx(file_path)
            elif file_type == "text/plain":
                return await self._extract_from_txt(file_path)
            else:
                raise HTTPException(400, f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise HTTPException(500, f"Failed to extract text: {str(e)}")
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise Exception(f"PDF extraction error: {str(e)}")
    
    async def _extract_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            raise Exception(f"DOCX extraction error: {str(e)}")
    
    async def _extract_from_txt(self, file_path: str) -> str:
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                return await file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
                return await file.read()
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {str(e)}")
            raise Exception(f"TXT extraction error: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = ' '.join(text.split())
        
        medical_abbreviations = {
            'BP': 'Blood Pressure',
            'HR': 'Heart Rate',
            'RR': 'Respiratory Rate',
            'Temp': 'Temperature',
            'Rx': 'Prescription',
            'Dx': 'Diagnosis',
            'Tx': 'Treatment'
        }
        
        for abbr, full in medical_abbreviations.items():
            text = text.replace(f' {abbr} ', f' {full} ')
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        if not text:
            return []
            
        chunks = []
        words = text.split()
        
        if len(words) == 0:
            return []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_data = {
                'text': chunk_text,
                'start_index': i,
                'end_index': i + len(chunk_words),
                'chunk_id': f"chunk_{len(chunks)}"
            }
            chunks.append(chunk_data)
        
        return chunks

document_processor = DocumentProcessor()