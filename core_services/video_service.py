"""
Video Generation Service
Wrapper around the working Manim video generation function
"""
import os
import sys
from pathlib import Path
from typing import Dict
import shutil

# Add Manim app directory to path
current_dir = Path(__file__).parent.parent
manim_dir = current_dir / "ManimLibraryVideoGenAI"
sys.path.insert(0, str(manim_dir))

# Try to import logger
try:
    from logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import the working video generation function
try:
    from app import generate_video
    logger.info("✅ Successfully imported generate_video function")
except ImportError as e:
    logger.error(f"❌ Failed to import generate_video: {e}", exc_info=True)
    logger.error(f"Make sure you're in ai_backend directory and Manim dependencies are installed")
    generate_video = None
except Exception as e:
    logger.error(f"❌ Unexpected error importing generate_video: {e}", exc_info=True)
    generate_video = None


async def generate_educational_video(concept: str, model_provider: str = "gemini") -> Dict:
    """
    Generate an educational video explaining a concept
    
    Args:
        concept: The topic/concept to explain
        model_provider: AI model to use (gemini only)
        
    Returns:
        dict with success status, video path, and metadata
    """
    try:
        if generate_video is None:
            logger.error("❌ generate_video function is None - import failed!")
            logger.error(f"Check logs above for import errors. Manim directory: {manim_dir}")
            raise ImportError("Video generation function not available. Check if Manim dependencies are installed.")
            
        logger.info(f"🎬 Starting video generation for: {concept}")
        
        # Call the working function
        final_video_path = await generate_video(concept)
        
        if final_video_path and os.path.exists(final_video_path):
            # Convert to absolute path if it's relative
            if not os.path.isabs(final_video_path):
                final_video_path = os.path.abspath(final_video_path)
            
            # Create outputs directory
            output_dir = Path("outputs/videos")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy to outputs
            new_filename = f"{concept.replace(' ', '_')[:50]}_final.mp4"
            new_path = output_dir / new_filename
            shutil.copy(final_video_path, new_path)
            
            logger.info(f"✅ Video generated: {new_path}")
            
            return {
                "success": True,
                "video_path": str(new_path),
                "filename": new_path.name,
                "download_url": f"/download/{new_path.name}",
                "title": concept,
                "chapters": 3,
                "duration": 0,
                "model_used": model_provider,
                "message": "Video generated successfully"
            }
        else:
            logger.error("❌ Video generation failed - no file returned")
            return {
                "success": False,
                "message": "Video generation encountered an error. Please try again.",
                "model_used": model_provider
            }
        
    except Exception as e:
        logger.error(f"❌ Video generation failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": "Video generation encountered an error. Please try again.",
            "model_used": model_provider
        }
