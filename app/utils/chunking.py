import re
from typing import List, Dict, Any
from app.config import settings

class DocumentChunker:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def chunk_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """Chunk document by paragraphs with medical section awareness"""
        # Split by multiple newlines
        paragraphs = re.split(r'\n\s*\n', text.strip())
        chunks = []
        current_chunk = ""
        current_metadata = {}
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check for medical section headers
            section_info = self._detect_medical_section(paragraph)
            
            if section_info:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': current_metadata.copy()
                    })
                
                # Start new chunk with section info
                current_chunk = paragraph + "\n"
                current_metadata.update(section_info)
            else:
                # Check if adding this paragraph would exceed chunk size
                if len(current_chunk + paragraph) > self.chunk_size and current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': current_metadata.copy()
                    })
                    # Start new chunk with overlap
                    current_chunk = self._get_overlap_text(current_chunk) + paragraph + "\n"
                else:
                    current_chunk += paragraph + "\n"
        
        # Add the final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': current_metadata.copy()
            })
        
        return chunks
    
    def _detect_medical_section(self, text: str) -> Dict[str, Any]:
        """Detect medical section headers and extract metadata"""
        section_patterns = {
            'patient_info': r'(patient information|demographics|personal details)',
            'medical_history': r'(medical history|past medical history|history of present illness)',
            'medications': r'(medications|prescriptions|drugs)',
            'lab_results': r'(lab results|laboratory|blood tests)',
            'diagnosis': r'(diagnosis|assessment|impression)',
            'treatment': r'(treatment plan|management|therapy)',
            'vital_signs': r'(vital signs|vitals|blood pressure|heart rate)'
        }
        
        text_lower = text.lower().strip()
        for section, pattern in section_patterns.items():
            if re.search(pattern, text_lower):
                return {'section': section, 'section_header': text}
        
        return {}
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlapping text for chunk continuity"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) <= 1:
            return text[-self.chunk_overlap:] if len(text) > self.chunk_overlap else text
        
        overlap_text = ""
        for sentence in reversed(sentences):
            if sentence.strip():
                if len(overlap_text + sentence) <= self.chunk_overlap:
                    overlap_text = sentence + ". " + overlap_text
                else:
                    break
        
        return overlap_text.strip()

document_chunker = DocumentChunker()