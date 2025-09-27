import uuid
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from app.models.database import vector_db
from app.services.medical_ner import medical_ner
from app.services.gemini_service import gemini_service
from app.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.conversation_history = {}
        self.medical_disclaimer = "Disclaimer: This AI assistant provides information based on uploaded documents and should not be used for medical diagnosis or treatment decisions. Please consult with qualified healthcare professionals for medical advice."
    
    async def process_message(self, chat_message: Dict) -> Dict[str, Any]:
        """Process chat message using RAG pipeline with Gemini"""
        start_time = time.time()
        session_id = chat_message['session_id']
        user_message = chat_message['message']
        context_documents = chat_message.get('context_documents')
        
        try:
            logger.info(f"💬 Processing message: '{user_message}'")
            
            # Step 1: Retrieve relevant context
            context_results = self._retrieve_context(user_message, context_documents)
            logger.info(f"📚 Retrieved {len(context_results)} context chunks")
            
            # Step 2: Generate response using RAG with Gemini
            response = await self._generate_rag_response(user_message, context_results)
            logger.info(f"🤖 Generated response: {response[:100]}...")
            print("................response",response)
            # Step 3: Update conversation history
            self._update_conversation_history(session_id, user_message, response)
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence(context_results, response)
            
            processing_time = time.time() - start_time
            
            result = {
                'response': response,
                'sources': self._format_sources(context_results),
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'medical_disclaimer': self.medical_disclaimer
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing chat message: {str(e)}")
            raise e
    
    def _retrieve_context(self, query: str, document_ids: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve relevant context using vector similarity search"""
        # Expand medical abbreviations in query for better search
        expanded_query = medical_ner.expand_abbreviations(query)
        logger.info(f"🔍 Expanded query: '{expanded_query}'")
        
        # Search for relevant chunks
        results = vector_db.search(expanded_query, n_results=5, document_ids=document_ids)
        
        # Filter and rank results
        filtered_results = self._filter_relevant_results(results, query)
        logger.info(f"✅ Filtered to {len(filtered_results)} relevant results")
        
        return filtered_results
    
    def _filter_relevant_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Filter and rank search results based on relevance"""
        if not results:
            logger.warning("⚠️ No results found from vector search")
            return []
        
        # Simple relevance filtering
        relevant_results = []
        
        for result in results:
            relevance_score = self._calculate_relevance_score(result, query)
            if relevance_score > 0.1:  # Threshold for relevance
                result['relevance_score'] = relevance_score
                relevant_results.append(result)
        
        # Sort by relevance score
        relevant_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_results[:3]  # Return top 3 most relevant results
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calculate relevance score between query and result"""
        score = 0.0
        document_text = result['document'].lower()
        query_lower = query.lower()
        
        # Basic keyword matching
        if any(keyword in document_text for keyword in ['medication', 'prescription', 'drug']):
            if any(keyword in query_lower for keyword in ['medication', 'prescription', 'drug']):
                score += 0.3
        
        if any(keyword in document_text for keyword in ['lab', 'test', 'result']):
            if any(keyword in query_lower for keyword in ['lab', 'test', 'result']):
                score += 0.3
        
        if any(keyword in document_text for keyword in ['diagnosis', 'condition']):
            if any(keyword in query_lower for keyword in ['diagnosis', 'condition']):
                score += 0.3
        
        # Length-based scoring (longer chunks might be more informative)
        score += min(len(document_text) / 1000, 0.1)
        
        return min(score, 1.0)
    
    async def _generate_rag_response(self, query: str, context_results: List[Dict]) -> str:
        """Generate response using Retrieval-Augmented Generation with Gemini"""
        
        if not context_results:
            logger.warning("⚠️ No context results found, using fallback")
            return await self._generate_fallback_response(query)
        
        # Build context from retrieved documents
        context_text = self._build_context_text(context_results)
        logger.info(f"📝 Built context with {len(context_text)} characters")
        
        # Use Gemini for response generation
        response = await gemini_service.generate_response(query, context_text)
        return response
    
    def _build_context_text(self, context_results: List[Dict]) -> str:
        """Build context text from retrieved documents"""
        if not context_results:
            return "No relevant document content found."
        
        context_parts = ["Relevant medical document excerpts:"]
        
        for i, result in enumerate(context_results):
            metadata = result.get('metadata', {})
            filename = metadata.get('filename', 'Unknown document')
            section = metadata.get('section', 'General')
            content = result['document']
            
            context_parts.append(f"\n--- Excerpt {i+1} from {filename} ({section}) ---")
            context_parts.append(content)
        
        return "\n".join(context_parts)
    
    async def _generate_fallback_response(self, query: str) -> str:
        """Generate fallback response when no context is found"""
        # Try using Gemini without specific context
        response = await gemini_service.generate_response(
            f"Please respond to this healthcare-related query: {query}. "
            "Note that no specific document context was found."
        )
        return response
    
    def _format_sources(self, context_results: List[Dict]) -> List[Dict[str, Any]]:
        """Format source information for response"""
        sources = []
        for result in context_results:
            metadata = result.get('metadata', {})
            sources.append({
                'document_id': metadata.get('document_id'),
                'filename': metadata.get('filename'),
                'section': metadata.get('section', 'unknown'),
                'relevance_score': result.get('relevance_score', 0),
                'content_preview': result['document'][:100] + '...' if len(result['document']) > 100 else result['document']
            })
        return sources
    
    def _calculate_confidence(self, context_results: List[Dict], response: str) -> float:
        """Calculate confidence score for the response"""
        if not context_results:
            return 0.3
        
        total_relevance = sum(result.get('relevance_score', 0) for result in context_results)
        avg_relevance = total_relevance / len(context_results)
        
        # Adjust based on response quality
        quality_indicators = [
            len(response) > 50,
            any(keyword in response.lower() for keyword in ['medication', 'lab', 'result', 'diagnosis', 'patient']),
            'not found' not in response.lower() and 'unable' not in response.lower()
        ]
        
        quality_boost = sum(quality_indicators) * 0.1
        confidence = min(avg_relevance + quality_boost, 1.0)
        return round(confidence, 2)
    
    def _update_conversation_history(self, session_id: str, user_message: str, response: str):
        """Update conversation history for the session"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = {
                'created_at': datetime.now(),
                'messages': []
            }
        
        self.conversation_history[session_id]['messages'].append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'ai_response': response,
            'type': 'message'
        })
        
        # Limit history to last 50 messages
        if len(self.conversation_history[session_id]['messages']) > 50:
            self.conversation_history[session_id]['messages'] = self.conversation_history[session_id]['messages'][-50:]

chat_service = ChatService()