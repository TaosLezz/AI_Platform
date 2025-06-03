import requests

with open(r"C:\Users\Lenovo\Downloads\anh-con-meo-cute.jpg", "rb") as f:
    files = {"image": (r"C:\Users\Lenovo\Downloads\anh-con-meo-cute.jpg", f, "image/jpeg")}
    data = {"useHuggingFace": "false"}  # hoặc true nếu muốn dùng mô hình HuggingFace
    res = requests.post("http://localhost:8000/api/v1/segment", files=files, data=data)

response_json = res.json()
# print(response_json)
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt

segments = response_json["segments"]
for i, seg in enumerate(segments):
    print(f"Label: {seg['name']} - Confidence: {seg['confidence']:.2f}")

    # Decode base64 mask
    mask_data = base64.b64decode(seg["mask"])
    mask_image = Image.open(io.BytesIO(mask_data))

    # Hiển thị mask
    plt.imshow(mask_image, cmap="gray")
    plt.title(f"Mask {i+1}: {seg['name']}")
    plt.axis("off")
    plt.show()

