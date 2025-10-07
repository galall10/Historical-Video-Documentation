"""
Configuration settings for the Historical Building Video Story Generator
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === API KEYS ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")  # For Wan video generation
WAN_API_KEY = os.getenv("WAN_API_KEY", "")  # Optional, if some endpoints require it

# === MODEL CONFIGURATIONS ===
GEMINI_MODEL = "gemini-2.0-flash-exp"
OPENROUTER_MODEL = "meta-llama/llama-4-maverick:free"
WAN_MODEL = "wan2.5-t2v-preview"  # DashScope video model

# === APP BEHAVIOR FLAGS ===
USE_WAN = True           # Enable Wan text-to-video generation
USE_GEMINI = True        # Enable Gemini for narration and script generation
USE_OPENROUTER = False   # Optional fallback for LLM text generation

# === PROCESSING PARAMETERS ===
MAX_ITERATIONS = 2

# === VALIDATION ===
def validate_config():
    """Check that at least one key is active and print model setup summary."""
    ok = True

    print("=" * 60)
    print("🔧 CONFIGURATION SUMMARY")
    print("=" * 60)

    if not GEMINI_API_KEY and not OPENROUTER_API_KEY and not DASHSCOPE_API_KEY:
        print("⚠️  WARNING: No valid API keys detected!")
        print("Please set GEMINI_API_KEY, OPENROUTER_API_KEY, or DASHSCOPE_API_KEY in your .env file.")
        ok = False

    # Display model settings
    if USE_WAN:
        print(f"🎬 Wan model enabled: {WAN_MODEL}")
    if USE_GEMINI:
        print(f"⚙️  Gemini model:      {GEMINI_MODEL}")
    if USE_OPENROUTER:
        print(f"💬 OpenRouter model:   {OPENROUTER_MODEL}")

    print(f"🔁 Max Iterations:     {MAX_ITERATIONS}")
    print("=" * 60)

    return ok


# Run validation when the file loads
validate_config()
