"""
LLM factory for initializing Gemini model
"""
from langchain_google_genai import ChatGoogleGenerativeAI
import config


def initialize_llm():
    """Initialize and return a Gemini LLM instance."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    return ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.5,
        convert_system_message_to_human=True
    )
