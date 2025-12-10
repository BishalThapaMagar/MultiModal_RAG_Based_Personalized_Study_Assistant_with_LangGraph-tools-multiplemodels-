import os
from dotenv import load_dotenv
from perplexity import Perplexity

load_dotenv()

client = Perplexity(api_key=os.getenv("PERPLEXITY_API_KEY"))

def call_perplexity_chat(prompt: str, model: str = "sonar-pro") -> str:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error (Perplexity Chat): {str(e)}"


def call_perplexity_search(query: str, max_results: int = 3):
    try:
        search = client.search.create(query=query, max_results=max_results)
        return [{"title": r.title, "url": r.url} for r in search.results]
    except Exception as e:
        return {"error": f"Error (Perplexity Search): {str(e)}"}

