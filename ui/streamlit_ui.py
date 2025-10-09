import os
import json
import time
import streamlit as st
from PIL import Image
import config
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64
from utils.video_generator import generate_video_with_wan


# Main APP
def create_interface():
    st.set_page_config(page_title="AI Tour Historian", page_icon="🏛️", layout="wide")
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {background-color: #1f77b4;}
        .shot-card {background: #f9fafb; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4;}
        </style>
    """, unsafe_allow_html=True)

    # State Init
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "final_state" not in st.session_state:
        st.session_state.final_state = None

    # Header
    st.title("🏛️ AI Tourism: Landmark Analysis & Storytelling")
    st.markdown("""
    Upload an image of a historical landmark to:
    - Analyze its architecture and cultural significance  
    - Generate an engaging historical story  
    - Visualize cinematic video shots for tourists and learners
    """)

    # SIDEBAR
    api_provider = render_sidebar()

    # Main Layout
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file, refinement_input = render_upload_section()
    with col2:
        render_generation_controls(uploaded_file, refinement_input, api_provider)

    # RESULTS & FOOTER
    render_results()
    render_footer()



# SIDEBAR
def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Provider
        st.subheader("🧠 AI Provider")
        st.info("**Provider:** Gemini")

        # Model Info
        st.divider()
        st.subheader("⚙️ Model Settings")
        st.info(f"**Model:** {config.GEMINI_MODEL}")
        st.info(f"**Max Iterations:** {config.MAX_ITERATIONS}")

        # Usage Guide
        st.divider()
        st.subheader("📘 Quick Guide")
        st.markdown("""
        1. **Upload** a landmark image  
        2. **Analyze** its architecture and story  
        3. **Generate** cinematic shots  
        4. **Preview or render** video segments
        """)

    return "gemini"


# def validate_api_keys():
#     key = config.GEMINI_API_KEY
#     name = "Gemini"
#     if key:
#         st.success(f"✅ {name} API Key configured")
#     else:
#         st.error(f"❌ {name} API Key missing — please set it in your .env file")



def render_upload_section():
    st.header("📤 Upload Image")
    uploaded_file = st.file_uploader("Choose a photo of a historical landmark", type=["png", "jpg", "jpeg"])
    refinement_input = ""
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="Uploaded Image", use_container_width=True)
        st.subheader("🔧 Optional Refinement")
        refinement_input = st.text_area("Add notes (optional)", placeholder="Example: Focus on cultural details")
    return uploaded_file, refinement_input


# Generation
def render_generation_controls(uploaded_file, refinement_input, api_provider):
    st.header("🎬 Generate Story & Video")
    if not uploaded_file:
        st.info("👆 Upload an image to begin.")
        return
    if st.button("🚀 Generate landmark analysis", type="primary", use_container_width=True):
        process_generation(uploaded_file, refinement_input, api_provider)


def process_generation(uploaded_file, refinement_input, api_provider):
    if api_provider == "gemini" and not config.GEMINI_API_KEY:
        st.error("Gemini API key missing."); return

    progress, status = st.progress(0), st.empty()
    try:
        image_base64 = image_to_base64(Image.open(uploaded_file))
        refinement_notes = [refinement_input.strip()] if refinement_input.strip() else []
        initial_state = {
            "image_base64": image_base64,
            "api_provider": api_provider,
            "image_analysis": "",
            "created_telling_story": "",
            "shots_description": [],
            "refinement_notes": refinement_notes,
            "iteration_count": 0,
            "final_output": "",
            "messages": [],
            "progress_log": ""
        }

        status.info("🔄 Initializing workflow..."); progress.progress(10)
        workflow = create_workflow()

        status.info("🔍 Analyzing image and generating story..."); progress.progress(30)
        final_state = workflow.invoke(initial_state)

        progress.progress(100)
        status.success("✅ Completed successfully!")

        st.session_state.processing_complete = True
        st.session_state.final_state = final_state

    except Exception as e:
        st.error(f"❌ Workflow failed: {e}")
    finally:
        time.sleep(1)
        progress.empty(); status.empty()


# Results
def render_results():
    if not (st.session_state.processing_complete and st.session_state.final_state):
        return

    st.divider()
    st.header("📊 Results Overview")
    tabs = st.tabs(["📋 Summary", "🏛️ Analysis", "📖 Story", "🎥 Video Shots", "📝 Log", "🐛 Debug"])
    final_state = st.session_state.final_state

    render_summary_tab(final_state, tabs[0])
    render_analysis_tab(final_state, tabs[1])
    render_story_tab(final_state, tabs[2])
    render_shots_tab(final_state, tabs[3])
    render_log_tab(final_state, tabs[4])
    # render_debug_tab(final_state, tabs[5])


def render_summary_tab(final_state, tab):
    with tab:
        st.subheader("Summary")
        try:
            data = json.loads(final_state.get("final_output", "{}"))
            st.metric("Total Shots", data.get("total_shots", 0))
            st.metric("Iterations", data.get("iterations", 0))
            st.metric("Status", data.get("status", "unknown").upper())
        except Exception:
            st.warning("Output not JSON-formatted.")
            st.code(final_state.get("final_output", ""), language=None)


def render_analysis_tab(final_state, tab):
    with tab:
        st.subheader("🏛️ Landmark Analysis")
        analysis = final_state.get("image_analysis", "")
        st.markdown(analysis or "No analysis available.")
        if analysis:
            st.download_button("📥 Download", analysis, "analysis.txt")


def render_story_tab(final_state, tab):
    with tab:
        st.subheader("📖 Landmark Story")
        story = final_state.get("created_telling_story", "")
        st.markdown(story or "No story generated.")
        if story:
            st.info(f"Word count: {len(story.split())}")
            st.download_button("📥 Download", story, "story.txt")


def render_shots_tab(final_state, tab):
    with tab:
        st.subheader("🎥 Video Shot Breakdown")
        shots = final_state.get("shots_description", [])
        if not shots:
            st.info("No shots generated."); return

        st.info(f"Total shots: {len(shots)}")

        for i, shot in enumerate(shots):
            with st.expander(f"🎬 {shot.get('shot_title', f'Shot {i+1}')}", expanded=False):
                st.markdown(f"**Visual:** {shot.get('visual_description', 'N/A')}")
                st.markdown(f"**Narration:** {shot.get('narration', 'N/A')}")
                st.markdown(f"**Mood:** {shot.get('mood', 'N/A')} | **Transition:** {shot.get('transition', 'N/A')}")

                # Build full cinematic prompt for video
                full_prompt = f"""
Cinematic reenactment of {final_state.get('landmark_name', 'a historical landmark')}.
Scene Title: {shot.get('shot_title', '')}
Visual: {shot.get('visual_description', '')}
Narration: "{shot.get('narration', '')}"
Mood: {shot.get('mood', '')}
The landmark should appear in the scene background.
Use dynamic motion, natural light, and atmosphere.
"""

                # st.code(full_prompt, language=None)

                if st.button(f"🎞️ Generate Video for Shot {i+1}", key=f"gen_{i}"):
                    try:
                        st.info("⏳ Generating video...")
                        video_path = generate_video_with_wan(full_prompt.strip(), f"shot_{i+1}.mp4")
                        if os.path.exists(video_path):
                            st.success("✅ Video ready!")
                            st.video(video_path)
                        else:
                            st.error("Video file missing.")
                    except Exception as e:
                        st.error(f"Failed: {e}")

        st.download_button("📥 Download Shots JSON", json.dumps(shots, indent=2), "shots.json")



def render_log_tab(final_state, tab):
    with tab:
        st.subheader("📝 Progress Log")
        st.text_area("Processing Log", final_state.get("progress_log", ""), height=300, disabled=True)


# def render_debug_tab(final_state, tab):
#     with tab:
#         st.subheader("🐛 Debug Info")
#         st.json(final_state)


def render_footer():
    st.divider()
    st.markdown("<div style='text-align:center;color:#888;padding:15px'>🏛️ Historical Landmark Story Generator</div>", unsafe_allow_html=True)
