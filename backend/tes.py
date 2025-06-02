
# # import os
# # from together import Together
# # from dotenv import load_dotenv
# # load_dotenv()
# # client = Together(api_key=os.getenv("TOGETHER_API_KEY")) # auth defaults to os.environ.get("TOGETHER_API_KEY")

# # response = client.chat.completions.create(
# #     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
# #     messages=[
# #       {
# #         "role": "user",
# #         "content": "what is your name"
# #       }
# #     ]
# # )
# # print(response.choices[0].message.content)


# # import os
# # from together import Together
# # from dotenv import load_dotenv

# # # Load API key từ file .env
# # load_dotenv()
# # client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# # # Gọi API tạo ảnh
# # response = client.images.generate(
# #     model="black-forest-labs/FLUX.1-schnell-Free",
# #     prompt="a cat",
# #     n=1,
# #     steps=1,
# #     size="1024x1024",
# #     quality="standard"
# # )

# # # In ra kết quả
# # print("Ảnh đã tạo:")
# # for image in response.data:
# #     print("Image URL:", image.url)



# # import requests

# # API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
# # headers = {"Authorization": f"Bearer "}

# # with open(r"C:\Users\Tao Le\Downloads\cat.jpg", "rb") as f:
# #     data = f.read()

# # response = requests.post(API_URL, headers=headers, data=data)
# # print(response.json())

# import requests
# import os
# API_URL = "https://router.huggingface.co/hf-inference/models/google/vit-base-patch16-224"
# headers = {
#     "Authorization": "Bearer ",
# }

# # def query(filename):
# #     with open(filename, "rb") as f:
# #         data = f.read()
# #     response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=data)
# #     return response.json()

# # output = query(r"C:\Users\Tao Le\Downloads\cat.jpg")
# # print(output)
# with open(r"C:\Users\Tao Le\Downloads\cat.jpg", "rb") as f:
#     data = f.read()

# result = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=data)
# print("resultzzz", result.json())
raw_objects = [{'score': 0.5076082348823547, 'label': 'cat', 'box': {'xmin': 177, 'ymin': 57, 'xmax': 1021, 'ymax': 1020}}, {'score': 0.9936797618865967, 'label': 'cat', 'box': {'xmin': 276, 'ymin': 67, 'xmax': 1023, 'ymax': 1018}}]
mapped_objects = []
for obj in raw_objects:
    mapped_objects.append({
        "name": obj["label"],
        "confidence": obj["score"],
        "bbox": [
            int(obj["box"]["xmin"]),
            int(obj["box"]["ymin"]),
            int(obj["box"]["xmax"]),
            int(obj["box"]["ymax"]),
        ],
    })
from PIL import Image, ImageDraw, ImageFont

# Mở ảnh gốc
image = Image.open(r"C:\Users\Tao Le\Downloads\cat.jpg")
draw = ImageDraw.Draw(image)

# Vẽ từng bounding box
for obj in mapped_objects:
    label = f"{obj['name']} ({obj['confidence']:.2f})"
    xmin, ymin, xmax, ymax = obj["bbox"]
    
    draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=3)
    draw.text((xmin, ymin - 10), label, fill="red")

# Hiển thị ảnh
image.show()