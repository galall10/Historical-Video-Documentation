import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")

# Model configurations
GEMINI_MODEL = "gemini-2.0-flash"
OPENROUTER_MODEL = "meta-llama/llama-4-maverick:free"
WAN_MODEL = "wan2.5-t2v"  # stable release, not preview

# Feature flags
USE_WAN = True          # Enable Wan for text-to-video generation
USE_GEMINI = True       # Enable Gemini for narration and text generation
USE_OPENROUTER = False  # Optional fallback for text generation

# Processing parameters
MAX_ITERATIONS = 2


def validate_config():
    """Check for valid API keys and print configuration summary."""
    has_keys = any([GEMINI_API_KEY, OPENROUTER_API_KEY, DASHSCOPE_API_KEY])

    print("\nConfiguration Summary:")
    print("----------------------")

    if not has_keys:
        print("Warning: No valid API keys found. Update your .env file.")
        return False

    if USE_WAN:
        print(f"Wan model:      {WAN_MODEL}")
    if USE_GEMINI:
        print(f"Gemini model:   {GEMINI_MODEL}")
    if USE_OPENROUTER:
        print(f"OpenRouter:     {OPENROUTER_MODEL}")

    print(f"Max iterations: {MAX_ITERATIONS}\n")
    return True


validate_config()
