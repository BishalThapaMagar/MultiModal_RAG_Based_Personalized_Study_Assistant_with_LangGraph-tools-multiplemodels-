"""
Perplexity Web Search Service
Provides web search capabilities using Perplexity API

Supported Models:
- sonar: Standard for general queries (default)
- sonar-pro: For more complex queries
- sonar-reasoning: For complex analytical tasks
"""
import os
from typing import List, Dict

# Try to import logger, fallback to print for standalone testing
try:
    from logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

def perplexity_web_search(query: str, max_results: int = 5) -> Dict:
    """
    Perform web search using Perplexity API
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        dict with search results and metadata
    """
    try:
        logger.info(f"🔍 Perplexity Search - Query: '{query}', Max Results: {max_results}")
        
        # Import Perplexity client
        try:
            from perplexity import Perplexity
        except ImportError:
            logger.error("❌ Perplexity package not installed. Run: pip install perplexity-sdk")
            return {
                "success": False,
                "error": "Perplexity package not installed",
                "results": []
            }
        
        # Initialize client
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("❌ PERPLEXITY_API_KEY not found in environment")
            return {
                "success": False,
                "error": "Perplexity API key not configured",
                "results": []
            }
        
        client = Perplexity(api_key=api_key)
        
        # Perform search
        search = client.search.create(
            query=query,
            max_results=max_results
        )
        
        # Format results
        results = []
        for result in search.results:
            results.append({
                "title": result.title,
                "url": result.url,
                "snippet": getattr(result, 'snippet', ''),
            })
        
        logger.info(f"✅ Perplexity Search completed - Found {len(results)} results")
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"❌ Perplexity Search Error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


def perplexity_search_and_answer(query: str, model: str = "sonar") -> str:
    """
    Use Perplexity's Sonar models for web-grounded AI responses
    
    Args:
        query: Search query
        model: Perplexity model to use:
            - "sonar" (default): Standard for general queries
            - "sonar-pro": For more complex queries
            - "sonar-reasoning": For complex analytical tasks
        
    Returns:
        AI-generated answer with web search context
    """
    try:
        logger.info(f"🔍💬 Perplexity {model.upper()} - Query: '{query}'")
        
        # Use Perplexity's Sonar models (built-in web search)
        from perplexity import Perplexity
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.error("❌ PERPLEXITY_API_KEY not found in environment")
            return "Perplexity API key not configured"
        
        client = Perplexity(api_key=api_key)
        
        # Validate model choice
        valid_models = ["sonar", "sonar-pro", "sonar-reasoning"]
        if model not in valid_models:
            logger.warning(f"⚠️ Invalid model '{model}', using 'sonar' as default")
            model = "sonar"
        
        # Use Sonar model (automatically includes web search)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        
        answer = response.choices[0].message.content
        logger.info(f"✅ Perplexity {model.upper()} completed")
        
        return answer
        
    except Exception as e:
        logger.error(f"❌ Perplexity Error: {str(e)}", exc_info=True)
        # Return generic error (never expose internal details)
        return "I encountered an error while searching. Please try again."


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "="*60)
    print("Testing Perplexity Sonar Models")
    print("="*60 + "\n")
    
    query = "What are the latest AI developments this week?"
    
    # Test standard sonar
    print("1. Testing SONAR (standard):")
    print("-" * 60)
    answer = perplexity_search_and_answer(query, model="sonar")
    print(answer)
    print()
    
    # Test sonar-pro
    print("\n2. Testing SONAR-PRO (complex queries):")
    print("-" * 60)
    complex_query = "Analyze the economic implications of recent AI model releases"
    answer = perplexity_search_and_answer(complex_query, model="sonar-pro")
    print(answer)
    print()
    
    # Test sonar-reasoning
    print("\n3. Testing SONAR-REASONING (analytical):")
    print("-" * 60)
    reasoning_query = "Compare and contrast the capabilities of GPT-4, Claude, and Gemini step by step"
    answer = perplexity_search_and_answer(reasoning_query, model="sonar-reasoning")
    print(answer)

