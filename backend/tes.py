
import os
from together import Together
from dotenv import load_dotenv
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY")) # auth defaults to os.environ.get("TOGETHER_API_KEY")

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    messages=[
      {
        "role": "user",
        "content": "what is your name"
      }
    ]
)
print(response.choices[0].message.content)