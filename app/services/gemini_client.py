import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.3-70b-versatile"


def generate_response(prompt: str) -> str:

    try:

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL_NAME,
            temperature=0.3,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print("Groq Error:", str(e))
        return "AI service temporarily unavailable."