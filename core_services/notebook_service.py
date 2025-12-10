import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir / "NoteBookLMProject"))

from document_processor import DocumentProcessor
from podcast_generator import PodcastGenerator
from ai_services.GroqClient import generate_completion

# Global processor and generator (singleton pattern)
_processor = None
_podcast_gen = None

def get_processor():
    """Get or create document processor instance"""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
        _processor.load_vector_store()
    return _processor

def get_podcast_generator():
    """Get or create podcast generator instance"""
    global _podcast_gen
    if _podcast_gen is None:
        _podcast_gen = PodcastGenerator()
    return _podcast_gen

def process_notebook_document(file_path: str, model_provider: str = "groq") -> dict:
    """Process PDF document for NotebookLM-style Q&A and audio generation"""
    try:
        processor = get_processor()
        podcast_gen = get_podcast_generator()
        
        # Process document
        result = processor.process_document(file_path)
        
        if "Error" in result:
            raise Exception(result)
        
        # Ensure vector store is loaded
        if not processor.vector_store:
            processor.load_vector_store()
        
        # Generate podcast/audio summary
        if processor.vector_store:
            docs = processor.vector_store.similarity_search("key concepts and main topics", k=7)
            context = "\n".join([d.page_content[:300] for d in docs])
            
            # Generate unique filenames
            base_name = Path(file_path).stem
            timestamp = str(int(__import__('time').time()))
            audio_filename = f"{base_name}_podcast_{timestamp}.mp3"
            script_filename = f"{base_name}_script_{timestamp}.txt"
            
            # Generate audio
            audio_path, script_path = podcast_gen.generate_podcast(
                context, 
                filename=audio_filename,
                script_filename=script_filename
            )
            
            return {
                "success": True,
                "message": "Document processed and ready for Q&A",
                "audio_file": Path(audio_path).name if audio_path else None,
                "script_file": Path(script_path).name if script_path else None,
                "audio_url": f"/download/{Path(audio_path).name}" if audio_path else None,
                "model_used": model_provider
            }
        else:
            raise Exception("Failed to process document - vector store not initialized")
            
    except Exception as e:
        raise Exception(f"NotebookLM processing error: {str(e)}")

def ask_question_about_document(question: str, model_provider: str = "groq") -> dict:
    """Ask question about uploaded document"""
    try:
        processor = get_processor()
        
        # Ensure vector store is loaded
        if not processor.vector_store:
            processor.load_vector_store()
        
        if not processor.vector_store:
            raise Exception("No document uploaded. Please upload a PDF first.")
        
        # Check if vector store has content
        test_docs = processor.vector_store.similarity_search("test", k=1)
        if not test_docs or (len(test_docs) == 1 and test_docs[0].page_content.strip() == ""):
            raise Exception("No document uploaded. Please upload a PDF first.")
        
        # Search relevant documents
        docs = processor.vector_store.similarity_search(question, k=5)
        context = "\n".join([d.page_content for d in docs])
        
        # Generate answer using selected model
        prompt = f"""Answer based on the provided context.

Context:
{context}

Question: {question}

Answer:"""
        
        answer = generate_completion(prompt, "You are a helpful assistant analyzing documents.")
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": len(docs),
            "model_used": model_provider
        }
        
    except Exception as e:
        raise Exception(f"Q&A error: {str(e)}")

