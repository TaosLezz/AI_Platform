
# import os
# from together import Together
# from dotenv import load_dotenv
# load_dotenv()
# client = Together(api_key=os.getenv("TOGETHER_API_KEY")) # auth defaults to os.environ.get("TOGETHER_API_KEY")

# response = client.chat.completions.create(
#     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
#     messages=[
#       {
#         "role": "user",
#         "content": "what is your name"
#       }
#     ]
# )
# print(response.choices[0].message.content)


import os
from together import Together
from dotenv import load_dotenv

# Load API key từ file .env
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Gọi API tạo ảnh
response = client.images.generate(
    model="black-forest-labs/FLUX.1-schnell-Free",
    prompt="a cat",
    n=1,
    steps=1,
    size="1024x1024",
    quality="standard"
)

# In ra kết quả
print("Ảnh đã tạo:")
for image in response.data:
    print("Image URL:", image.url)
