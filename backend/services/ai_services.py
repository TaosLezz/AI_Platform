import asyncio
import time
from typing import Dict, List, Any, Optional
import openai
import os
from openai import AsyncOpenAI
from together import Together
import requests
from dotenv import load_dotenv
import traceback
import base64
load_dotenv()

class AIServiceManager:
    """Manages all AI services including OpenAI and Hugging Face integrations"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        )
        self.together_client = Together(
            api_key=os.getenv("TOGETHER_API_KEY")
        )
        self.hf_token = os.getenv("HF_API_KEY")
        
    
    def check_openai_connection(self) -> bool:
        """Check if OpenAI API is accessible"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            return bool(api_key and api_key != "your-openai-api-key")
        except Exception:
            return False

    async def generate_image(self, prompt: str, parameters: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Generate images using OpenAI DALL-E"""
        start_time = time.time()
        print("para", parameters)
        print("p1", parameters.get("steps", 4))
        print("p2", parameters.get("resolution", "1024x1024"))
        print("p3", parameters.get("quality", "standard"))
        print("p4", parameters.get("style", "action"))
        size_str = parameters.get("resolution", "1024x1024")
        width_str, height_str = size_str.split("x")
        style=parameters.get("style", "anime")
        try:
            response = self.together_client.images.generate(
                model="black-forest-labs/FLUX.1-schnell-Free",
                prompt=f"{prompt}, in {style} style",
                n=1,
                steps=parameters.get("steps", 4),
                width = int(width_str),
                height = int(height_str),
                quality=parameters.get("quality", "standard"),
                
            )
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": {
                    "url": response.data,
                    "prompt": prompt
                },
                "processing_time": processing_time
            }
            
        except Exception as e:
            print("error", e)
            traceback.print_exc()
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}",
                "processing_time": processing_time
            }

    async def classify_image(self, base64_image: str, use_hugging_face: bool = False) -> Dict[str, Any]:
        """Classify images using OpenAI Vision or Hugging Face models"""
        start_time = time.time()
        
        try:
            if use_hugging_face:
                # Hugging Face classification (placeholder with realistic responses)
                await asyncio.sleep(0.5)  # Simulate processing time
                API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
                # result = {
                #     "class": "mountain landscape",
                #     "confidence": 0.92,
                #     "description": "A scenic mountain landscape with natural features",
                #     "alternatives": [
                #         {"label": "nature scene", "score": 0.87},
                #         {"label": "outdoor landscape", "score": 0.83},
                #         {"label": "scenic view", "score": 0.79}
                #     ]
                # }
            else:
                # # OpenAI Vision classification
                # response = await self.together_client.chat.completions.create(
                #     model="gpt-4o",
                #     messages=[
                #         {
                #             "role": "system",
                #             "content": "You are an expert image classifier. Analyze the image and classify it into a specific category. Provide a confidence score between 0 and 1, and a brief description. Respond with JSON in this format: { 'class': string, 'confidence': number, 'description': string }"
                #         },
                #         {
                #             "role": "user",
                #             "content": [
                #                 {
                #                     "type": "text",
                #                     "text": "Classify this image and provide confidence score and description."
                #                 },
                #                 {
                #                     "type": "image_url",
                #                     "image_url": {
                #                         "url": f"data:image/jpeg;base64,{base64_image}"
                #                     }
                #                 }
                #             ]
                #         }
                #     ],
                #     response_format={"type": "json_object"}
                # )
                
                # import json
                # result = json.loads(response.choices[0].message.content)
                # result = {
                #     "class": result.get("class", "Unknown"),
                #     "confidence": max(0, min(1, result.get("confidence", 0))),
                #     "description": result.get("description", "No description available")
                # }
                API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": f"Image classification failed: {str(e)}",
                "processing_time": processing_time
            }

    async def detect_objects(self, base64_image: str, use_hugging_face: bool = False) -> Dict[str, Any]:
        """Detect objects in images using OpenAI Vision or YOLO models"""
        start_time = time.time()
        
        try:
            if use_hugging_face:
                # result = {
                #     "objects": [
                #         {"name": "car", "confidence": 0.92, "bbox": [25, 30, 40, 35]},
                #         {"name": "person", "confidence": 0.88, "bbox": [60, 20, 25, 45]},
                #         {"name": "building", "confidence": 0.85, "bbox": [10, 5, 50, 60]}
                #     ]
                # }
                # Hugging Face object detection (placeholder with realistic responses)
                await asyncio.sleep(1.0)  # Simulate processing time
                API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
            else:
                # OpenAI Vision object detection
                # response = await self.together_client.chat.completions.create(
                #     model="gpt-4o",
                #     messages=[
                #         {
                #             "role": "system",
                #             "content": "You are an expert object detection system. Analyze the image and detect all objects present. For each object, provide the name, confidence score (0-1), and approximate bounding box coordinates as [x, y, width, height] in percentage of image dimensions. Respond with JSON in this format: { 'objects': [{ 'name': string, 'confidence': number, 'bbox': [number, number, number, number] }] }"
                #         },
                #         {
                #             "role": "user",
                #             "content": [
                #                 {
                #                     "type": "text",
                #                     "text": "Detect and locate all objects in this image with bounding boxes."
                #                 },
                #                 {
                #                     "type": "image_url",
                #                     "image_url": {
                #                         "url": f"data:image/jpeg;base64,{base64_image}"
                #                     }
                #                 }
                #             ]
                #         }
                #     ],
                #     response_format={"type": "json_object"}
                # )
                
                # import json
                # result = json.loads(response.choices[0].message.content)
                await asyncio.sleep(0.5)  # Simulate processing time
                API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": f"Object detection failed: {str(e)}",
                "processing_time": processing_time
            }

    async def segment_image(self, base64_image: str, use_hugging_face: bool = False) -> Dict[str, Any]:
        """Perform image segmentation using OpenAI Vision or SAM models"""
        start_time = time.time()
        
        try:
            if use_hugging_face:
                # Hugging Face segmentation (placeholder with realistic responses)
                await asyncio.sleep(1.0)  # Simulate processing time
                # result = {
                #     "segments": [
                #         {"name": "background", "mask": "polygon(0% 0%, 100% 0%, 100% 40%, 0% 40%)", "confidence": 0.95},
                #         {"name": "foreground object", "mask": "polygon(20% 40%, 80% 40%, 80% 80%, 20% 80%)", "confidence": 0.91},
                #         {"name": "secondary object", "mask": "polygon(60% 20%, 90% 20%, 90% 50%, 60% 50%)", "confidence": 0.87}
                #     ]
                # }
                API_URL = "https://api-inference.huggingface.co/models/facebook/mask2former-swin-large-coco-panoptic"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
            else:
                # OpenAI Vision segmentation
                # response = await self.together_client.chat.completions.create(
                #     model="gpt-4o",
                #     messages=[
                #         {
                #             "role": "system",
                #             "content": "You are an expert image segmentation system. Analyze the image and identify distinct segments/regions. For each segment, provide a name, confidence score (0-1), and a description of the mask area. Respond with JSON in this format: { 'segments': [{ 'name': string, 'mask': string, 'confidence': number }] }"
                #         },
                #         {
                #             "role": "user",
                #             "content": [
                #                 {
                #                     "type": "text",
                #                     "text": "Segment this image into distinct regions and describe each segment."
                #                 },
                #                 {
                #                     "type": "image_url",
                #                     "image_url": {
                #                         "url": f"data:image/jpeg;base64,{base64_image}"
                #                     }
                #                 }
                #             ]
                #         }
                #     ],
                #     response_format={"type": "json_object"}
                # )
                
                # import json
                # result = json.loads(response.choices[0].message.content)
                API_URL = "https://api-inference.huggingface.co/models/facebook/mask2former-swin-large-coco-panoptic"
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(",")[1]
                image_bytes = base64.b64decode(base64_image)

                response = requests.post(API_URL, headers={"Content-Type": "image/jpeg", **headers}, data=image_bytes)
                result = response.json()
                # print("result segmen", result)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": f"Image segmentation failed: {str(e)}",
                "processing_time": processing_time
            }

    async def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate chat responses using OpenAI GPT models"""
        start_time = time.time()
        
        try:
            # Format messages for OpenAI API
            formatted_messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant specialized in computer vision and AI services. You help users understand and use various AI tools including image generation, classification, object detection, and segmentation. Provide helpful, accurate, and friendly responses."
                }
            ]
            
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            response = self.together_client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=formatted_messages,
                max_tokens=1000
            )
            # print("responsezz", response)
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": {
                    "response": response.choices[0].message.content
                },
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": f"Chat completion failed: {str(e)}",
                "processing_time": processing_time
            }