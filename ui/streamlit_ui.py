"""
Streamlit UI interface for Historical Building Video Story Generator
"""
import streamlit as st
import json
import os
from PIL import Image
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64
import config

def create_interface():
    """Create and configure the Streamlit interface"""

    # Page configuration
    st.set_page_config(
        page_title="Historical Building Video Story Generator",
        page_icon="🏛️",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #1f77b4;
        }
        .shot-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #1f77b4;
        }
        .success-box {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .error-box {
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'final_state' not in st.session_state:
        st.session_state.final_state = None

    # Title and description
    st.title("🏛️ Historical Building to Video Story Generator")
    st.markdown("""
    This application analyzes historical buildings/landmarks from images and generates:
    - Detailed historical analysis
    - Compelling narrative story  
    - Professional video shot breakdown with AI generation prompts
    - **AI-generated video clips** 🎬
    """)

    # Sidebar
    api_provider = render_sidebar()

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file, refinement_input = render_upload_section()

    with col2:
        render_generation_controls(uploaded_file, refinement_input, api_provider)

    # Results
    render_results()

    # Footer
    render_footer()

def render_sidebar():
    """Render the sidebar content"""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Provider Selection
        api_provider = st.selectbox(
            "Select API Provider",
            ["gemini", "openrouter"],
            help="Choose which AI provider to use"
        )

        st.divider()

        # API Key check
        if api_provider == "gemini":
            if config.GEMINI_API_KEY:
                st.success("✅ Gemini API Key configured")
            else:
                st.error("❌ Gemini API Key not found")
                st.info("Please set GEMINI_API_KEY in your .env file")
        else:  # openrouter
            if config.OPENROUTER_API_KEY:
                st.success("✅ OpenRouter API Key configured")
            else:
                st.error("❌ OpenRouter API Key not found")
                st.info("Please set OPENROUTER_API_KEY in your .env file")

        # Check HF_TOKEN for video generation
        st.divider()
        st.subheader("🎬 Video Generation")
        if os.environ.get("HF_TOKEN"):
            st.success("✅ HF_TOKEN configured")
        else:
            st.error("❌ HF_TOKEN not found")
            st.info("Set HF_TOKEN in .env for video generation")

        st.divider()

        st.subheader("Model Settings")
        if api_provider == "gemini":
            st.info(f"**Model:** {config.GEMINI_MODEL}")
        else:
            st.info(f"**Model:** {config.OPENROUTER_MODEL}")
        st.info(f"**Max Iterations:** {config.MAX_ITERATIONS}")
        st.info(f"**Video Model:** Wan-AI/Wan2.2-TI2V-5B")

        st.divider()

        st.subheader("📖 How to Use")
        st.markdown("""
        1. Select API provider (Gemini or OpenRouter)
        2. Upload an image of a historical building
        3. Click 'Generate Video Story'
        4. Review the analysis and story
        5. Examine detailed shot breakdown
        6. Watch the AI-generated video! 🎬
        """)

        return api_provider

def render_upload_section():
    """Render the image upload section"""
    st.header("📤 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image of a historical building/landmark",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of a historical building or monument"
    )

    refinement_input = ""

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Optional refinement notes
        st.subheader("🔧 Optional Refinement")
        refinement_input = st.text_area(
            "Add refinement notes (optional)",
            placeholder="E.g., 'Focus more on architectural details' or 'Add more historical context'",
            help="These notes will be used to refine the video shots"
        )

    return uploaded_file, refinement_input

def render_generation_controls(uploaded_file, refinement_input, api_provider):
    """Render the generation controls and handle processing"""
    st.header("🎬 Generation Controls")

    if uploaded_file is not None:
        if st.button("🚀 Generate Video Story", type="primary", use_container_width=True):
            process_generation(uploaded_file, refinement_input, api_provider)
    else:
        st.info("👆 Please upload an image to begin")

def process_generation(uploaded_file, refinement_input, api_provider):
    """Handle the generation process"""
    # Check API keys based on provider
    if api_provider == "gemini" and not config.GEMINI_API_KEY:
        st.error("Please configure GEMINI_API_KEY in your .env file")
        return
    elif api_provider == "openrouter" and not config.OPENROUTER_API_KEY:
        st.error("Please configure OPENROUTER_API_KEY in your .env file")
        return

    # Check HF_TOKEN
    if not os.environ.get("HF_TOKEN"):
        st.warning("⚠️ HF_TOKEN not configured. Video generation will be skipped.")

    # Reset state
    st.session_state.processing_complete = False
    st.session_state.final_state = None

    # Create progress containers
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Convert image to base64
        image = Image.open(uploaded_file)
        image_base64 = image_to_base64(image)

        # Prepare refinement notes
        refinement_notes = []
        if refinement_input.strip():
            refinement_notes.append(refinement_input.strip())

        # Initial state
        initial_state = {
            "image_base64": image_base64,
            "api_provider": api_provider,
            "image_analysis": "",
            "created_telling_story": "",
            "shots_description": [],
            "refinement_notes": refinement_notes,
            "iteration_count": 0,
            "final_output": "",
            "final_video_path": "",
            "video_clips": [],
            "messages": [],
            "progress_log": ""
        }

        # Create and run workflow
        status_text.info("🔄 Initializing workflow...")
        progress_bar.progress(10)

        workflow = create_workflow()

        status_text.info("🔍 Analyzing image...")
        progress_bar.progress(25)

        status_text.info("📖 Creating story...")
        progress_bar.progress(40)

        status_text.info("🎬 Generating shots...")
        progress_bar.progress(60)

        status_text.info("🎥 Generating video (this may take several minutes)...")
        progress_bar.progress(75)

        # Run the workflow
        final_state = workflow.invoke(initial_state)

        progress_bar.progress(100)
        status_text.success("✅ Generation complete!")

        # Store in session state
        st.session_state.processing_complete = True
        st.session_state.final_state = final_state

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)
    finally:
        # Clean up progress indicators after a delay
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

def render_results():
    """Render the results section"""
    if not (st.session_state.processing_complete and st.session_state.final_state):
        return

    st.divider()
    st.header("📊 Results")

    final_state = st.session_state.final_state

    # Tabs for different outputs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎬 Final Video",
        "📋 Summary",
        "🏛️ Building Analysis",
        "📖 Historical Story",
        "🎥 Video Shots",
        "📝 Progress Log",
        "🐛 Debug Info"
    ])

    with tab1:
        render_video_tab(final_state)

    with tab2:
        render_summary_tab(final_state)

    with tab3:
        render_analysis_tab(final_state)

    with tab4:
        render_story_tab(final_state)

    with tab5:
        render_shots_tab(final_state)

    with tab6:
        render_log_tab(final_state)

    with tab7:
        render_debug_tab(final_state)

