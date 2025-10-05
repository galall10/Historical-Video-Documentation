"""
Configuration settings for the Historical Building Video Story Generator
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model Configuration
OPENROUTER_MODEL = "meta-llama/llama-4-maverick:free"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Workflow Settings
MAX_ITERATIONS = 2

# Validation
def validate_config():
    """Validate that at least one API key is configured"""
    if not GEMINI_API_KEY and not OPENROUTER_API_KEY:
        print("⚠️ WARNING: No API keys configured!")
        print("Please set either GEMINI_API_KEY or OPENROUTER_API_KEY in your .env file")
        return False
    return True

# Run validation on import
validate_config()