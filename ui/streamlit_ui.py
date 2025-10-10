import os
import sys
import json
import time
from PIL import Image

# Add the parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64
from utils.video_generator import generate_video_with_veo, generate_or_get_cached_video, get_video_cache_info, clear_video_cache
from utils.recommendation import load_landmarks, get_recommendations
import streamlit as st
# Temporarily disable moviepy due to Python 3.13 compatibility issues
# from moviepy.editor import concatenate_videoclips, VideoFileClip, AudioFileClip


# Main APP
def create_interface():
    st.set_page_config(page_title="HistoTales", page_icon="🏛️", layout="wide")
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
        uploaded_file, refinement_input, landmark_name_input = render_upload_section()
    with col2:
        render_generation_controls(uploaded_file, refinement_input, landmark_name_input, api_provider)

    # RESULTS & FOOTER
    render_results()
    render_footer()



# SIDEBAR
def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Model Info
        # st.divider()
        # st.subheader("⚙️ Model Settings")
        st.info(f"**LLM Model:** {config.GEMINI_MODEL}")
        st.info(f"**Video Model:** {config.VIDEO_MODEL}")

        # Video Cache Management
        st.divider()
        st.subheader("💾 Video Cache")
        cache_info = get_video_cache_info()
        if cache_info:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cached Videos", cache_info.get("total_videos", 0))
            with col2:
                st.metric("Unique Landmarks", cache_info.get("unique_landmarks", 0))

            if st.button("🗑️ Clear All Cache", type="secondary"):
                if clear_video_cache():
                    st.success("✅ Cache cleared successfully!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Failed to clear cache")
        else:
            st.info("💾 Video cache not available")

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
    landmark_name_input = ""
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="Uploaded Image", use_container_width=True)
        st.subheader("🔧 Optional Refinement")
        refinement_input = st.text_area("Add notes (optional)", placeholder="Example: Focus on cultural details")

        st.subheader("🏛️ Landmark Name (Optional)")
        st.info("💡 If the system doesn't recognize the landmark automatically, you can enter the name here:")
        landmark_name_input = st.text_input("Landmark name", placeholder="e.g., Pyramids of Giza, Luxor Temple, etc.")

    return uploaded_file, refinement_input, landmark_name_input


# Generation
def render_generation_controls(uploaded_file, refinement_input, landmark_name_input, api_provider):
    st.header("🎬 Generate Story & Video")
    if not uploaded_file:
        st.info("👆 Upload an image to begin.")
        return
    if st.button("🚀 Generate landmark analysis", type="primary", use_container_width=True):
        process_generation(uploaded_file, refinement_input, landmark_name_input, api_provider)


def process_generation(uploaded_file, refinement_input, landmark_name_input, api_provider):
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
            "progress_log": "",
            "user_provided_landmark_name": landmark_name_input.strip() if landmark_name_input.strip() else None
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
    tabs = st.tabs(["📋 Summary", "🏛️ Analysis", "📖 Story", "🎥 Video Shots", "🎬 Generated Video", "📍 Recommendations", "📝 Log", "🐛 Debug"])
    final_state = st.session_state.final_state

    render_summary_tab(final_state, tabs[0])
    render_analysis_tab(final_state, tabs[1])
    render_story_tab(final_state, tabs[2])
    render_shots_tab(final_state, tabs[3])
    render_video_tab(final_state, tabs[4])
    render_recommendations_tab(final_state, tabs[5])
    render_log_tab(final_state, tabs[6])
    # render_debug_tab(final_state, tabs[7])


def render_summary_tab(final_state, tab):
    with tab:
        st.subheader("Summary")
        try:
            data = json.loads(final_state.get("final_output", "{}"))
            st.metric("Total Shots", data.get("total_shots", 0))
            st.metric("Iterations", data.get("iterations", 0))
            st.metric("Status", data.get("status", "unknown").upper())

            # Show video info if available
            video_path = final_state.get("generated_video_path", "")
            video_cached = final_state.get("video_cached", False)

            if video_path:
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                st.metric("Video Size", f"{file_size:.1f} MB")
                st.metric("Video Status", "Cached" if video_cached else "New")
            else:
                st.metric("Video", "Not generated")

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


