"""
Image processing utilities
"""
import base64
import io
from PIL import Image

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string (without data URI prefix)"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def pil_to_base64_data_uri(image: Image.Image) -> str:
    """Convert PIL Image to base64 data URI (with data:image/png;base64, prefix)"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"