import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_KEY = GOOGLE_API_KEY or os.getenv("GEMINI_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
WAN_API_KEY = os.getenv("WAN_API_KEY", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Expose Google API key for genai client (required by google-genai SDK)
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash"
WAN_MODEL = "wan2.1-t2v-turbo"        # Alibaba DashScope
VEO_MODEL = "veo-2.0-generate-001"    # Google Veo

VIDEO_MODEL = VEO_MODEL


def validate_config():
    """Check for valid API keys and print configuration summary."""
    print("\n=== Configuration Summary ===")
    print("-----------------------------")

    keys_status = {
        "Google / Gemini API Key": bool(GOOGLE_API_KEY),
        "DashScope API Key": bool(DASHSCOPE_API_KEY),
        "WAN API Key": bool(WAN_API_KEY),
        "MongoDB URI": bool(MONGO_URI),
    }

    for key, exists in keys_status.items():
        print(f"{key}: {'Found' if exists else 'Missing'}")

    if not any(keys_status.values()):
        print("No valid API keys found — please update your .env file.")
        return False

    print(f"\nActive Video Model: {VIDEO_MODEL}")
    print(f"Active LLM Model: {GEMINI_MODEL}")
    print("-----------------------------\n")
    return True


# Validate configuration automatically
validate_config()