def render_video_tab(final_state):
    """Render the final video tab"""
    st.subheader("🎬 Generated Video")

    video_path = final_state.get("final_video_path", "")
    video_clips = final_state.get("video_clips", [])

    if video_path and os.path.exists(video_path):
        st.success("✅ Video generated successfully!")

        # Display the video
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
            st.video(video_bytes)

        # Download button
        st.download_button(
            "📥 Download Final Video",
            video_bytes,
            file_name="historical_building_video.mp4",
            mime="video/mp4"
        )

        # Video info
        st.info(f"📊 Video file: {video_path}")
        st.info(f"📊 File size: {len(video_bytes) / (1024*1024):.2f} MB")

    elif video_clips:
        st.warning("⚠️ Individual clips generated but concatenation failed")
        st.info("You can download individual clips below:")

        for clip_path in video_clips:
            if os.path.exists(clip_path):
                clip_name = os.path.basename(clip_path)
                with open(clip_path, 'rb') as clip_file:
                    clip_bytes = clip_file.read()
                    st.download_button(
                        f"📥 Download {clip_name}",
                        clip_bytes,
                        file_name=clip_name,
                        mime="video/mp4",
                        key=clip_name
                    )
    else:
        st.warning("⚠️ No video was generated")
        st.info("This could be due to:\n- Missing HF_TOKEN\n- Video generation errors\n- Check the Progress Log for details")

def render_summary_tab(final_state):
    """Render the summary tab"""
    st.subheader("Generation Summary")

    try:
        final_output = json.loads(final_state.get("final_output", "{}"))

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Total Shots", final_output.get("total_shots", 0))
        with col_b:
            st.metric("Refinement Iterations", final_output.get("iterations", 0))
        with col_c:
            status = final_output.get("status", "unknown").upper()
            st.metric("Status", status)
        with col_d:
            video_status = "✅ YES" if final_output.get("final_video_path") else "❌ NO"
            st.metric("Video Generated", video_status)

        if final_output.get("total_shots", 0) > 0:
            st.success("✅ All processing stages completed successfully!")
        else:
            st.warning("⚠️ Processing completed but no shots were generated")

    except json.JSONDecodeError:
        st.warning("Could not parse final output JSON")
        st.code(final_state.get("final_output", "No output available"))

