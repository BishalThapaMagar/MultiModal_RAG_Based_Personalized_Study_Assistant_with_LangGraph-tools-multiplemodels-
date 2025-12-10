# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain_ollama import OllamaEmbeddings

# class DocumentProcessor:
#     def __init__(self):
#         self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200
#         )
#         self.vector_store = None

#     def process_document(self, file_path):
#         # Choose loader based on file type
#         if file_path.endswith('.pdf'):
#             loader = PyPDFLoader(file_path)
#         else:
#             loader = TextLoader(file_path)
            
#         documents = loader.load()
#         chunks = self.text_splitter.split_documents(documents)
        
#         # Create or update vector store
#         self.vector_store = Chroma.from_documents(
#             documents=chunks,
#             embedding=self.embeddings,
#             persist_directory="./chroma_db"
#         )
        
#         return "Document processed and stored successfully!"

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import shutil
import os

class DocumentProcessor:
    def __init__(self, persist_dir="./chroma_db"):
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.persist_directory = persist_dir
        self.vector_store = None

    def process_document(self, file_path):
        # Clear previous vector store to avoid mixing old documents
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)

        # Choose loader based on file type
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)

        # Load and chunk
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        # Create a fresh vector store
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        # Persist embeddings to disk
        self.vector_store.persist()

        return f"Document '{os.path.basename(file_path)}' processed and stored successfully!"
