import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# Model configurations
GEMINI_MODEL = "gemini-2.0-flash"
WAN_MODEL = "wan2.1-t2v-turbo"


def validate_config():
    """Check for valid API keys and print configuration summary."""
    has_keys = any([GEMINI_API_KEY, DASHSCOPE_API_KEY])

    print("\nConfiguration Summary:")
    print("----------------------")

    if not has_keys:
        print("Warning: No valid API keys found. Update your .env file.")
        return False

    return True


validate_config()
