import os
import asyncio
import glob
from pypdf import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_BASE_DIR = "knowledge_base"
CHROMA_PATH = "./chroma_db"

def ingest_documents():
    print(f"--- Starting Ingestion (ChromaDB) from '{KNOWLEDGE_BASE_DIR}' ---")
    
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)
        print(f"Created directory: {KNOWLEDGE_BASE_DIR}")
        return

    # Initialize Embeddings
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Initialize Chroma
    vector_store = Chroma(
        collection_name="knowledge_base",
        embedding_function=embeddings_model,
        persist_directory=CHROMA_PATH
    )

    files = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.*"))
    print(f"Found {len(files)} files.")

    documents_to_add = []

    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        content = ""
        try:
            if file_path.lower().endswith(".pdf"):
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
            elif file_path.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                continue
                
            if not content.strip():
                continue

            # Simple Chunking
            chunk_size = 1000
            overlap = 100
            
            for i in range(0, len(content), chunk_size - overlap):
                chunk_text = content[i:i + chunk_size]
                doc = Document(
                    page_content=chunk_text,
                    metadata={"source": filename, "chunk_index": i}
                )
                documents_to_add.append(doc)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if documents_to_add:
        print(f"Adding {len(documents_to_add)} chunks to ChromaDB...")
        vector_store.add_documents(documents_to_add)
        print("--- Ingestion Complete ---")
    else:
        print("No new documents to add.")

if __name__ == "__main__":
    ingest_documents()
