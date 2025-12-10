import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
groq_pro_client = Groq(api_key=os.getenv("GROQ_API_PRO"))

def generate_completion(prompt: str, system_message: str = "You are a helpful assistant.", model: str = "llama-3.3-70b-versatile") -> str:
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error (Groq Free): {str(e)}"


def generate_completion_paid(prompt: str, system_message: str = "You are a helpful assistant.", model: str = "mixtral-8x7b") -> str:
    try:
        chat_completion = groq_pro_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error (Groq Paid): {str(e)}"

# Test the function if run directly
if __name__ == "__main__":
    result = generate_completion("Explain the importance of fast language models")
    resultpaid=generate_completion_paid("Explain the importance of fastapi")
    print(result)