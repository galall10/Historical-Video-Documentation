import base64
import io
from PIL import Image


def image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to a base64 string (no data URI prefix)."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def pil_to_base64_data_uri(image: Image.Image) -> str:
    """Convert a PIL image to a full data URI (with 'data:image/png;base64,' prefix)."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"
