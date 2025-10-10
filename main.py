import sys
from dotenv import load_dotenv
import config
from ui.streamlit_ui import create_interface


# Load environment variables
load_dotenv()


def main():
    """Run the Streamlit interface for the Historical Building Story Generator."""
    try:
        import streamlit as st
        _ = st.session_state
    except Exception:
        print("\nError: This application must be launched with Streamlit.\n")
        print("Try one of the following commands:")
        print(f"  streamlit run {sys.argv[0]}")
        print(f"  python -m streamlit run {sys.argv[0]}\n")
        sys.exit(1)

    # API key status
    print("API Key Status:")
    print(f"  Gemini:     {'Set' if config.GEMINI_API_KEY else 'Not Set'}")
    print(f"  DashScope:  {'Set' if config.DASHSCOPE_API_KEY else 'Not Set'}\n")

    # Model configuration
    print("Model Configuration:")
    print(f"  Gemini Model:     {config.GEMINI_MODEL}")
    print(f"  Wan Model:        {config.WAN_MODEL}")

    if not any([config.GEMINI_API_KEY, config.DASHSCOPE_API_KEY]):
        print("Warning: No API keys found. Update your .env file before proceeding.\n")

    print("Launching Streamlit interface...\n")
    create_interface()


if __name__ == "__main__":
    main()
