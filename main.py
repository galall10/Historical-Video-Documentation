"""
Main application entry point for Historical Building Video Story Generator
"""
import sys
from dotenv import load_dotenv
import config
from ui.streamlit_ui import create_interface

# Load environment variables
load_dotenv()

def main():
    """Launch the Streamlit interface"""
    # --- Check if Streamlit is running ---
    try:
        import streamlit as st
        _ = st.session_state
        is_streamlit = True
    except Exception:
        is_streamlit = False

    if not is_streamlit:
        print("=" * 70)
        print("❌ ERROR: This app must be run with Streamlit!")
        print("=" * 70)
        print("\nPlease run one of the following commands:")
        print(f"\n  streamlit run {sys.argv[0]}")
        print(f"\n  python -m streamlit run {sys.argv[0]}")
        print("\n" + "=" * 70)
        sys.exit(1)

    # --- App Header ---
    print("=" * 70)
    print("🏛️  Historical Building Video Story Generator")
    print("Powered by LangGraph, Gemini, and Alibaba DashScope (Wan)")
    print("=" * 70)

    # --- API Key Status ---
    gemini_status = "✅ Set" if config.GEMINI_API_KEY else "❌ Not Set"
    openrouter_status = "✅ Set" if config.OPENROUTER_API_KEY else "❌ Not Set"
    dashscope_status = "✅ Set" if config.DASHSCOPE_API_KEY else "❌ Not Set"

    print(f"Gemini API Key:     {gemini_status}")
    print(f"OpenRouter API Key: {openrouter_status}")
    print(f"DashScope API Key:  {dashscope_status}")
    print("=" * 70)

    # --- Model Configuration ---
    print("🧠 Model Configuration:")
    print(f"  • Gemini Model:     {config.GEMINI_MODEL}")
    print(f"  • OpenRouter Model: {config.OPENROUTER_MODEL}")
    print(f"  • Wan Model:        {config.WAN_MODEL}")
    print(f"  • Max Iterations:   {config.MAX_ITERATIONS}")
    print("=" * 70)

    # --- Validation ---
    if not any([config.GEMINI_API_KEY, config.OPENROUTER_API_KEY, config.DASHSCOPE_API_KEY]):
        print("\n⚠️  WARNING: No API keys configured!")
        print("Please set GEMINI_API_KEY, OPENROUTER_API_KEY, or DASHSCOPE_API_KEY in your .env file.\n")

    print("🚀 Streamlit interface loaded successfully!")
    print("=" * 70)

    # --- Launch UI ---
    create_interface()


if __name__ == "__main__":
    main()
