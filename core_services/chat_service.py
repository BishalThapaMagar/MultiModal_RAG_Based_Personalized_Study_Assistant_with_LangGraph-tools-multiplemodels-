from typing import Optional
from chat import GroqChat
from .notebook_service import get_processor

# Global chat instance
_chat_instance = None

def get_chat_instance():
    """Get or create chat instance"""
    global _chat_instance
    if _chat_instance is None:
        _chat_instance = GroqChat()
    return _chat_instance

def chat_with_ai(message: str, use_document: bool = False, model_provider: str = "groq") -> dict:
    """Chat with AI with optional document context"""
    try:
        chat = get_chat_instance()
        processor = get_processor()
        
        if use_document:
            # Chat with document context
            if not processor.vector_store:
                processor.load_vector_store()
                
                if not processor.vector_store:
                    return {
                        "success": True,
                        "message": message,
                        "response": "I don't have any documents uploaded yet. Please upload a PDF document using the document upload feature first, then I can answer questions about its content. In the meantime, I'm happy to help with general study questions!",
                        "context_used": False,
                        "model": f"StudyBuddyAI ({model_provider})"
                    }
            
            # Search for relevant context
            try:
                docs = processor.vector_store.similarity_search(message, k=5)
                vector_results = [doc.page_content for doc in docs if doc.page_content.strip()]
                
                if vector_results:
                    # Use chat with document context
                    document_context = f"Student has uploaded documents for study assistance. Found {len(vector_results)} relevant sections."
                    response = chat.chat_with_document(message, document_context, vector_results)
                    
                    return {
                        "success": True,
                        "message": message,
                        "response": response,
                        "context_used": True,
                        "sources_found": len(docs),
                        "model": f"StudyBuddyAI with Document Analysis ({model_provider})"
                    }
                else:
                    # No relevant content found
                    fallback_response = chat.chat(
                        f"The student asked: '{message}' about their uploaded document, but I couldn't find relevant content in the document for this question. Please provide general study assistance for this topic."
                    )
                    return {
                        "success": True,
                        "message": message,
                        "response": f"I couldn't find specific information about your question in the uploaded document. However, let me help you with this topic:\n\n{fallback_response}",
                        "context_used": False,
                        "sources_found": 0,
                        "model": f"StudyBuddyAI ({model_provider})"
                    }
                
            except Exception as e:
                # Fallback to regular chat
                response = chat.chat(
                    f"I had trouble searching the uploaded document for this question: '{message}'. Please provide general study assistance on this topic."
                )
                return {
                    "success": True,
                    "message": message,
                    "response": f"I encountered an issue accessing your document, but I can still help with your question:\n\n{response}",
                    "context_used": False,
                    "error": f"Document search failed: {str(e)}",
                    "model": f"StudyBuddyAI ({model_provider})"
                }
        else:
            # Regular chat without document context
            try:
                response = chat.chat(message)
                
                return {
                    "success": True,
                    "message": message,
                    "response": response,
                    "context_used": False,
                    "model": f"StudyBuddyAI ({model_provider})"
                }
            except Exception as chat_error:
                return {
                    "success": False,
                    "error": str(chat_error),
                    "response": f"Error processing your message: {str(chat_error)}",
                    "model": f"StudyBuddyAI ({model_provider})"
                }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "I'm sorry, I'm having trouble connecting right now. Please try again."
        }

def stream_chat(message: str, model_provider: str = "groq"):
    """Stream chat responses - placeholder for now"""
    # This would need to be implemented with async generators for streaming
    # For now, we'll keep the streaming logic in main.py
    raise NotImplementedError("Streaming chat needs to be implemented in routes layer")

