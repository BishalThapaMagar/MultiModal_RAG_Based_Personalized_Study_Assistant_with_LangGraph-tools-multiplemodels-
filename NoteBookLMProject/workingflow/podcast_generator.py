import os
import re
import io
from langchain_community.llms import Ollama
from gtts import gTTS
from pydub import AudioSegment

# TTS configuration for each host
TTS_CONFIG = {
    "Host 1": {"lang": "en", "tld": "com"},
    "Host 2": {"lang": "en", "tld": "co.uk"}
}

# Regex to match host dialogue
DIALOGUE_PATTERN = re.compile(r"^\[Host\s*([12])\]:\s*(.+)$")

class PodcastGenerator:
    def __init__(self):
        self.llm = Ollama(model="llama3.2")

    def _save_script(self, script: str, filename="podcast_script.txt") -> str:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script)
        return os.path.abspath(filename)

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
        return self.llm.invoke(prompt)

    def generate_podcast(self, context: str, filename="podcast.mp3") -> tuple[str, str]:
        # 1) Generate and save script
        script = self.generate_script(context)
        script_path = self._save_script(script)

        # 2) Parse script into ordered segments
        segments = []
        for line in script.splitlines():
            m = DIALOGUE_PATTERN.match(line.strip())
            if m:
                speaker = f"Host {m.group(1)}"
                text = m.group(2).strip()
                segments.append((speaker, text))

        if not segments:
            raise ValueError("No dialogue segments found in generated script.")

        # 3) Synthesize each segment in order and build audio
        combined = AudioSegment.empty()
        for speaker, text in segments:
            cfg = TTS_CONFIG.get(speaker)
            if not cfg:
                continue
            # TTS to buffer
            tts = gTTS(text=text, lang=cfg['lang'], tld=cfg['tld'], slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            seg_audio = AudioSegment.from_file(buf, format="mp3")
            # Append with short pause
            combined += seg_audio + AudioSegment.silent(duration=300)

        # 4) Export combined audio
        combined.export(filename, format="mp3")
        return os.path.abspath(filename), script_path
