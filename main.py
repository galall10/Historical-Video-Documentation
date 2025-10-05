"""
Main application entry point for Historical Building Video Story Generator
"""
import sys
from ui.streamlit_ui import create_interface
import config


def main():
    """Launch the Streamlit interface"""
    # Check if running with streamlit
    try:
        import streamlit as st
        # If we can access session_state without error, we're running with streamlit
        _ = st.session_state
        is_streamlit = True
    except:
        is_streamlit = False

    if not is_streamlit:
        print("=" * 70)
        print("❌ ERROR: This app must be run with Streamlit!")
        print("=" * 70)
        print("\nPlease run the following command instead:")
        print(f"\n  streamlit run {sys.argv[0]}")
        print("\nOr if that doesn't work:")
        print(f"\n  python -m streamlit run {sys.argv[0]}")
        print("\n" + "=" * 70)
        sys.exit(1)

    # If we get here, we're running with streamlit
    print("=" * 60)
    print("🏛️  Historical Building Video Story Generator")
    print("Powered by LangGraph & AI")
    print("=" * 60)

    # API Key Status
    gemini_status = '✅ Set' if config.GEMINI_API_KEY else '❌ Not Set'
    openrouter_status = '✅ Set' if config.OPENROUTER_API_KEY else '❌ Not Set'

    print(f"Gemini API Key: {gemini_status}")
    print(f"OpenRouter API Key: {openrouter_status}")
    print("=" * 60)

    # Model Configuration
    print("Model Configuration:")
    print(f"  • Gemini Model: {config.GEMINI_MODEL}")
    print(f"  • OpenRouter Model: {config.OPENROUTER_MODEL}")
    print(f"  • Max Iterations: {config.MAX_ITERATIONS}")
    print("=" * 60)

    # Validation
    if not config.GEMINI_API_KEY and not config.OPENROUTER_API_KEY:
        print("\n⚠️  WARNING: No API keys configured!")
        print("Please set GEMINI_API_KEY or OPENROUTER_API_KEY in your .env file\n")

    print("Streamlit interface loaded successfully!")
    print("=" * 60)

    # Launch the Streamlit interface
    create_interface()


if __name__ == "__main__":
    main()