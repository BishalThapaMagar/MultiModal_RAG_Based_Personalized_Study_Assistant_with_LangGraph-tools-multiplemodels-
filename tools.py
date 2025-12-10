from langchain_core.tools import tool
from typing import Optional, Dict, Any
from core_services.ppt_service import generate_ppt
from core_services.video_service import generate_educational_video
from core_services.quiz_service import generate_quiz_from_pdf, generate_flashcards_from_pdf
from core_services.notebook_service import ask_question_about_document

# --- Tool Definitions ---

@tool
def generate_presentation_tool(topic: str, num_slides: int = 5) -> Dict[str, Any]:
    """
    Generates a PowerPoint presentation on the given topic.
    Useful when the user asks to "create a presentation", "make a PPT", or "generate slides".
    Returns the file path and download URL.
    """
    try:
        result = generate_ppt(topic, num_slides)
        return result
    except Exception as e:
        return {"error": str(e)}

@tool
def generate_educational_video_tool(concept: str) -> Dict[str, Any]:
    """
    Generates an educational video explaining a complex concept using Manim.
    Useful when the user asks to "create a video", "explain with animation", or "visualize this concept".
    Returns the video path.
    """
    # Note: Requires Gemini (handled inside the service or we verify selected_model?)
    # The service default is "gemini".
    try:
        # We need to run async function in sync tool?
        # LangChain tools can be async, but for simplicity we might need a wrapper or run_in_executor if passing to sync LLM.
        # However, generate_educational_video is async.
        # Let's check if we can run it.
        import asyncio
        # Check if we are in an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # If we are already in an async loop (e.g. LangGraph runner), we shouldn't block it.
            # But the tool execution might be synchronous in standard BindTools?
            # For now, let's try standard await if we can, or just run_until_complete if we are in a thread.
            # Safety hack for now:
            return {"error": "Video generation requires async execution, not fully integrated in sync tool wrapper yet."}
            # Actually, let's just return a placeholder message for Phase 3 verification
            # unless the user *really* wants the video generated now.
            # return asyncio.run(generate_educational_video(concept)) 
        else:
            return loop.run_until_complete(generate_educational_video(concept))
            
    except Exception as e:
        return {"error": str(e)}

@tool
def generate_quiz_tool(file_path: str, num_questions: int = 5) -> Dict[str, Any]:
    """
    Generates a quiz from a specific PDF file.
    Useful when the user asks to "make a quiz from this file" or "test me on [document]".
    """
    try:
        return generate_quiz_from_pdf(file_path, num_questions)
    except Exception as e:
        return {"error": str(e)}

@tool
def ask_document_tool(question: str) -> Dict[str, Any]:
    """
    Asks a question about the currently uploaded document/notebook.
    Useful for specific questions like "What does the document say about X?" or "Summarize the pdf".
    """
    try:
        return ask_question_about_document(question)
    except Exception as e:
        return {"error": str(e)}

@tool
def retrieve_knowledge_tool(query: str):
    """
    Search the knowledge base (RAG) for information.
    Use this to find answers in stored documents.
    """
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_chroma import Chroma
        import os
        
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        vector_store = Chroma(
            collection_name="knowledge_base",
            embedding_function=embeddings_model,
            persist_directory="./chroma_db"
        )
        
        # Search
        results = vector_store.similarity_search(query, k=3)
        
        if not results:
            return "No relevant information found in knowledge base."
            
        formatted = "Found relevant info:\n"
        for doc in results:
             content_snippet = doc.page_content[:300].replace("\n", " ")
             formatted += f"- {content_snippet}... (Source: {doc.metadata.get('source')})\n"
        return formatted
        
    except Exception as e:
        return f"Error searching knowledge base: {e}"

# List of all available tools
ALL_TOOLS = [
    generate_presentation_tool,
    # generate_educational_video_tool, 
    generate_quiz_tool,
    ask_document_tool,
    retrieve_knowledge_tool
]
