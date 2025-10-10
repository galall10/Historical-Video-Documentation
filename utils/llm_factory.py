"""
LLM factory for initializing Gemini model
"""
from langchain_google_genai import ChatGoogleGenerativeAI
import config


def initialize_llm():
    """
    Initialize and return a Gemini LLM instance.
    Ensures the Gemini API key is loaded and provides safe initialization.
    """
    if not config.GEMINI_API_KEY:
        raise EnvironmentError("❌ GEMINI_API_KEY is missing. Please set it in your .env file.")

    try:
        llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.5,
            convert_system_message_to_human=True
        )
        print(f"✅ Gemini model '{config.GEMINI_MODEL}' initialized successfully.")
        return llm
    except Exception as e:
        raise RuntimeError(f"❌ Failed to initialize Gemini LLM: {e}")
