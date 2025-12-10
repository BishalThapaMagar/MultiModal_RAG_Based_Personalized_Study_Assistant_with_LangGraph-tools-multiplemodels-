# Core Services - Business logic layer
from .ppt_service import generate_ppt
from .quiz_service import generate_quiz_from_pdf, generate_flashcards_from_pdf
from .notebook_service import process_notebook_document, ask_question_about_document
from .chat_service import chat_with_ai, stream_chat

__all__ = [
    'generate_ppt',
    'generate_quiz_from_pdf',
    'generate_flashcards_from_pdf',
    'process_notebook_document',
    'ask_question_about_document',
    'chat_with_ai',
    'stream_chat'
]

