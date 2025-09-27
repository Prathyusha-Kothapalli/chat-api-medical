from fastapi import APIRouter, HTTPException
import logging
from app.models.schemas import ChatMessage, ChatResponse
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/message",
    response_model=ChatResponse,
    summary="Send chat message",
    description="Send a message to chat with your healthcare documents"
)
async def chat_message(chat_message: ChatMessage):
    """Send a message and get AI response with document context"""
    try:
        # Validate session_id
        if not chat_message.session_id or not isinstance(chat_message.session_id, str):
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Process the message using chat service (this handles everything internally)
        response_data = await chat_service.process_message({
            'session_id': chat_message.session_id,
            'message': chat_message.message,
            'context_documents': chat_message.context_documents
        })
        print("Response data:",response_data)
        return ChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing message")

@router.get(
    "/history/{session_id}",
    summary="Get chat history",
    description="Retrieve conversation history for a session"
)
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = chat_service.get_conversation_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "created_at": history['created_at'],
            "message_count": len(history['messages']),
            "messages": history['messages']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving history")

@router.delete(
    "/history/{session_id}",
    summary="Delete chat history", 
    description="Clear conversation history for a session"
)
async def clear_chat_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        success = chat_service.delete_conversation_history(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Chat history cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error clearing history")