import sys
from pathlib import Path

# Add paths for utilities
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir / "summarizer-and-quiz-generator" / "backend"))

from utils import extract_text_from_pdf, split_text, summarize_text
from quiz_generator import generate_quiz
from flashcard_gen import generate_flashcards

def generate_quiz_from_pdf(file_path: str, num_questions: int = 5, model_provider: str = "groq") -> dict:
    """Generate quiz from PDF file"""
    try:
        # Process PDF
        text = extract_text_from_pdf(file_path)
        chunks = split_text(text)
        summary = summarize_text(chunks)
        quiz = generate_quiz(summary, num_questions)
        
        return {
            "success": True,
            "summary": summary,
            "quiz": quiz,
            "stats": {
                "text_length": len(text),
                "questions": len(quiz)
            },
            "model_used": model_provider
        }
    except Exception as e:
        raise Exception(f"Quiz generation error: {str(e)}")

def generate_flashcards_from_pdf(file_path: str, num_cards: int = 10, model_provider: str = "groq") -> dict:
    """Generate flashcards from PDF file"""
    try:
        # Process PDF
        text = extract_text_from_pdf(file_path)
        chunks = split_text(text)
        summary = summarize_text(chunks)
        flashcards = generate_flashcards(summary, chunks, text, num_cards)
        
        return {
            "success": True,
            "summary": summary,
            "flashcards": flashcards,
            "stats": {
                "text_length": len(text),
                "cards": len(flashcards)
            },
            "model_used": model_provider
        }
    except Exception as e:
        raise Exception(f"Flashcard generation error: {str(e)}")

