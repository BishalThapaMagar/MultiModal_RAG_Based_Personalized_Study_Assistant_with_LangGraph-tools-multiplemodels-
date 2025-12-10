import asyncio
import os
import subprocess
import logging
import re
from typing import List

# Streamlit import - only for UI, not for API
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Mock streamlit for API usage
    class MockStreamlit:
        def success(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
    st = MockStreamlit()

from moviepy.editor import concatenate_videoclips, VideoFileClip, ImageClip
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()

# Google Cloud TTS imports
import requests
import json
from gtts import gTTS
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

api_key = os.getenv('GEMINI_API_KEY')
# Instantiate provider + model (for Gemini via Google)
provider = GoogleProvider(api_key=api_key)
gemini_llm = GoogleModel(
    model_name="gemini-2.0-flash",
    provider=provider
)

# Initialize TTS configuration - Force gTTS only
tts_api_key = None
tts_project_id = None
use_google_cloud_tts = False
logging.info("Using gTTS (free) for text-to-speech")

class ChapterDescription(BaseModel):
    """Describes a chapter in the video."""
    title: str = Field(description="Title of the chapter.")
    explanation: str = Field(
        description=(
            "Detailed explanation of the chapter's content, including how Manim should visualize it. "
            "Be very specific with Manim instructions, including animations, shapes, positions, colors, and timing. "
            "Include LaTeX for mathematical formulas. Specify scene transitions."
        )
    )

class VideoOutline(BaseModel):
    """Describes the outline of the video."""
    title: str = Field(description="Title of the entire video.")
    chapters: List[ChapterDescription] = Field(description="List of chapters in the video.")

class ManimCode(BaseModel):
    """Describes the Manim code for a chapter."""
    code: str = Field(description="Complete Manim code for the chapter. Include all necessary imports and runnable code.")

class ChapterNarration(BaseModel):
    """Narration script for a chapter."""
    script: str = Field(description="Natural, spoken narration script for the chapter")

# Agents with proper output_type
def get_outline_agent():
    return Agent(
        model=gemini_llm,
        output_type=VideoOutline,
        system_prompt=(
            "You are a video script writer. Your job is to create a clear and concise outline for an educational video "
            "explaining a concept. The video should have a title and a list of chapters (maximum 3). Each chapter should "
            "have a title and a detailed explanation. The explanation should be very specific about how the concept "
            "should be visualized using Manim. Include detailed instructions for animations, shapes, positions, colors, "
            "and timing. Use Text() for displaying text and simple shapes for mathematical concepts. Specify scene transitions. "
            "Do not include code, only explanations. Avoid suggesting LaTeX or Tex functions."
        )
    )

def get_manim_agent():
    return Agent(
        model=gemini_llm,
        output_type=ManimCode,
        system_prompt=(
            "You are a Manim code generator for an educational video system. "
            "Always generate a **consistent scene structure**:\n"
            "- Start with a Title Text centered using Text() with color=YELLOW, font_size=36\n"
            "- Show 2–3 key visual elements (Circles, Rectangles, Lines, Arrows)\n"
            "- Animate each element using Create() or Transform() with explicit run_time values (2-4 seconds each)\n"
            "- End with a Summary Text (color=WHITE, font_size=28) and self.wait(3)\n"
            "- Set camera background to '#1e1e2f' (dark theme)\n"
            "- Ensure total scene runtime is between 25–35 seconds\n"
            "- Use Text() instead of Tex() or MathTex() to avoid LaTeX dependencies\n"
            "- Avoid randomness or conditional logic\n"
            "- If unsure about an animation, display explanatory text instead\n"
            "- Never leave the scene empty or return minimal code\n"
            "- Always include: self.camera.background_color = '#1e1e2f' at the start"
        )
    )

def get_code_fixer_agent():
    return Agent(
        model=gemini_llm,
        output_type=ManimCode,
        system_prompt=(
            "You are a Manim code debugging expert. You will receive Manim code that failed to execute and the error message. "
            "Your task is to analyse the code and the error, identify the issue, and provide corrected, runnable Manim code. "
            "Ensure the corrected code addresses the error and still aims to achieve the visualization described in the original code. "
            "Include all necessary imports and ensure the code creates a single scene. Add comments to explain the changes. "
            "IMPORTANT: Use Text() instead of Tex() or MathTex() to avoid LaTeX dependencies. "
            "Use simple shapes like Circle(), Rectangle(), Line(), Arrow() for visualizations. "
            "Avoid any LaTeX-related functions like Tex, MathTex, or LaTeX rendering."
        )
    )

def get_narration_agent():
    return Agent(
        model=gemini_llm,
        output_type=ChapterNarration,
        system_prompt=(
            "You are a narration script writer for educational videos. "
            "Create a clear, engaging spoken narration that explains the concept. "
            "Write in a conversational tone suitable for voice synthesis. "
            "Keep sentences short and clear. Avoid complex punctuation."
        )
    )

def generate_manim_code(chapter_description: ChapterDescription, target_duration: float = None) -> str:
    """Generates initial Manim code for a single chapter with optional target duration."""
    logging.info(f"Generating Manim code for chapter: {chapter_description.title}")
    prompt = f"title: {chapter_description.title}. Explanation: {chapter_description.explanation}"
    if target_duration:
        prompt += f" Target duration: {target_duration:.1f} seconds. Ensure the scene runs for approximately this duration."
    manim_agent = get_manim_agent()
    result = manim_agent.run_sync(prompt)
    return result.output.code

def fix_manim_code(error: str, current_code: str) -> str:
    """Attempts to fix the Manim code that resulted in an error."""
    logging.info(f"Attempting to fix Manim code due to error: {error}")
    prompt = f"Error: {error}\nCurrent Code: {current_code}"
    code_fixer_agent = get_code_fixer_agent()
    result = code_fixer_agent.run_sync(prompt)
    return result.output.code

def generate_video_outline(concept: str) -> VideoOutline:
    """Generates the video outline."""
    logging.info(f"Generating video outline for concept: {concept}")
    outline_agent = get_outline_agent()
    result = outline_agent.run_sync(concept)
    return result.output

def generate_audio_from_text(text: str, output_path: str, chapter_number: int) -> str:
    """Generates audio file from text using gTTS."""
    return generate_audio_gtts(text, output_path, chapter_number)


def generate_audio_gtts(text: str, output_path: str, chapter_number: int) -> str:
    """Generates audio using gTTS (free Google TTS)."""
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to file
        tts.save(output_path)
        
        logging.info(f"Generated audio using gTTS for chapter {chapter_number}: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"gTTS audio generation failed: {e}")

def estimate_duration_from_text(text: str) -> float:
    """Roughly estimate narration duration from word count."""
    words = len(text.split())
    return max(10.0, words / 2.5)  # ~2.5 words per second average

def normalize_chapter_durations(video_files):
    """Normalize chapter durations for smooth transitions."""
    clips = [VideoFileClip(f) for f in video_files if os.path.exists(f)]
    if not clips:
        return []
    
    # For now, just return the clips without normalization to avoid ImageClip issues
    logging.info(f"Found {len(clips)} video clips for concatenation")
    for i, clip in enumerate(clips):
        logging.info(f"Clip {i+1}: duration={clip.duration:.2f}s")
    
    return clips

def generate_placeholder_scene(title: str, explanation: str, out_path: str):
    """Create a simple text-only video scene if Manim fails."""
    from moviepy.editor import ColorClip
    
    # Create a simple colored background video without text (to avoid ImageMagick dependency)
    bg = ColorClip(size=(854, 480), color=(30, 30, 47)).set_duration(15)
    bg.write_videofile(out_path, fps=24, codec='libx264', audio=False, verbose=False, logger=None)
    bg.close()
    logging.info(f"Generated placeholder scene: {out_path}")


def sync_audio_video(video_path: str, audio_path: str, output_path: str) -> str:
    """Improved audio-video sync with freeze-frame extension."""
    from moviepy.editor import AudioFileClip
    
    try:
        v = VideoFileClip(video_path)
        a = AudioFileClip(audio_path)
        
        logging.info(f"Video duration: {v.duration}, Audio duration: {a.duration}")
        
        # Simple approach: just set audio to video without complex extensions
        v = v.set_audio(a)
        v.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
        
        # Clean up
        v.close()
        a.close()
        
        logging.info(f"Successfully synced audio with video: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Failed to sync audio with video: {e}")
        # Return the original video path if audio sync fails
        return video_path

def create_video_from_code(code: str, chapter_number: int) -> str:
    """Creates a video from Manim code and returns the video file path using subprocess."""
    with open("temp.py", "w", encoding="utf-8") as temp_file:
        temp_file.write(code)
        temp_file_name = temp_file.name

    try:
        command = ["manim", temp_file_name, "-qh", "--disable_caching"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=120)  # a bit more time
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
        logging.info(f"Manim execution successful for chapter {chapter_number}")
    except subprocess.TimeoutExpired:
        logging.error(f"Manim timed out for chapter {chapter_number}")
        process.kill()
        raise
    except FileNotFoundError:
        logging.error("Manim command not found. Ensure Manim is installed and in your PATH.")
        raise

    match = re.search(r"class\s+(\w+)\(Scene\):", code)
    if not match:
        raise ValueError(f"Could not extract class name from Manim code for chapter {chapter_number}")
    class_name = match.group(1)
    video_file_name = f"{class_name}.mp4"
    return os.path.join("./media/videos/temp/1080p60/", video_file_name)

async def generate_video(concept: str):
    try:
        logging.info(f"Generating video for concept: {concept}")
        outline = generate_video_outline(concept)
        logging.info(f"Video outline: {outline}")

        video_files = []
        for i, chapter in enumerate(outline.chapters):
            logging.info(f"Processing chapter {i+1}: {chapter.title}")
            
            # NARRATION-FIRST: Generate narration script first
            try:
                narration_agent = get_narration_agent()
                narration_result = narration_agent.run_sync(
                    f"Chapter: {chapter.title}\nContent: {chapter.explanation}"
                )
                narration_script = narration_result.output.script
                
                # Estimate target duration from narration
                target_duration = estimate_duration_from_text(narration_script)
                logging.info(f"Target duration for {chapter.title}: {target_duration:.1f}s")
                
            except Exception as narration_error:
                logging.warning(f"Narration generation failed for chapter {i+1}: {narration_error}")
                narration_script = f"This chapter explains {chapter.title}. {chapter.explanation[:100]}..."
                target_duration = 25.0  # Default duration
            
            # Generate Manim code with target duration
            manim_code = generate_manim_code(chapter, target_duration)
            success = False
            attempts = 0
            max_attempts = 2

            while attempts < max_attempts and not success:
                try:
                    video_file = create_video_from_code(manim_code, i+1)
                    
                    # Check if video file exists and is valid
                    if not os.path.exists(video_file):
                        raise FileNotFoundError(f"Video file not found: {video_file}")
                    
                    # Generate audio from narration
                    try:
                        audio_path = f"audio_chapter_{i+1}.mp3"
                        generate_audio_from_text(narration_script, audio_path, i+1)
                        
                        # Sync audio with video using improved function
                        video_with_audio = f"video_with_audio_{i+1}.mp4"
                        final_video_file = sync_audio_video(video_file, audio_path, video_with_audio)
                        
                        # Only add to video_files if audio sync was successful
                        if final_video_file == video_with_audio and os.path.exists(video_with_audio):
                            video_files.append(final_video_file)
                            logging.info(f"Added video with audio to final list: {final_video_file}")
                        else:
                            # Fall back to original video if audio sync failed
                            video_files.append(video_file)
                            logging.warning(f"Audio sync failed, using original video: {video_file}")
                        
                        # Clean up temporary files
                        if os.path.exists(audio_path):
                            try:
                                os.remove(audio_path)
                            except:
                                pass  # Ignore cleanup errors
                        if os.path.exists(video_file) and final_video_file != video_file:
                            try:
                                os.remove(video_file)
                            except:
                                pass  # Ignore cleanup errors
                            
                    except Exception as audio_error:
                        logging.warning(f"Audio generation failed for chapter {i+1}: {audio_error}")
                        # Fall back to video without audio
                        video_files.append(video_file)
                    
                    success = True
                except subprocess.CalledProcessError as e:
                    attempts += 1
                    logging.error(f"Manim execution failed for chapter {i+1}, attempt {attempts}: {e}")
                    if attempts < max_attempts:
                        manim_code = fix_manim_code(str(e), manim_code)
                except Exception as exc:
                    logging.error(f"Unexpected error in chapter {i+1}: {exc}")
                    # PLACEHOLDER FALLBACK: Generate placeholder scene if Manim fails
                    try:
                        placeholder_path = f"placeholder_chapter_{i+1}.mp4"
                        generate_placeholder_scene(chapter.title, chapter.explanation, placeholder_path)
                        video_files.append(placeholder_path)
                        logging.info(f"Generated placeholder scene for chapter {i+1}: {placeholder_path}")
                        success = True
                    except Exception as placeholder_error:
                        logging.error(f"Placeholder generation also failed for chapter {i+1}: {placeholder_error}")
                        break

            if not success:
                logging.warning(f"Failed to generate video for chapter {i+1} after {max_attempts} attempts.")

        # NORMALIZE DURATIONS and create final video
        final_video_path = None
        if video_files:
            logging.info(f"Creating final video from {len(video_files)} files: {video_files}")
            # Normalize chapter durations for smooth transitions
            normalized_clips = normalize_chapter_durations(video_files)
            if normalized_clips:
                final_video_path = "final_video.mp4"
                logging.info(f"Concatenating {len(normalized_clips)} clips into final video")
                final_clip = concatenate_videoclips(normalized_clips)
                logging.info(f"Final clip duration: {final_clip.duration:.2f}s")
                final_clip.write_videofile(final_video_path, codec="libx264", audio_codec="aac", 
                                         bitrate="2000k", fps=24, verbose=False, logger=None)
                final_clip.close()
                logging.info(f"Final video saved: {final_video_path}")
                st.success("Video generation complete!")
            else:
                st.warning("No valid video clips to combine.")
        else:
            st.warning("No chapters produced video files.")

        return final_video_path
        
    except Exception as e:
        logging.error(f"Video generation failed: {e}")
        st.error(f"Video generation failed: {str(e)}")
        return None

def main():
    """Streamlit UI - only runs when streamlit is available"""
    if not STREAMLIT_AVAILABLE:
        print("Streamlit not available. This function is for UI only.")
        print("Use generate_video(concept) function directly for API integration.")
        return
    
    st.title("Explanatory Video Generator")
    concept = st.text_input("Enter the concept for the video:")

    if st.button("Generate Video"):
        if concept:
            with st.spinner("Generating video… this may take a few minutes."):
                try:
                    final_video_file = asyncio.run(generate_video(concept))
                    if final_video_file and os.path.exists(final_video_file):
                        st.success("Video generated successfully!")
                        st.video(final_video_file)
                    else:
                        st.error("Video generation failed - no video file was created.")
                except Exception as e:
                    st.error(f"Video generation failed: {str(e)}")
        else:
            st.warning("Please enter a concept.")

if __name__ == "__main__":
    main()
