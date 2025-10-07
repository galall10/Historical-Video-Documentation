"""
Streamlit UI interface for Historical Building Video Story Generator
"""
import streamlit as st
import json
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

        st.divider()

        st.subheader("Model Settings")
        if api_provider == "gemini":
            st.info(f"**Model:** {config.GEMINI_MODEL}")
        else:
            st.info(f"**Model:** {config.OPENROUTER_MODEL}")
        st.info(f"**Max Iterations:** {config.MAX_ITERATIONS}")

        st.divider()

        st.subheader("📖 How to Use")
        st.markdown("""
        1. Select API provider (Gemini or OpenRouter)
        2. Upload an image of a historical building
        3. Click 'Generate Video Shots'
        4. Review the analysis and story
        5. Examine detailed shot breakdown
        6. Use AI prompts for video generation
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
        if st.button("🚀 Generate Video Shots", type="primary", use_container_width=True):
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
            "messages": [],
            "progress_log": ""
        }

        # Create and run workflow
        status_text.info("🔄 Initializing workflow...")
        progress_bar.progress(10)

        workflow = create_workflow()

        status_text.info("🔍 Analyzing image...")
        progress_bar.progress(25)

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Summary",
        "🏛️ Building Analysis",
        "📖 Historical Story",
        "🎥 Video Shots",
        "📝 Progress Log",
        "🐛 Debug Info"
    ])

    with tab1:
        render_summary_tab(final_state)

    with tab2:
        render_analysis_tab(final_state)

    with tab3:
        render_story_tab(final_state)

    with tab4:
        render_shots_tab(final_state)

    with tab5:
        render_log_tab(final_state)

    with tab6:
        render_debug_tab(final_state)


def render_summary_tab(final_state):
    """Render the summary tab"""
    st.subheader("Generation Summary")

    try:
        final_output = json.loads(final_state.get("final_output", "{}"))

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Shots", final_output.get("total_shots", 0))
        with col_b:
            st.metric("Refinement Iterations", final_output.get("iterations", 0))
        with col_c:
            status = final_output.get("status", "unknown").upper()
            st.metric("Status", status)

        if final_output.get("total_shots", 0) > 0:
            st.success("✅ All processing stages completed successfully!")
        else:
            st.warning("⚠️ Processing completed but no shots were generated")
            st.info("Check the Debug Info tab to see what the LLM returned")

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
    import streamlit as st
    import json
    import os

    st.subheader("🎥 Video Shot Breakdown")
    shots = final_state.get("shots_description", [])

    if shots:
        st.info(f"Total shots: {len(shots)}")

        # Check if this is an error shot
        if len(shots) == 1 and shots[0].get("error"):
            st.error("⚠️ Shot generation failed. Check the Debug Info tab for details.")

        # Display each shot
        for i, shot in enumerate(shots):
            shot_num = shot.get("shot_number", i + 1)
            shot_type = shot.get("shot_type", "Unknown")
            duration = shot.get("duration_seconds", 0)

            with st.expander(
                f"🎬 Shot {shot_num} - {shot_type} ({duration}s)",
                expanded=(i == 0)
            ):
                col_left, col_right = st.columns([2, 1])

                with col_left:
                    st.markdown("**Visual Description:**")
                    st.write(shot.get("visual_description", "N/A"))

                    st.markdown("**Narration:**")
                    st.write(shot.get("narration", "N/A"))

                with col_right:
                    st.markdown("**Details:**")
                    st.write(f"**Mood:** {shot.get('mood', 'N/A')}")
                    st.write(f"**Transition:** {shot.get('transition', 'N/A')}")

                st.markdown("**🤖 AI Generation Prompt:**")
                ai_prompt = shot.get("ai_generation_prompt", "N/A")
                st.code(ai_prompt, language=None)

                # 🎞️ Generate video using Wan 2.2
                generate_btn_key = f"generate_video_{shot_num}"
                if st.button(f"🎞️ Generate Video for Shot {shot_num}", key=generate_btn_key):
                    from utils.video_generator import generate_video_with_wan
                    status_placeholder = st.empty()

                    try:
                        status_placeholder.info("⏳ Generating video with Wan2.2-t2v-plus... please wait (20–60s)...")
                        video_path = generate_video_with_wan(ai_prompt, f"shot_{shot_num}.mp4")

                        if os.path.exists(video_path):
                            status_placeholder.success("✅ Video generated successfully!")
                            st.video(video_path)
                        else:
                            status_placeholder.error("❌ Video file not found after generation.")
                    except Exception as e:
                        status_placeholder.error(f"❌ Failed: {e}")

                # Show error if present
                if "error" in shot:
                    st.error(f"⚠️ {shot['error']}")
                    if "raw_response" in shot:
                        with st.expander("View Raw LLM Response"):
                            st.code(shot["raw_response"])

        # Download all shots as JSON
        shots_json = json.dumps(shots, indent=2)
        st.download_button(
            "📥 Download All Shots (JSON)",
            shots_json,
            file_name="video_shots.json",
            mime="application/json",
        )
    else:
        st.warning("No shots were generated")
        st.info("💡 Tip: Check the Debug Info tab to see what happened during shot creation")


def render_log_tab(final_state):
    """Render the progress log tab"""
    st.subheader("📝 Processing Log")
    progress_log = final_state.get("progress_log", "No log available")
    st.text_area("Log Output", progress_log, height=300, key="log_output", disabled=True)


def render_debug_tab(final_state):
    """Render debug information"""
    st.subheader("🐛 Debug Information")

    st.markdown("### Messages")
    messages = final_state.get("messages", [])
    for msg in messages:
        if "Error" in msg:
            st.error(f"• {msg}")
        else:
            st.success(f"• {msg}")

    st.divider()

    # Check if we have debug responses
    raw_response = final_state.get("_debug_raw_response", "")
    cleaned_response = final_state.get("_debug_cleaned_response", "")

    if raw_response or cleaned_response:
        st.markdown("### 🔍 LLM Response Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Raw LLM Response (first 2000 chars):**")
            if raw_response:
                st.code(raw_response, language=None)

                # Analysis
                st.markdown("**Analysis:**")
                if raw_response.strip().startswith("```"):
                    st.warning("⚠️ Response starts with markdown code block")
                elif raw_response.strip().startswith("{"):
                    st.success("✓ Response starts with JSON")
                elif raw_response.strip().startswith("\n"):
                    st.error("⚠️ Response starts with newline(s)")
                else:
                    st.info(f"Response starts with: {raw_response[:50]}")
            else:
                st.info("No raw response saved")

        with col2:
            st.markdown("**Cleaned Response (first 2000 chars):**")
            if cleaned_response:
                st.code(cleaned_response, language=None)

                # Validation
                st.markdown("**Validation:**")
                try:
                    json.loads(cleaned_response)
                    st.success("✓ Valid JSON after cleaning")
                except json.JSONDecodeError as e:
                    st.error(f"✗ Still invalid: {e.msg} at position {e.pos}")
            else:
                st.info("No cleaned response saved")
    else:
        st.warning("No debug response data found. The error occurred before debug data could be saved.")

    st.divider()

    st.markdown("### State Keys")
    st.json(list(final_state.keys()))

    st.markdown("### Shots Description")
    shots = final_state.get("shots_description", [])
    if shots:
        st.json(shots)

        # Check for error shots
        if len(shots) > 0 and shots[0].get("error"):
            st.error("Shots array contains error information")
            if "raw_response" in shots[0]:
                st.markdown("**Raw Response from Error Shot:**")
                st.code(shots[0]["raw_response"], language=None)
            if "cleaned_response" in shots[0]:
                st.markdown("**Cleaned Response from Error Shot:**")
                st.code(shots[0]["cleaned_response"], language=None)
    else:
        st.warning("No shots in state")

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
        </div>
    """, unsafe_allow_html=True)