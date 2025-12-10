from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import sys
from pathlib import Path

# Add ai_services to path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from ai_services.GroqClient import generate_completion

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    if not text.strip():
        raise ValueError("No text found in PDF")
    return text

def split_text(text: str, chunk_size=2000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

def call_llama(prompt: str) -> str:
    """Use GroqClient instead of local Ollama"""
    return generate_completion(prompt)

def summarize_text(chunks: list) -> str:
    limited_text = "\n".join(chunks[:8])  # keep fast
    prompt = f"Summarize the following text clearly and concisely:\n\n{limited_text}"
    return call_llama(prompt)