def generate_shot_video(shot, video_filename, landmark_name):
    """Generate video with narration audio layered on top using caching system."""

    # Build full prompt for video generation
    full_prompt = f"""
Cinematic reenactment of {landmark_name}.
Scene Title: {shot.get('shot_title', '')}
Visual: {shot.get('visual_description', '')}
Mood: {shot.get('mood', '')}
The landmark should appear in the background.
Use dynamic motion, natural lighting, and realistic atmosphere.
"""

    # Use caching system
    video_path, was_cached = generate_or_get_cached_video(
        landmark_name=landmark_name,
        prompt=full_prompt.strip(),
        story_type=f"shot_{shot.get('shot_title', 'unknown')}",
        size="832*480",
        force_regenerate=False
    )

    if was_cached:
        print(f"Using cached video for {landmark_name}")
    else:
        print(f"Generated new video for {landmark_name}")

    # Temporarily disable moviepy audio processing
    # TODO: Re-enable when moviepy compatibility is fixed
    audio_path = shot.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        print(f"Audio file found: {audio_path} (processing disabled for now)")

    return video_path, None



def render_shots_tab(final_state, tab):
    with tab:
        st.subheader("🎥 Video Shot Breakdown")

        shots = final_state.get("shots_description", [])
        if not shots:
            st.info("No shots generated yet.")
            return

        st.info(f"Total shots: {len(shots)}")
        landmark_name = final_state.get("landmark_name", "a historical landmark")

        for i, shot in enumerate(shots):
            with st.expander(f"🎬 {shot.get('shot_title', f'Shot {i + 1}')}", expanded=False):
                st.markdown(f"**Visual:** {shot.get('visual_description', 'N/A')}")
                st.markdown(f"**Narration:** {shot.get('narration', 'N/A')}")
                st.markdown(f"**Mood:** {shot.get('mood', 'N/A')} | **Transition:** {shot.get('transition', 'N/A')}")

                # Show audio status
                audio_path = shot.get("audio_path")
                if audio_path and os.path.exists(audio_path):
                    st.success("🔊 Narration audio ready")
                    st.audio(audio_path)
                else:
                    st.warning("⚠️ No narration audio generated")

                # Generate button
                video_filename = f"shot_{i + 1}.mp4"


                if st.button(f"🎞️ Generate Video with Narration for Shot {i + 1}", key=f"gen_{i}"):
                    try:
                        st.info(f"⏳ Generating video with narration for Shot {i + 1}...")
                        video_path, audio_used = generate_shot_video(shot, video_filename, landmark_name)

                        if audio_used:
                            st.success(f"✅ Shot {i + 1} ready with narration!")
                        else:
                            st.success(f"✅ Shot {i + 1} ready (no audio)")

                        st.video(video_path)
                    except Exception as e:
                        st.error(f"❌ Failed: {e}")

        # Download Shots JSON
        st.download_button(
            "📥 Download Shots JSON",
            json.dumps(shots, indent=2),
            "shots.json",
            mime="application/json"
        )
        # Temporarily disable video combination due to moviepy compatibility issues
        # TODO: Re-enable when moviepy compatibility is fixed
        st.info("🎬 Video combination feature is temporarily disabled due to Python 3.13 compatibility issues with moviepy. Individual video generation works normally.")


