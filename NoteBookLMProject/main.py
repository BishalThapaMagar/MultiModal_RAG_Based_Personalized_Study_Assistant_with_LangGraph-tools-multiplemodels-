
import os
import re
import io
import numpy as np
from pydub import AudioSegment
from gtts import gTTS
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from sentence_transformers import CrossEncoder
from document_processor import DocumentProcessor

# Configuration
TTS_CONFIG = {
    "Host 1": {"lang": "en", "tld": "com"},
    "Host 2": {"lang": "en", "tld": "co.uk"}
}
DIALOGUE_PATTERN = re.compile(r"^\[Host\s*([12])\]:\s*(.+)$")

class PodcastGenerator:
    def __init__(self):
        self.llm = OllamaLLM(model="llama3.2")

    def generate_podcast(self, context):
        """Generate podcast audio and script with error handling"""
        try:
            # Generate script
            prompt = f"""Create technical podcast dialogue between two hosts discussing:
{context}

Format requirements:
- Alternate between [Host 1] and [Host 2]
- 10+ turns total (5+ each)
- 2 sentences max per turn
- Cover all key concepts
- Strict format:
[Host 1]: ...
[Host 2]: ..."""
            
            script = self.llm.invoke(prompt)
            script_path = self._save_script(script)
            audio_path = self._generate_audio(script)
            
            return audio_path, script_path
        
        except Exception as e:
            return "", f"Generation failed: {str(e)}"

    def _save_script(self, script):
        """Save generated script to file"""
        path = "podcast_script.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        return os.path.abspath(path)

    def _generate_audio(self, script):
        """Convert script to audio"""
        segments = []
        for line in script.splitlines():
            match = DIALOGUE_PATTERN.match(line.strip())
            if match:
                segments.append((
                    f"Host {match.group(1)}",
                    match.group(2).strip()
                ))

        if not segments:
            raise ValueError("No valid dialogue found in script")

        audio = AudioSegment.empty()
        for speaker, text in segments:
            config = TTS_CONFIG.get(speaker)
            if config:
                tts = gTTS(text=text[:150], **config)
                buffer = io.BytesIO()
                tts.write_to_fp(buffer)
                buffer.seek(0)
                audio += AudioSegment.from_file(buffer, format="mp3")
                audio += AudioSegment.silent(300)

        audio_path = "podcast_summary.mp3"
        audio.export(audio_path, format="mp3")
        return os.path.abspath(audio_path)

def main():
    processor = DocumentProcessor()
    podcast = PodcastGenerator()
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    # Initialize QA chain
    model = OllamaLLM(model="llama3.2")
    chain = ChatPromptTemplate.from_template("{input}") | model

    while True:
        print("\n=== Document Analysis Interface ===")
        print("1. Upload Document")
        print("2. Ask Question")
        print("3. Generate Podcast")
        print("4. Exit")
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1":
            file_path = input("Document path: ").strip()
            print(processor.process_document(file_path))
        
        elif choice == "2":
            question = input("\nQuestion: ").strip()
            if not processor.vector_store:
                print("Upload documents first!")
                continue
                
            docs = processor.vector_store.similarity_search(question, k=5)
            context = "\n\n".join(
                f"Source: {d.metadata['source']} (Page {d.metadata.get('page','?')})\n{d.page_content}"
                for d in docs[:3]
            )
            response = chain.invoke({"input": f"Context: {context}\nQuestion: {question}\nAnswer:"})
            print(f"\nANSWER:\n{response}")
        
        elif choice == "3":
            if processor.vector_store:
                docs = processor.vector_store.similarity_search("key concepts", k=7)
                context = "\n".join(d.page_content[:300] for d in docs)
                audio_path, script_path = podcast.generate_podcast(context)
                
                if audio_path and script_path:
                    print(f"\nAudio saved: {audio_path}")
                    print(f"Script saved: {script_path}")
                else:
                    print("Podcast generation failed")
            else:
                print("Upload documents first!")
        
        elif choice == "4":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()