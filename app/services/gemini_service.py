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
        print("----api key:",api_key)
        logger.info(f"Attempting to initialize Gemini with API key: {api_key[:10]}..." if api_key else "No API key provided")
        
        # if not api_key or api_key == settings.GOOGLE_API_KEY:
        #     logger.warning("❌ GOOGLE_API_KEY not set or is placeholder. Gemini integration will be disabled.")
        #     self.enabled = False
        #     return
        
        try:
            print(".............key......",settings.GOOGLE_API_KEY)
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.enabled = True
            logger.info("✅ Gemini service initialized successfully")
            
            # Test the connection with a simple request
            test_response = self.model.generate_content("Say 'Hello' in one word.")
            logger.info(f"✅ Gemini test successful: {test_response.text}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini service: {str(e)}")
            self.enabled = False
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using Gemini model"""
        if not self.enabled:
            logger.warning("Gemini service is disabled - returning fallback response")
            return self._get_fallback_response()
        
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            logger.info(f"📤 Sending request to Gemini with {len(full_prompt)} characters")
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            logger.info(f"📥 Gemini response received: {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error generating response with Gemini: {str(e)}")
            return f"Error: {str(e)}. Please try again."
    
    def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Build the prompt for Gemini"""
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
        """Get fallback response when Gemini is not available"""
        return "I'm currently unable to generate AI responses. Please check the server configuration."

gemini_service = GeminiService()

# app/services/gemini_service.py
# from google.generativeai  import genai
# from typing import Optional
# import logging
# from app.config import settings

# logger = logging.getLogger(__name__)

# class GeminiService:
#     def __init__(self):
#         self.enabled = False
#         self.client = None

#     def initialize(self):
#         """Initialize Gemini client at startup"""
#         api_key = settings.GOOGLE_API_KEY
#         if not api_key:
#             logger.warning("❌ GOOGLE_API_KEY not set. Gemini integration disabled.")
#             self.enabled = False
#             return

#         try:
#             # Initialize client
#             self.client = genai.Client(api_key=api_key)
#             self.enabled = True
#             logger.info("✅ Gemini client initialized successfully")

#             # Optional test
#             test_response = self.client.models.generate_content(
#                 model=settings.GEMINI_MODEL,
#                 contents="Say 'Hello' in one word."
#             )
#             logger.info(f"✅ Gemini test successful: {test_response.text}")

#         except Exception as e:
#             logger.error(f"❌ Failed to initialize Gemini client: {str(e)}")
#             self.enabled = False

#     async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
#         """Generate AI response using Gemini"""
#         if not self.enabled or not self.client:
#             logger.warning("Gemini client not enabled. Returning fallback response.")
#             return self._get_fallback_response()

#         try:
#             full_prompt = self._build_prompt(prompt, context)
#             # Gemini client call
#             response = self.client.models.generate_content(
#                 model=settings.GEMINI_MODEL,
#                 contents=full_prompt
#             )
#             return response.text

#         except Exception as e:
#             logger.error(f"❌ Error generating response with Gemini: {str(e)}")
#             return self._get_fallback_response()

#     def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
#         base_prompt = """You are a helpful medical AI assistant. Analyze the healthcare documents and provide accurate information.

# Guidelines:
# - Use only the provided medical context
# - Be precise with medical terms, dosages, and values
# - If information is not in the context, say so
# - Do not provide medical advice

# Medical Context:
# """
#         if context:
#             return f"{base_prompt}\n{context}\n\nQuestion: {query}\n\nAnswer:"
#         else:
#             return f"{base_prompt}\nNo specific context provided.\n\nQuestion: {query}\n\nAnswer:"

#     def _get_fallback_response(self) -> str:
#         return "I'm currently unable to generate AI responses. Please check the server configuration."


# # Singleton instance
# gemini_service = GeminiService()

# import google.generativeai as genai
# from typing import Optional
# import logging
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)

# class GeminiService:
#     def __init__(self):
#         self.enabled = False
#         self.model = None

#     def initialize(self):
#         """Initialize Gemini client at startup"""
#         # api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
#         api_key = "AIzaSyCrzBi1Z37nahhpTEAyd_zhv9o9Uy5Pih0"
#         if not api_key:
#             logger.warning("❌ GOOGLE_API_KEY/GEMINI_API_KEY not set. Gemini integration disabled.")
#             self.enabled = False
#             return

#         try:
#             # Configure the API key
#             genai.configure(api_key=api_key)
            
#             # Initialize the model
#             self.model = genai.GenerativeModel('gemini-pro')
#             self.enabled = True
#             logger.info("✅ Gemini client initialized successfully")

#             # Optional test
#             test_response = self.model.generate_content("Say 'Hello' in one word.")
#             logger.info(f"✅ Gemini test successful: {test_response.text}")

#         except Exception as e:
#             logger.error(f"❌ Failed to initialize Gemini client: {str(e)}")
#             self.enabled = False

#     async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
#         """Generate AI response using Gemini"""
#         if not self.enabled or not self.model:
#             logger.warning("Gemini client not enabled. Returning fallback response.")
#             return self._get_fallback_response()

#         try:
#             full_prompt = self._build_prompt(prompt, context)
            
#             # Generate content
#             response = self.model.generate_content(full_prompt)
#             return response.text

#         except Exception as e:
#             logger.error(f"❌ Error generating response with Gemini: {str(e)}")
#             return self._get_fallback_response()

#     def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
#         base_prompt = """You are a helpful medical AI assistant. Analyze the healthcare documents and provide accurate information.

# Guidelines:
# - Use only the provided medical context
# - Be precise with medical terms, dosages, and values
# - If information is not in the context, say so
# - Do not provide medical advice

# Medical Context:
# """
#         if context:
#             return f"{base_prompt}\n{context}\n\nQuestion: {query}\n\nAnswer:"
#         else:
#             return f"{base_prompt}\nNo specific context provided.\n\nQuestion: {query}\n\nAnswer:"

#     def _get_fallback_response(self) -> str:
#         return "I'm currently unable to generate AI responses. Please check the server configuration."


# # Singleton instance
# gemini_service = GeminiService()