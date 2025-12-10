import json
import re
import sys
from pathlib import Path

# Add ai_services to path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from ai_services.GroqClient import generate_completion

def call_llama(prompt: str) -> str:
    """Use GroqClient instead of local Ollama."""
    try:
        response = generate_completion(
            prompt, 
            "You are an expert educational content creator. Generate only valid JSON responses.",
            "llama-3.3-70b-versatile"
        )
        return response
    except Exception as e:
        print(f"❌ GroqClient error: {e}")
        return f"Error: {str(e)}"

def generate_flashcards(summary: str, chunks: list, full_text: str, num_cards=10):
    """Generate flashcards (front/back) as JSON objects."""
    prompt = f"""
    You are a flashcard generator expert.
    Create exactly {num_cards} high-quality educational flashcards to help students study and learn.
    Use the provided material (summary, chunks, and full text) to ensure accuracy and completeness.

    Rules:
    1. Each flashcard must have EXACTLY these fields: "front" and "back"
    2. "front": should be a clear, concise question, term, or prompt
    3. "back": should be the correct answer or detailed explanation
    4. Focus on key concepts, definitions, and important facts
    5. Make questions varied (definitions, explanations, examples, applications)
    6. Return ONLY a valid JSON array with no additional text or formatting

    Example format:
    [
      {{
        "front": "What is the capital of France?",
        "back": "Paris"
      }},
      {{
        "front": "Define Photosynthesis",
        "back": "Process by which green plants use sunlight to make food from CO2 and water, producing glucose and oxygen."
      }}
    ]

    ---
    Summary:
    {summary[:1000]}

    Additional Content:
    {str(chunks)[:2000] if chunks else "No additional chunks"}

    Full Text Sample:
    {full_text[:1500] if full_text else "No full text available"}
    """

    try:
        print(f"🃏 Generating {num_cards} flashcards...")
        raw_output = call_llama(prompt)
        print(f"📝 Raw output received: {raw_output[:200]}...")

        # Clean and extract JSON
        cleaned_output = raw_output.strip()
        
        # Remove markdown formatting if present
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        elif cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[3:]
        
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        
        cleaned_output = cleaned_output.strip()

        # Try to extract JSON array
        import re
        json_match = re.search(r'\[.*\]', cleaned_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            flashcards = json.loads(json_str)
            
            # Validate flashcard structure
            validated_flashcards = []
            for i, card in enumerate(flashcards):
                if isinstance(card, dict) and "front" in card and "back" in card:
                    validated_flashcards.append({
                        "front": str(card["front"]).strip(),
                        "back": str(card["back"]).strip()
                    })
                else:
                    print(f"⚠️ Invalid flashcard {i}: {card}")
            
            if validated_flashcards:
                print(f"✅ Generated {len(validated_flashcards)} valid flashcards")
                return validated_flashcards
            else:
                raise Exception("No valid flashcards found")
        else:
            raise Exception("No JSON array found in response")
            
    except Exception as e:
        print(f"❌ Flashcard generation error: {e}")
        print(f"📄 Raw output: {raw_output}")
        
        # Enhanced fallback with actual content
        fallback_cards = []
        
        # Try to create cards from summary
        if summary:
            summary_sentences = summary.split('. ')
            for i, sentence in enumerate(summary_sentences[:num_cards]):
                if len(sentence.strip()) > 10:
                    fallback_cards.append({
                        "front": f"What is the key point about: {sentence[:50]}...?",
                        "back": sentence.strip()
                    })
        
        # Fill remaining cards if needed
        while len(fallback_cards) < num_cards:
            fallback_cards.append({
                "front": f"Study Topic {len(fallback_cards) + 1}",
                "back": "Please refer to the original document for details."
            })
        
        return fallback_cards[:num_cards]
