import os
import fitz
import pytesseract
import logging
from PIL import Image
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Try to use new HuggingFace embeddings, fallback to old if not available
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentProcessor:
    def __init__(self, persist_dir="./faiss_db"):
        # Using HuggingFace embeddings instead of Ollama (faster and more reliable)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n• ", ". ", " ", ""]
        )
        self.persist_directory = persist_dir
        self.vector_store = None

    def load_vector_store(self):
        """Load existing vector store or create empty one if none exists"""
        try:
            if os.path.exists(self.persist_directory):
                print(f"📂 Loading existing vector store from {self.persist_directory}")
                self.vector_store = FAISS.load_local(
                    self.persist_directory, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Vector store loaded successfully")
            else:
                print(f"📂 No existing vector store found, creating empty one")
                self.vector_store = FAISS.from_texts([""], self.embeddings)
        except Exception as e:
            logging.error(f"Vector store loading error: {str(e)}")
            print(f"❌ Vector store loading failed, creating new empty one")
            self.vector_store = FAISS.from_texts([""], self.embeddings)

    def process_document(self, file_path):
        # Don't reload vector store here - preserve the global state
        try:
            doc = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if not text.strip():
                    text = self._ocr_page(page)
                
                if text.strip():
                    text_content.append({
                        "text": text,
                        "metadata": {
                            "source": os.path.basename(file_path),
                            "page": page_num + 1
                        }
                    })

            if not text_content:
                return f"No content found: {os.path.basename(file_path)}"

            chunks = self.text_splitter.create_documents(
                [t["text"] for t in text_content],
                metadatas=[t["metadata"] for t in text_content]
            )
            
            # Create a FRESH vector store for the new document (replace old one)
            print(f"🔄 Creating fresh vector store for {os.path.basename(file_path)}")
            self.vector_store = FAISS.from_texts(
                texts=[c.page_content for c in chunks],
                metadatas=[c.metadata for c in chunks],
                embedding=self.embeddings
            )
            
            # Save the new vector store (overwrites the old one)
            self.vector_store.save_local(self.persist_directory)
            print(f"✅ Fresh vector store saved with {len(chunks)} chunks from {os.path.basename(file_path)}")
            
            return f"Processed {len(chunks)} chunks from {os.path.basename(file_path)}"
        
        except Exception as e:
            logging.error(f"Processing error: {str(e)}")
            return f"Error: {str(e)}"

    def _ocr_page(self, page):
        text = []
        for img in page.get_images():
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image = Image.open(io.BytesIO(base_image["image"]))
            text.append(pytesseract.image_to_string(image))
        return "\n".join(text)