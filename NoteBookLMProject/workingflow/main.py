# from langchain_community.llms import Ollama
# from langchain.prompts import ChatPromptTemplate
# from document_processor import DocumentProcessor
# from podcast_generator import PodcastGenerator

# # Initialize core components
# model = Ollama(model="llama3.2")
# processor = DocumentProcessor()
# podcast = PodcastGenerator()

# # Define the Q&A template
# template = """You are a helpful assistant analyzing documents. Answer based on context.
# Context: {context}
# Question: {question}
# Answer:"""
# prompt = ChatPromptTemplate.from_template(template)
# chain = prompt | model

# def handle_query(question):
#     if processor.vector_store is None:
#         return "Please upload documents first!"
    
#     # Retrieve relevant context
#     docs = processor.vector_store.similarity_search(question, k=5)
#     context = "\n".join([d.page_content for d in docs])
#     return chain.invoke({"context": context, "question": question})

# def main_flow():
#     while True:
#         print("\n=== NotebookLM Interface ===")
#         print("1. Upload Document (PDF/TXT)")
#         print("2. Ask Question")
#         print("3. Generate Podcast Summary")
#         print("4. Exit")
        
#         choice = input("\nChoose an option (1-4): ").strip()
        
#         if choice == "1":
#             file_path = input("Enter document path: ").strip()
#             print(processor.process_document(file_path))
            
#         elif choice == "2":
#             question = input("\nEnter your question: ").strip()
#             print(f"\nANSWER: {handle_query(question)}")
            
#         elif choice == "3":
#            # In the podcast generation section (choice == 3):
#             # In the podcast generation section (choice == 3):
#             if processor.vector_store:
#                 print("Generating podcast summary...")
#                 # Get key themes from the document
#                 summary_query = "What are the main topics and key concepts in this document?"
#                 docs = processor.vector_store.similarity_search(summary_query, k=5)
#                 context = "\n".join([f"Concept {i+1}: {d.page_content}" for i,d in enumerate(docs)])
                
#                 audio_path, script_path = podcast.generate_podcast(context)
#                 print(f"Audio podcast saved to: {audio_path}")
#                 print(f"Script saved to: {script_path}")
        
#             else:
#                 print("Please upload documents first!")

#         elif choice == "4":
#             print("Exiting NotebookLM...")
#             break
                    
#         else:
#              print("Invalid choice. Please select 1-4.")

# if __name__ == "__main__":
#     main_flow()




from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from document_processor import DocumentProcessor
from podcast_generator import PodcastGenerator

# Initialize components
model = Ollama(model="llama3.2")
processor = DocumentProcessor()
podcast = PodcastGenerator()

# Q&A Prompt Template
template = """You are a helpful assistant analyzing documents. Answer based on the provided context.

Context:
{context}

Question:
{question}

Answer:"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def handle_query(question):
    if processor.vector_store is None:
        return "Please upload documents first!"
    
    docs = processor.vector_store.similarity_search(question, k=5)
    context = "\n".join([d.page_content for d in docs])
    return chain.invoke({"context": context, "question": question})

def main_flow():
    while True:
        print("\n=== NotebookLM Interface ===")
        print("1. Upload Document (PDF/TXT)")
        print("2. Ask Question")
        print("3. Generate Podcast Summary")
        print("4. Exit")

        choice = input("\nChoose an option (1-4): ").strip()

        if choice == "1":
            file_path = input("Enter document path: ").strip()
            print(processor.process_document(file_path))

        elif choice == "2":
            question = input("\nEnter your question: ").strip()
            print(f"\nANSWER: {handle_query(question)}")

        elif choice == "3":
            if processor.vector_store:
                print("Generating podcast summary...")
                summary_query = "What are the main topics and key concepts in this document?"
                docs = processor.vector_store.similarity_search(summary_query, k=5)
                context = "\n".join([f"Concept {i+1}: {d.page_content}" for i, d in enumerate(docs)])

                audio_path, script_path = podcast.generate_podcast(context)
                print(f"Podcast script saved to: {script_path}")
                print(f"Audio podcast saved to: {audio_path}")
            else:
                print("Please upload documents first!")

        elif choice == "4":
            print("Exiting NotebookLM...")
            break

        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main_flow()