def render_analysis_tab(final_state):
    """Render the building analysis tab"""
    st.subheader("🏛️ Building Analysis")
    analysis = final_state.get("image_analysis", "No analysis available")

    if analysis:
        st.markdown(analysis)

        # Download button
        st.download_button(
            "📥 Download Analysis",
            analysis,
            file_name="building_analysis.txt",
            mime="text/plain"
        )
    else:
        st.warning("No analysis was generated")

def render_story_tab(final_state):
    """Render the historical story tab"""
    st.subheader("📖 Historical Story")
    story = final_state.get("created_telling_story", "No story available")

    if story:
        st.markdown(story)

        # Word count
        word_count = len(story.split())
        st.info(f"📊 Word count: {word_count} words")

        # Download button
        st.download_button(
            "📥 Download Story",
            story,
            file_name="historical_story.txt",
            mime="text/plain"
        )
    else:
        st.warning("No story was generated")

def render_shots_tab(final_state):
    """Render the video shots tab"""
    st.subheader("🎥 Video Shot Breakdown")
    shots = final_state.get("shots_description", [])

    if shots:
        st.info(f"Total shots: {len(shots)}")

        # Display each shot
        for i, shot in enumerate(shots):
            shot_num = shot.get('shot_number', i + 1)
            shot_type = shot.get('shot_type', 'Unknown')
            duration = shot.get('duration_seconds', 0)

            with st.expander(
                f"🎬 Shot {shot_num} - {shot_type} ({duration}s)",
                expanded=(i == 0)
            ):
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.markdown("**Visual Description:**")
                    st.write(shot.get('visual_description', 'N/A'))

                    st.markdown("**Narration:**")
                    st.write(shot.get('narration', 'N/A'))

                with col_right:
                    st.markdown("**Details:**")
                    st.write(f"**Mood:** {shot.get('mood', 'N/A')}")
                    st.write(f"**Transition:** {shot.get('transition', 'N/A')}")

                st.markdown("**🤖 AI Generation Prompt:**")
                ai_prompt = shot.get('ai_generation_prompt', 'N/A')
                st.code(ai_prompt, language=None)

        # Download shots as JSON
        shots_json = json.dumps(shots, indent=2)
        st.download_button(
            "📥 Download All Shots (JSON)",
            shots_json,
            file_name="video_shots.json",
            mime="application/json"
        )
    else:
        st.warning("No shots were generated")

def render_log_tab(final_state):
    """Render the progress log tab"""
    st.subheader("📝 Processing Log")
    progress_log = final_state.get("progress_log", "No log available")
    st.text_area("Log Output", progress_log, height=400, key="log_output", disabled=True)

def render_debug_tab(final_state):
    """Render debug information"""
    st.subheader("🐛 Debug Information")

    st.markdown("### Messages")
    messages = final_state.get("messages", [])
    for msg in messages:
        if "Error" in msg or "ERROR" in msg:
            st.error(f"• {msg}")
        else:
            st.success(f"• {msg}")

    st.divider()

    st.markdown("### State Keys")
    st.json(list(final_state.keys()))

    st.markdown("### Video Generation Status")
    col1, col2 = st.columns(2)
    with col1:
        video_path = final_state.get("final_video_path", "")
        if video_path:
            st.success(f"✅ Video Path: {video_path}")
            st.info(f"Exists: {os.path.exists(video_path)}")
        else:
            st.warning("❌ No video path in state")

    with col2:
        video_clips = final_state.get("video_clips", [])
        if video_clips:
            st.info(f"Individual clips: {len(video_clips)}")
            for clip in video_clips:
                exists = "✅" if os.path.exists(clip) else "❌"
                st.text(f"{exists} {clip}")
        else:
            st.info("No individual clips")

    st.divider()

    st.markdown("### Full State (Raw)")
    if st.checkbox("Show full state (may be large)"):
        # Convert to JSON-serializable format
        debug_state = {}
        for key, value in final_state.items():
            if key == "image_base64":
                debug_state[key] = f"<base64 data: {len(value)} chars>"
            else:
                debug_state[key] = value
        st.json(debug_state)


def render_footer():
    """Render the footer"""
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🏛️ Historical Building Video Story Generator | Powered by LangGraph & AI</p>
            <p style='font-size: 0.8em;'>Video Generation: Hugging Face Replicate (Wan-AI/Wan2.2-TI2V-5B)</p>
        </div>
    """, unsafe_allow_html=True)
