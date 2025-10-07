"""
Configuration settings for the Historical Building Video Story Generator
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# === API Keys ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")   # Optional — some endpoints may not require it

# === Model Configuration ===
OPENROUTER_MODEL = "meta-llama/llama-4-maverick:free"
GEMINI_MODEL = "gemini-2.0-flash-exp"
WAN_MODEL = "Wan-AI/Wan2.1"   # Free text-to-video model on Hugging Face

# === Workflow Settings ===
MAX_ITERATIONS = 2

# === Execution Modes ===
USE_WAN = True   # Set True to enable Wan for text-to-video generation
USE_GEMINI = True
USE_OPENROUTER = False  # Optional fallback


# === Validation ===
def validate_config():
    """
    Validate that at least one API key or free model is configured properly.
    """
    ok = True

    if not GEMINI_API_KEY and not OPENROUTER_API_KEY and not WAN_API_KEY:
        print("⚠️ WARNING: No API keys configured!")
        print("Please set GEMINI_API_KEY, OPENROUTER_API_KEY, or WAN_API_KEY in your .env file.")
        ok = False

    if USE_WAN:
        print(f"🆓 Wan2.1 is enabled (model = {WAN_MODEL}) — free tier via Hugging Face.")
    if USE_GEMINI:
        print(f"⚙️ Gemini model set to: {GEMINI_MODEL}")
    if USE_OPENROUTER:
        print(f"💬 OpenRouter model set to: {OPENROUTER_MODEL}")

    return ok


# Run validation on import
validate_config()
