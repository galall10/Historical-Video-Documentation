import streamlit as st
import json
import config
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64


# MAIN APP ENTRY
def create_interface():
    """Launch the main Streamlit interface"""

    # ---------- PAGE CONFIG ----------
    st.set_page_config(
        page_title="Historical Landmark Story Generator",
        page_icon="🏛️",
        layout="wide"
    )

    # ---------- STYLES ----------
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {background-color: #1f77b4;}
        .shot-card {background: #f9fafb; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4;}
        .success-box {background: #d4edda; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;}
        .error-box {background: #f8d7da; padding: 10px; border-radius: 5px; border-left: 4px solid #dc3545;}
        </style>
    """, unsafe_allow_html=True)

    # ---------- STATE INIT ----------
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "final_state" not in st.session_state:
        st.session_state.final_state = None

    # ---------- HEADER ----------
    st.title("🏛️ Historical Building to Educational Story Generator")
    st.markdown("""
    Upload an image of a historical landmark to:
    - Analyze its architecture and history  
    - Generate a rich educational story  
    - Visualize a cinematic shot breakdown for student learning
    """)

    # ---------- SIDEBAR ----------
    api_provider = render_sidebar()

    # ---------- MAIN LAYOUT ----------
    col1, col2 = st.columns([1, 1])
    uploaded_file, refinement_input = None, ""

    with col1:
        uploaded_file, refinement_input = render_upload_section()

    with col2:
        render_generation_controls(uploaded_file, refinement_input, api_provider)

    # ---------- RESULTS ----------
    render_results()

    # ---------- FOOTER ----------
    render_footer()


# SIDEBAR
def render_sidebar():
    """Render configuration sidebar"""
    with st.sidebar:
        st.header("⚙️ Configuration")

        api_provider = st.selectbox(
            "Select API Provider",
            ["gemini", "openrouter"],
            help="Choose the AI model provider for generation"
        )

        st.divider()
        validate_api_keys(api_provider)

        st.divider()
        st.subheader("Model Settings")
        st.info(f"**Model:** {config.GEMINI_MODEL if api_provider == 'gemini' else config.OPENROUTER_MODEL}")
        st.info(f"**Max Iterations:** {config.MAX_ITERATIONS}")

        st.divider()
        st.subheader("📘 How to Use")
        st.markdown("""
        1. Select API provider  
        2. Upload an image of a historical building  
        3. Click **Generate Video Shots**  
        4. Explore analysis, story, and cinematic plan  
        5. Use AI prompts for video creation  
        """)

        return api_provider


def validate_api_keys(api_provider):
    """Check API key configuration"""
    key_status = (config.GEMINI_API_KEY if api_provider == "gemini" else config.OPENROUTER_API_KEY)
    provider_name = "Gemini" if api_provider == "gemini" else "OpenRouter"

    if key_status:
        st.success(f"✅ {provider_name} API Key configured")
    else:
        st.error(f"❌ {provider_name} API Key missing")
        st.info(f"Please set your {provider_name.upper()}_API_KEY in the .env file.")


# UPLOAD & REFINEMENT
def render_upload_section():
    """Upload image and optional refinement notes"""
    from PIL import Image

    st.header("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose a clear photo of a historical building or landmark",
        type=["png", "jpg", "jpeg"]
    )

    refinement_input = ""
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        st.subheader("🔧 Optional Refinement")
        refinement_input = st.text_area(
            "Add refinement notes (optional)",
            placeholder="Example: 'Focus on cultural background' or 'Add student-friendly facts'."
        )

    return uploaded_file, refinement_input


# GENERATION & WORKFLOW
def render_generation_controls(uploaded_file, refinement_input, api_provider):
    """Run generation process"""
    st.header("🎬 Generate Educational Story & Shots")

    if not uploaded_file:
        st.info("👆 Upload an image to begin.")
        return

    if st.button("🚀 Generate Video Shots", type="primary", use_container_width=True):
        process_generation(uploaded_file, refinement_input, api_provider)


def process_generation(uploaded_file, refinement_input, api_provider):
    """Run the full LangGraph workflow"""
    from PIL import Image
    import time

    if api_provider == "gemini" and not config.GEMINI_API_KEY:
        st.error("Please configure GEMINI_API_KEY in your .env file.")
        return
    if api_provider == "openrouter" and not config.OPENROUTER_API_KEY:
        st.error("Please configure OPENROUTER_API_KEY in your .env file.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

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

        status_text.info("🔄 Initializing AI workflow...")
        progress_bar.progress(10)
        workflow = create_workflow()

        status_text.info("🔍 Analyzing image and generating story...")
        progress_bar.progress(30)

        final_state = workflow.invoke(initial_state)
        progress_bar.progress(100)
        status_text.success("✅ All stages completed successfully!")

        st.session_state.processing_complete = True
        st.session_state.final_state = final_state

    except Exception as e:
        st.error(f"❌ Workflow failed: {e}")
    finally:
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()


# RESULTS DISPLAY
def render_results():
    if not (st.session_state.processing_complete and st.session_state.final_state):
        return

    st.divider()
    st.header("📊 Results Overview")

    tabs = st.tabs([
        "📋 Summary",
        "🏛️ Building Analysis",
        "📖 Historical Story",
        "🎥 Video Shots",
        "📝 Progress Log",
        "🐛 Debug Info"
    ])

    final_state = st.session_state.final_state
    render_summary_tab(final_state, tabs[0])
    render_analysis_tab(final_state, tabs[1])
    render_story_tab(final_state, tabs[2])
    render_shots_tab(final_state, tabs[3])
    render_log_tab(final_state, tabs[4])
    render_debug_tab(final_state, tabs[5])


# TABS
def render_summary_tab(final_state, tab):
    with tab:
        st.subheader("Generation Summary")
        try:
            final_output = json.loads(final_state.get("final_output", "{}"))
            total = final_output.get("total_shots", 0)
            st.metric("Total Shots", total)
            st.metric("Iterations", final_output.get("iterations", 0))
            st.metric("Status", final_output.get("status", "unknown").upper())
            st.success("✅ Successfully completed all processing stages" if total else "⚠️ No shots generated")
        except Exception:
            st.warning("Output could not be parsed as JSON.")
            st.code(final_state.get("final_output", ""), language=None)


def render_analysis_tab(final_state, tab):
    with tab:
        st.subheader("🏛️ Building Analysis")
        analysis = final_state.get("image_analysis", "")
        if analysis:
            st.markdown(analysis)
            st.download_button("📥 Download Analysis", analysis, file_name="analysis.txt")
        else:
            st.info("No analysis available.")


def render_story_tab(final_state, tab):
    with tab:
        st.subheader("📖 Educational Story")
        story = final_state.get("created_telling_story", "")
        if story:
            st.markdown(story)
            st.info(f"Word count: {len(story.split())}")
            st.download_button("📥 Download Story", story, file_name="story.txt")
        else:
            st.warning("No story generated.")


def render_shots_tab(final_state, tab):
    with tab:
        from utils.video_generator import generate_video_with_wan
        import os

        st.subheader("🎥 Video Shot Breakdown")
        shots = final_state.get("shots_description", [])
        if not shots:
            st.info("No shots generated.")
            return

        st.info(f"Total shots: {len(shots)}")
        for i, shot in enumerate(shots):
            with st.expander(f"🎬 Shot {shot.get('shot_number', i+1)} - {shot.get('shot_type', 'Unknown')}"):
                st.markdown(f"**Visual:** {shot.get('visual_description', 'N/A')}")
                st.markdown(f"**Narration:** {shot.get('narration', 'N/A')}")
                st.markdown(f"**Mood:** {shot.get('mood', 'N/A')} | **Transition:** {shot.get('transition', 'N/A')}")
                st.code(shot.get("ai_generation_prompt", ""), language=None)

                if st.button(f"🎞️ Generate Video for Shot {i+1}", key=f"gen_{i}"):
                    try:
                        st.info("⏳ Generating video with wan2.2-t2v-plus...")
                        video_path = generate_video_with_wan(shot["ai_generation_prompt"], f"shot_{i+1}.mp4")
                        if os.path.exists(video_path):
                            st.success("✅ Video ready!")
                            st.video(video_path)
                        else:
                            st.error("Video file missing after generation.")
                    except Exception as e:
                        st.error(f"Failed: {e}")

        st.download_button("📥 Download Shots JSON", json.dumps(shots, indent=2), "shots.json")


def render_log_tab(final_state, tab):
    with tab:
        st.subheader("📝 Progress Log")
        st.text_area("Processing Log", final_state.get("progress_log", ""), height=300, disabled=True)


def render_debug_tab(final_state, tab):
    with tab:
        st.subheader("🐛 Debug Info")
        st.json(final_state)


# FOOTER
def render_footer():
    st.divider()
    st.markdown("""
    <div style='text-align:center;color:#888;padding:15px'>
    <p>🏛️ Historical Landmark Story Generator — for Learning & Visualization</p>
    </div>
    """, unsafe_allow_html=True)
