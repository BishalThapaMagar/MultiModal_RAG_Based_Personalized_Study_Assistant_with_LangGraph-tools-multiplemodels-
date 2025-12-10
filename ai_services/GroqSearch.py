"""
Groq Web Search Service
Provides web search capabilities using Groq's compound model
"""
import os
from groq import Groq
from typing import Dict
from logging_config import get_logger

logger = get_logger(__name__)

def groq_web_search(prompt: str, model: str = "groq/compound", exclude_domains: list = None) -> Dict:
    """
    Perform web search using Groq's compound model
    
    Args:
        prompt: Search query/prompt
        model: Groq model to use (default: groq/compound for web search)
        exclude_domains: List of domains to exclude from search
        
    Returns:
        dict with search answer and metadata
    """
    try:
        logger.info(f"🔍 Groq Web Search - Prompt: '{prompt[:50]}...', Model: {model}")
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("❌ GROQ_API_KEY not found in environment")
            return {
                "success": False,
                "error": "Groq API key not configured",
                "answer": ""
            }
        
        # Initialize client
        client = Groq(api_key=api_key)
        
        # Prepare search settings
        search_settings = {}
        if exclude_domains:
            search_settings["exclude_domains"] = exclude_domains
        
        # Create completion with web search
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            # Add search settings if provided
            **({"search_settings": search_settings} if search_settings else {})
        )
        
        # Extract answer
        answer = response.choices[0].message.content
        
        logger.info(f"✅ Groq Web Search completed - Answer length: {len(answer)} chars")
        
        return {
            "success": True,
            "prompt": prompt,
            "answer": answer,
            "model": model
        }
        
    except Exception as e:
        logger.error(f"❌ Groq Web Search Error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "answer": f"Error performing Groq web search: {str(e)}"
        }


def groq_web_search_stream(prompt: str, model: str = "groq/compound"):
    """
    Perform streaming web search using Groq's compound model
    
    Args:
        prompt: Search query/prompt
        model: Groq model to use
        
    Yields:
        Token chunks from the streaming response
    """
    try:
        logger.info(f"🔍🌊 Groq Web Search Stream - Prompt: '{prompt[:50]}...'")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            yield {"error": "Groq API key not configured"}
            return
        
        client = Groq(api_key=api_key)
        
        # Create streaming completion
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        token_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                token_count += 1
                yield token
        
        logger.info(f"✅ Groq Web Search Stream completed - {token_count} tokens")
        
    except Exception as e:
        logger.error(f"❌ Groq Web Search Stream Error: {str(e)}", exc_info=True)
        yield f"\nError: {str(e)}"


# Test function
if __name__ == "__main__":
    prompt = "What are the most important AI model releases this week?"
    result = groq_web_search(prompt)
    
    print(f"\n{'='*60}")
    print(f"Groq Web Search Result")
    print(f"{'='*60}\n")
    
    if result["success"]:
        print(f"Prompt: {result['prompt']}")
        print(f"Model: {result['model']}")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"Error: {result['error']}")

