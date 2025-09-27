import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import os
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.enabled = False
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini service with detailed logging"""
        api_key = settings.GOOGLE_API_KEY
        
        logger.info(f"Attempting to initialize Gemini with API key: {api_key[:10]}..." if api_key else "No API key provided")
        
       
        try:
           
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.enabled = True
            logger.info("✅ Gemini service initialized successfully")
            
            test_response = self.model.generate_content("Say 'Hello' in one word.")
            logger.info(f"✅ Gemini test successful: {test_response.text}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini service: {str(e)}")
            self.enabled = False
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        if not self.enabled:
            logger.warning("Gemini service is disabled - returning fallback response")
            return self._get_fallback_response()
        
        try:
            full_prompt = self._build_prompt(prompt, context)
            
            logger.info(f"📤 Sending request to Gemini with {len(full_prompt)} characters")
            
            response = self.model.generate_content(full_prompt)
            
            logger.info(f"📥 Gemini response received: {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error generating response with Gemini: {str(e)}")
            return f"Error: {str(e)}. Please try again."
    
    def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
        base_prompt = """You are a helpful medical AI assistant. Analyze the healthcare documents and provide accurate information.

Guidelines:
- Use only the provided medical context
- Be precise with medical terms, dosages, and values
- If information is not in the context, say so
- Do not provide medical advice

Medical Context:
"""

        if context:
            prompt = f"{base_prompt}\n{context}\n\nQuestion: {query}\n\nAnswer:"
        else:
            prompt = f"{base_prompt}\nNo specific context provided. Please ask about medications, lab results, or other medical information from the documents.\n\nQuestion: {query}\n\nAnswer:"
        
        return prompt
    
    def _get_fallback_response(self) -> str:
        return "I'm currently unable to generate AI responses. Please check the server configuration."

gemini_service = GeminiService()

