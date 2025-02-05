import os
from abc import ABC, abstractmethod
from PIL import Image
from openai import OpenAI
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import base64
from io import BytesIO

class LLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key, **kwargs):
        pass
    
    @abstractmethod
    def get_chat_response(self, prompt, model):
        pass
    
    @abstractmethod
    def get_vision_chat_response(self, prompt, image, model):
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, **kwargs):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.aiproxy.io/v1"
        )
    
    def get_chat_response(self, prompt, model):
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
        )
        return chat_completion.choices[0].message.content
    
    def get_vision_chat_response(self, prompt, image, model):
        encoded_image = self.encode_image_base64(image)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return chat_completion.choices[0].message.content
    
    def encode_image_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
class GeminiProvider(LLMProvider):
    def __init__(self, api_key, **kwargs):
        # Initialize Vertex AI
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{current_dir}/vertex-ai.json"
        
        vertexai.init(project="quick-formula-414701", location="us-central1")
        self.text_model = GenerativeModel("gemini-1.5-flash-001")
        self.vision_model = GenerativeModel("gemini-1.5-flash-001")
        
        # Define safety settings
        self.safety_settings = [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, 
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
            ),
        ]
        
        self.generation_config = {
            "max_output_tokens": 4096,
        }
    
    def get_chat_response(self, prompt, model):
        try:
            response = self.text_model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                if response.candidates[0].finish_reason == "SAFETY":
                    print("Response was blocked by safety filters.")
                    return "Response blocked by safety filters"
                return response.text.strip("\n")
            return "No valid response received"
            
        except Exception as e:
            print(f"Error in get_chat_response: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_vision_chat_response(self, prompt, image, model):
        try:
            # Convert PIL Image to bytes using our helper method
            image_bytes = self._convert_image_to_bytes(image)
            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            response = self.vision_model.generate_content(
                [image_part, prompt],
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                if response.candidates[0].finish_reason == "SAFETY":
                    print("Response was blocked by safety filters.")
                    return "Response blocked by safety filters"
                return response.text.strip("\n")
            return "No valid response received"
            
        except Exception as e:
            print(f"Error in get_vision_chat_response: {str(e)}")
            return f"Error: {str(e)}"
    
    def _convert_image_to_bytes(self, image):
        """Convert PIL Image to bytes"""
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()