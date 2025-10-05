import base64
import requests
import json
from pathlib import Path

class ImageStoryGenerator:
   

    def _init_(self, model_choice="gemini"):
        """
        Initialize the generator

        Args:
            model_choice: "gemini" or "qwen"
        """
        self.model_choice = model_choice.lower()

    def encode_image(self, image_path):
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_with_gemini(self, image_path, api_key):
        """
        Generate story using Google Gemini (Free tier available)

        Get your free API key from: https://makersuite.google.com/app/apikey
        """
        base64_image = self.encode_image(image_path)

        # Determine image mime type
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": "Create an engaging, creative story based on this image. Describe what you see and weave it into a narrative with characters, plot, and emotion. Make it vivid and immersive."
                    },
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }]
        }

        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            story = result['candidates'][0]['content']['parts'][0]['text']
            return story
        else:
            raise Exception(f"Gemini API Error: {response.status_code} - {response.text}")

    def generate_with_qwen(self, image_path, api_key):

        base64_image = self.encode_image(image_path)

        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-vl-plus",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": f"data:image/jpeg;base64,{base64_image}"
                            },
                            {
                                "text": "Create an engaging, creative story based on this image. Describe what you see and weave it into a narrative with characters, plot, and emotion. Make it vivid and immersive."
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            story = result['output']['choices'][0]['message']['content'][0]['text']
            return story
        else:
            raise Exception(f"Qwen API Error: {response.status_code} - {response.text}")

    def generate_story(self, image_path, api_key):
        """Generate story using the selected model"""
        if self.model_choice == "gemini":
            return self.generate_with_gemini(image_path, api_key)
        elif self.model_choice == "qwen":
            return self.generate_with_qwen(image_path, api_key)
        else:
            raise ValueError("Invalid model choice. Use 'gemini' or 'qwen'")