def render_video_tab(final_state, tab):
    with tab:
        st.subheader("🎬 Generated Video")

        video_path = final_state.get("generated_video_path", "")
        video_cached = final_state.get("video_cached", False)
        landmark_name = final_state.get("landmark_name", "Unknown")

        if not video_path or not os.path.exists(video_path):
            st.info("🎬 No video generated yet. Complete the analysis process to generate a video.")
            return

        # Show video status
        if video_cached:
            st.success(f"✅ Retrieved cached video for **{landmark_name}**")
        else:
            st.info(f"🎬 Generated new video for **{landmark_name}**")

        # Show video file info
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        st.info(f"📁 Video file: `{os.path.basename(video_path)}` ({file_size:.1f} MB)")

        # Display video
        try:
            st.video(video_path)

            # Download button
            with open(video_path, 'rb') as file:
                st.download_button(
                    label="📥 Download Video",
                    data=file,
                    file_name=f"{landmark_name.replace(' ', '_').lower()}_video.mp4",
                    mime="video/mp4",
                    key="download_video"
                )

        except Exception as e:
            st.error(f"❌ Error displaying video: {e}")

        # Cache management
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Video", help="Generate a new video even if cached version exists"):
                # Force regeneration by calling the workflow again
                st.info("🔄 Regenerating video...")
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Video Cache", help="Remove this video from cache"):
                from utils.video_generator import clear_video_cache
                if clear_video_cache(landmark_name, "educational"):
                    st.success("✅ Video cache cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear cache")


def render_recommendations_tab(final_state, tab):
    with tab:
        st.subheader("📍 Nearby Landmark Recommendations")
        landmark_name = final_state.get("landmark_name", "").strip()

        if not landmark_name or landmark_name == "Unknown":
            st.warning("🏛️ Landmark name not found in analysis. Cannot provide recommendations.")
            st.info("""
            **Possible solutions:**
            1. **Enter the landmark name manually** in the "🏛️ Landmark Name (Optional)" field before uploading
            2. **Try with a clearer image** that shows distinctive features of the landmark
            3. **Check the progress log** below for detailed extraction information
            """)

            # Show manual input option
            manual_name = st.text_input("Enter landmark name manually:", key="manual_landmark_input")
            if manual_name.strip():
                st.info(f"📍 Ready to generate recommendations for: **{manual_name}**")
                if st.button("🔄 Generate recommendations with manual name"):
                    # Update the state with manual name and regenerate
                    final_state["landmark_name"] = manual_name.strip()
                    landmarks_df = load_landmarks()
                    if not landmarks_df.empty:
                        recommendations_df = get_recommendations(manual_name.strip(), landmarks_df, top_n=10)
                        if not recommendations_df.empty:
                            st.success(f"✅ Found recommendations for **{manual_name}**!")
                            st.dataframe(recommendations_df, use_container_width=True, hide_index=True)
                        else:
                            st.error(f"❌ Could not find landmark '{manual_name}' in database.")
                    else:
                        st.error("❌ Landmark database not available.")

            return

        st.info(f"Recommendations based on detected landmark: **{landmark_name}**")

        landmarks_df = load_landmarks()
        if landmarks_df.empty:
            st.error("Landmark dataset is empty or could not be loaded.")
            return

        recommendations_df = get_recommendations(landmark_name, landmarks_df, top_n=10)
        if recommendations_df.empty:
            st.warning(f"No recommendations available for '{landmark_name}'. It might not be in our dataset.")
            st.info("💡 Try entering a different landmark name in the manual input field above.")
            return

        # Category filter
        available_categories = recommendations_df['category'].unique().tolist()
        selected_categories = st.multiselect(
            "Filter by category:",
            options=available_categories,
            default=available_categories
        )

        if selected_categories:
            filtered_recommendations = recommendations_df[recommendations_df['category'].isin(selected_categories)]
            filtered_recommendations = filtered_recommendations.reset_index(drop=True)
            st.dataframe(filtered_recommendations, use_container_width=True, hide_index=True)
        else:
            recommendations_df = recommendations_df.reset_index(drop=True)
            st.dataframe(recommendations_df, use_container_width=True, hide_index=True)

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
