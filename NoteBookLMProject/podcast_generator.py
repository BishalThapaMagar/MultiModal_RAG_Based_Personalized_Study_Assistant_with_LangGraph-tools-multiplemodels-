import os
import re
import io
import sys
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment

# Add ai_services to path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from ai_services.GroqClient import generate_completion

# TTS configuration for each host
TTS_CONFIG = {
    "Host 1": {"lang": "en", "tld": "com"},
    "Host 2": {"lang": "en", "tld": "co.uk"}
}

# Regex to match host dialogue
DIALOGUE_PATTERN = re.compile(r"^\[Host\s*([12])\]:\s*(.+)$")

class PodcastGenerator:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"  # Groq model
        # Ensure output directory exists
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    def _save_script(self, script: str, filename="podcast_script.txt") -> str:
        # Save to output directory
        script_path = self.output_dir / filename
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        return str(script_path.absolute())

    def generate_script(self, context: str) -> str:
        # Stronger prompt to ensure LLM stays on-topic and covers every concept
        prompt = f"""
You are creating a technical podcast dialogue between two hosts that discusses the following key concepts:

{context}

Instructions:
- Alternate between [Host 1] and [Host 2] turns.
- Ensure **every** concept listed is covered in the conversation.
- Provide at least one turn per concept.
- Provide at least 10 total turns (5 per host).
- Keep each turn concise (no more than 2 sentences).
- Format strictly as:
  [Host 1]: ...
  [Host 2]: ...

Begin now:
"""
        # Use Groq API instead of Ollama
        system_message = "You are a podcast script writer. Create engaging technical discussions between two hosts."
        return generate_completion(prompt, system_message, self.model)

    def generate_podcast(self, context: str, filename="podcast.mp3", script_filename="podcast_script.txt") -> tuple[str, str]:
        try:
            print(f"🎙️ Starting podcast generation...")
            
            # 1) Generate and save script
            print(f"📝 Generating script with Groq...")
            script = self.generate_script(context)
            script_path = self._save_script(script, script_filename)
            print(f"✅ Script saved: {script_path}")

            # 2) Parse script into ordered segments
            segments = []
            for line in script.splitlines():
                m = DIALOGUE_PATTERN.match(line.strip())
                if m:
                    speaker = f"Host {m.group(1)}"
                    text = m.group(2).strip()
                    segments.append((speaker, text))

            if not segments:
                print(f"❌ No dialogue segments found in script")
                raise ValueError("No dialogue segments found in generated script.")
            
            print(f"🎯 Found {len(segments)} dialogue segments")

            # 3) Synthesize each segment in order and build audio
            combined = AudioSegment.empty()
            for i, (speaker, text) in enumerate(segments, 1):
                cfg = TTS_CONFIG.get(speaker)
                if not cfg:
                    continue
                print(f"🔊 Synthesizing segment {i}/{len(segments)}: {speaker}")
                # TTS to buffer
                tts = gTTS(text=text, lang=cfg['lang'], tld=cfg['tld'], slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                seg_audio = AudioSegment.from_file(buf, format="mp3")
                # Append with short pause
                combined += seg_audio + AudioSegment.silent(duration=300)

            # 4) Export combined audio to output directory
            audio_path = self.output_dir / filename
            print(f"💾 Exporting audio to: {audio_path}")
            combined.export(str(audio_path), format="mp3")
            print(f"✅ Audio generated successfully!")
            
            return str(audio_path.absolute()), script_path
            
        except Exception as e:
            print(f"❌ Podcast generation error: {e}")
            raise Exception(f"Failed to generate podcast: {str(e)}")