from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= os.getenv("API_KEY"),
)

def send_prompt(prompt_array):
    try:
        completion = client.chat.completions.create(
        extra_body={},
        model="google/gemini-2.0-flash-exp:free",
        messages=prompt_array
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("Error fetching response:", e)
        return None