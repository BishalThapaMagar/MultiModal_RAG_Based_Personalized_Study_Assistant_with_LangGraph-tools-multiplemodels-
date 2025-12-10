
import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# === 1. CHAT / COMPLETION ===
def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    try:
        resp = client.models.generate_content(model=model, contents=prompt)
        return resp.text
    except Exception as e:
        return f"Error (Chat): {str(e)}"


# === 2. IMAGE GENERATION (Using Imagen 4.0) ===
def gemini_image_gen(prompt: str, num_images: int = 1) -> str:
    try:
        print(f"🎨 Attempting to generate {num_images} image(s) with Imagen 4.0...")
        print(f"📝 Prompt: {prompt}")
        
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=num_images,
            )
        )
        
        print(f"✅ API Response received")
        
        # Save all generated images
        saved_files = []
        for i, generated_image in enumerate(response.generated_images):
            file_path = f"generated_image_{i+1}.png"
            # Convert PIL image to bytes and save
            generated_image.image.save(file_path)
            saved_files.append(file_path)
            print(f"💾 Saved: {file_path}")
        
        return f"Successfully generated {len(saved_files)} image(s): {', '.join(saved_files)}"
    except AttributeError as e:
        error_msg = f"API method not available: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error (Image Gen): {error_msg}. Note: Imagen API might not be available in your current plan."
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error (Image Gen): {error_msg}"


# === 3. IMAGE UNDERSTANDING ===
def gemini_image_understand(image_path: str, task_prompt: str = "Describe this image") -> str:
    try:
        # Detect image format from file extension
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            mime_type = "image/jpeg"
        elif image_path.lower().endswith('.png'):
            mime_type = "image/png"
        elif image_path.lower().endswith('.webp'):
            mime_type = "image/webp"
        elif image_path.lower().endswith('.gif'):
            mime_type = "image/gif"
        else:
            mime_type = "image/png"  # Default
        
        with open(image_path, "rb") as f:
            img_data = f.read()
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [
                {"inline_data": {"mime_type": mime_type, "data": img_data}},
                {"text": task_prompt}
            ]}]
        )
        return resp.text
    except Exception as e:
        return f"Error (Image Understand): {str(e)}"


# === 4. WEB SEARCH / GROUNDING (Using Google Search Retrieval) ===
def gemini_search(query: str) -> str:
    try:
        # Configure Google Search grounding tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=config,
        )
        
        return response.text
    except Exception as e:
        return f"Error (Search): {str(e)}"



# === 5. AUDIO TRANSCRIPTION ===
def gemini_transcribe(audio_path: str) -> str:
    try:
        # Detect audio format from file extension
        if audio_path.lower().endswith('.mp3'):
            mime_type = "audio/mp3"
        elif audio_path.lower().endswith('.wav'):
            mime_type = "audio/wav"
        elif audio_path.lower().endswith('.m4a'):
            mime_type = "audio/mp4"
        else:
            mime_type = "audio/wav"  # Default
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [
                {"inline_data": {"mime_type": mime_type, "data": audio_data}},
                {"text": "Transcribe this audio."}
            ]}]
        )
        return resp.text
    except Exception as e:
        return f"Error (Audio): {str(e)}"


# === 6. VIDEO DESCRIPTION ===
def gemini_video_describe(video_path: str) -> str:
    try:
        with open(video_path, "rb") as f:
            video_data = f.read()
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [
                {"inline_data": {"mime_type": "video/mp4", "data": video_data}},
                {"text": "Describe this video briefly."}
            ]}]
        )
        return resp.text
    except Exception as e:
        return f"Error (Video): {str(e)}"
