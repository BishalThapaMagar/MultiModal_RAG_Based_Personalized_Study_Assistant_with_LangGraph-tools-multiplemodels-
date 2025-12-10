import os
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_text_from_pdf, split_text, summarize_text
from quiz_generator import generate_quiz
from flashcard_gen import generate_flashcards

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    """Upload a PDF → return summary + quiz."""
    try:
        # Save uploaded PDF asynchronously
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Extract + summarize
        text = extract_text_from_pdf(file_path)
        chunks =  split_text(text)
        summary =  summarize_text(chunks)
        # Generate quiz
        quiz = await generate_quiz(summary, num_questions=5)
        
        
        return {
            "filename": file.filename,
            "summary": summary,
            "quiz": quiz,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/flashcards")
async def flashcards_pdf(file: UploadFile = File(...)):
    """Upload a PDF → return summary + flashcards."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Extract + summarize
        text = extract_text_from_pdf(file_path)
        chunks = split_text(text)
        summary = summarize_text(chunks)

        # Generate flashcards
        flashcards = generate_flashcards(summary, chunks, text, num_cards=10)

        return {
            "filename": file.filename,
            "summary": summary,
            "flashcards": flashcards,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))