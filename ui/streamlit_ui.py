import os
import sys
import json
import time
import re
from PIL import Image

# Ensure project root is importable (needed in some run setups)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64
from utils.video_generator import (
    generate_video_with_veo,
    generate_or_get_cached_video,
    get_video_cache_info,
    clear_video_cache,
)
from utils.recommendation import load_landmarks, get_recommendations

import streamlit as st
from slugify import slugify

# MoviePy is optional: keep features disabled if incompatible (Python 3.13)
MOVIEPY_AVAILABLE = True
try:
    from moviepy.editor import concatenate_videoclips, VideoFileClip, AudioFileClip
except Exception:
    MOVIEPY_AVAILABLE = False


# Main APP
def create_interface():
    st.set_page_config(page_title="HistoTales", page_icon="🏛️", layout="wide")
    st.markdown(
        """
        <style>
        .stProgress > div > div > div > div {background-color: #1f77b4;}
        .shot-card {background: #f9fafb; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4;}
        </style>
    """,
        unsafe_allow_html=True,
    )

    # State Init
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "final_state" not in st.session_state:
        st.session_state.final_state = None

    # Header
    st.title("🏛️ AI Tourism: Landmark Analysis & Storytelling")
    st.markdown(
        """
    Upload an image of a historical landmark to:
    - Analyze its architecture and cultural significance  
    - Generate an engaging historical story  
    - Visualize cinematic video shots for tourists and learners
    """
    )

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
        st.info(f"**LLM Model:** {config.GEMINI_MODEL}")
        st.info(f"**Video Model:** {config.VIDEO_MODEL}")

        # Video Cache Management
        st.divider()
        st.subheader("💾 Video Cache")
        cache_info = None
        try:
            cache_info = get_video_cache_info()
        except Exception:
            cache_info = None

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
        st.markdown(
            """
        1. **Upload** a landmark image
        2. **Analyze** its architecture and story
        3. **Generate** cinematic shots
        4. **Preview or render** video segments
        """
        )

    return "gemini"


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
        st.error("Gemini API key missing.")
        return

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
            "user_provided_landmark_name": landmark_name_input.strip() if landmark_name_input.strip() else None,
        }

        status.info("🔄 Initializing workflow...")
        progress.progress(10)
        workflow = create_workflow()

        status.info("🔍 Analyzing image and generating story...")
        progress.progress(30)
        final_state = workflow.invoke(initial_state)

        # --- Determine landmark name: priority: user_provided > workflow-provided > extract from analysis text
        landmark_name = None
        if initial_state.get("user_provided_landmark_name"):
            landmark_name = initial_state["user_provided_landmark_name"]
        elif final_state.get("landmark_name"):
            landmark_name = final_state.get("landmark_name")
        else:
            analysis_text = final_state.get("image_analysis", "") or final_state.get("final_output", "")
            match = re.search(r"Name\s*:\s*(.+)", analysis_text)
            if match:
                landmark_name = match.group(1).strip()
                # Remove common Markdown or stray markers
                landmark_name = re.sub(r"[#*_`]+", "", landmark_name)
            else:
                landmark_name = "Unknown Landmark"

        final_state["landmark_name"] = landmark_name

        progress.progress(100)
        status.success("✅ Completed successfully!")

        st.session_state.processing_complete = True
        st.session_state.final_state = final_state

    except Exception as e:
        st.error(f"❌ Workflow failed: {e}")
    finally:
        time.sleep(1)
        progress.empty()
        status.empty()


# --- Video shot generation helpers (unified) --- #
def _build_shot_prompt(shot, landmark):
    title = shot.get("shot_title", f"Shot {shot.get('shot_number', '0')}")
    desc = shot.get("visual_description", "No visual description provided.")
    mood = shot.get("mood", "Neutral")
    return f"""
Cinematic reenactment of {landmark}.
Scene Title: {title}
Description: {desc}
Mood: {mood}
Include the landmark prominently in the frame.
Dynamic camera motion, realistic atmosphere, natural lighting.
""".strip()


def _merge_audio_with_moviepy(video_path, audio_path, out_path):
    try:
        v = VideoFileClip(video_path)
        a = AudioFileClip(audio_path)
        v = v.set_audio(a)
        v.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
        v.close()
        a.close()
        return out_path
    except Exception as e:
        print(f"[WARN] Audio merge failed for {video_path}: {e}")
        return video_path


def generate_tour_shot(shot, landmark):
    """
    Unified shot generator:
      - Prefers cached generation via generate_or_get_cached_video
      - Falls back to generate_video_with_veo
      - Attempts to merge narration audio using moviepy if available
    Returns: (video_path, audio_used_bool)
    """
    shot_number = shot.get("shot_number", shot.get("id", 0))
    filename = f"{slugify(landmark)}_shot_{shot_number}.mp4"
    full_prompt = _build_shot_prompt(shot, landmark)
    shot["full_prompt"] = full_prompt

    print(f"\n🎬 Generating shot {shot_number} for {landmark}")
    print(f"📝 Prompt:\n{full_prompt}\n")

    video_path = None
    audio_used = False

    # Attempt caching + generation via generate_or_get_cached_video
    try:
        video_path, was_cached = generate_or_get_cached_video(
            landmark_name=landmark,
            prompt=full_prompt.strip(),
            story_type=f"shot_{shot_number}",
            size="832*480",
            force_regenerate=False,
        )
        if video_path:
            print(f"{'Using cached' if was_cached else 'Generated new'} video: {video_path}")
    except Exception as e:
        print(f"[WARN] Cached generation failed: {e}")
        video_path = None

    # Fallback: direct Veo generation
    if not video_path:
        try:
            video_path = generate_video_with_veo(full_prompt, filename)
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video not found at {video_path}")
        except Exception as e:
            print(f"❌ Veo generation failed for shot {shot_number}: {e}")
            raise e

    # Merge audio if present
    audio_path = shot.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        if MOVIEPY_AVAILABLE:
            out_path = f"narrated_{filename}"
            merged = _merge_audio_with_moviepy(video_path, audio_path, out_path)
            if merged and os.path.exists(merged):
                video_path = merged
                audio_used = True
        else:
            print("[INFO] MoviePy not available; skipping audio merge.")

    print(f"✅ Finished shot {shot_number}: {video_path}")
    return video_path, audio_used


def render_shots_tab(final_state, tab):
    with tab:
        # Get recognized landmark name
        landmark = final_state.get("landmark_name", "a historical landmark")
        shots = final_state.get("shots_description", [])

        st.subheader(f"🎬 {landmark} — {len(shots)} Cinematic Shots")

        for i, shot in enumerate(shots):
            shot_title = shot.get("shot_title", f"Shot {i + 1}")
            with st.expander(f"Shot {shot.get('shot_number', i+1)}: {shot_title}", expanded=False):
                st.markdown(
                    f"""
                **Visual:** {shot.get('visual_description','')}  
                **Narration:** {shot.get('narration','')}  
                **Mood:** {shot.get('mood','')} | **Transition:** {shot.get('transition','')}
                """
                )

                # Audio UI
                if shot.get("audio_path") and os.path.exists(shot["audio_path"]):
                    st.audio(shot["audio_path"])
                else:
                    st.caption("No narration audio available.")

                # Show prompt
                with st.expander("📝 AI Prompt", expanded=True):
                    st.code(_build_shot_prompt(shot, landmark), language="text")

                # Generate shot button
                if st.button(f"🎞 Generate Shot {shot.get('shot_number', i+1)}", key=f"gen_shot_{i}"):
                    with st.spinner("Generating cinematic video..."):
                        try:
                            video_path, audio_used = generate_tour_shot(shot, landmark)
                            if video_path and os.path.exists(video_path):
                                st.video(video_path)
                                st.success("✅ Shot generated successfully!")
                            else:
                                st.error("❌ Shot generated but file missing.")
                        except Exception as e:
                            st.error(f"❌ Generation failed: {e}")

        # ---------- DOWNLOAD JSON ----------
        st.download_button("📥 Download Shots JSON", json.dumps(shots, indent=2), "shots.json", mime="application/json")

        st.divider()

        # ---------- COMBINE ALL SHOTS ----------
        if MOVIEPY_AVAILABLE:
            if st.button("🚀 Generate the Full Video"):
                with st.spinner("Combining all generated shots..."):
                    try:
                        clips = []
                        for s in shots:
                            base = f"{slugify(landmark)}_shot_{s['shot_number']}.mp4"
                            narrated = f"narrated_{base}"
                            file = narrated if os.path.exists(narrated) else base
                            if os.path.exists(file):
                                clips.append(VideoFileClip(file))
                            else:
                                st.warning(f"⚠️ Missing file: {file}")

                        if not clips:
                            st.error("No video clips found to combine.")
                            return

                        final_clip = concatenate_videoclips(clips, method="compose")
                        output_path = f"{slugify(landmark)}_final.mp4"
                        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
                        [c.close() for c in clips]
                        final_clip.close()

                        st.success("✅ Final cinematic video created!")
                        st.video(output_path)
                    except Exception as e:
                        st.error(f"❌ Combining failed: {e}")
        else:
            st.info(
                "🎬 Video combination (moviepy) disabled due to compatibility. Individual shot generation still works."
            )


def render_video_tab(final_state, tab):
    with tab:
        st.subheader("🎬 Generated Video")

        video_path = final_state.get("generated_video_path", "")
        video_cached = final_state.get("video_cached", False)
        landmark_name = final_state.get("landmark_name", "Unknown")

        if not video_path or not os.path.exists(video_path):
            st.info("🎬 No video generated yet. Complete the analysis process to generate a video.")
            return

        if video_cached:
            st.success(f"✅ Retrieved cached video for **{landmark_name}**")
        else:
            st.info(f"🎬 Generated new video for **{landmark_name}**")

        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        st.info(f"📁 Video file: `{os.path.basename(video_path)}` ({file_size:.1f} MB)")

        try:
            st.video(video_path)
            with open(video_path, "rb") as file:
                st.download_button(
                    label="📥 Download Video",
                    data=file,
                    file_name=f"{landmark_name.replace(' ', '_').lower()}_video.mp4",
                    mime="video/mp4",
                    key="download_video",
                )
        except Exception as e:
            st.error(f"❌ Error displaying video: {e}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Video", help="Generate a new video even if cached version exists"):
                st.info("🔄 Regenerating video...")
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Video Cache", help="Remove this video from cache"):
                if clear_video_cache(landmark_name, "educational"):
                    st.success("✅ Video cache cleared")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear cache")


def render_recommendations_tab(final_state, tab):
    with tab:
        st.subheader("📍 Nearby Landmark Recommendations")
        landmark_name = final_state.get("landmark_name", "").strip()

        if not landmark_name or landmark_name.lower().startswith("unknown"):
            st.warning("🏛️ Landmark name not found in analysis. Cannot provide recommendations.")
            st.info(
                """
            **Possible solutions:**
            1. **Enter the landmark name manually** in the "🏛️ Landmark Name (Optional)" field before uploading
            2. **Try with a clearer image** that shows distinctive features of the landmark
            3. **Check the progress log** below for detailed extraction information
            """
            )

            manual_name = st.text_input("Enter landmark name manually:", key="manual_landmark_input")
            if manual_name.strip():
                st.info(f"📍 Ready to generate recommendations for: **{manual_name}**")
                if st.button("🔄 Generate recommendations with manual name"):
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

        available_categories = recommendations_df["category"].unique().tolist()
        selected_categories = st.multiselect("Filter by category:", options=available_categories, default=available_categories)

        if selected_categories:
            filtered_recommendations = recommendations_df[recommendations_df["category"].isin(selected_categories)].reset_index(drop=True)
            st.dataframe(filtered_recommendations, use_container_width=True, hide_index=True)
        else:
            recommendations_df = recommendations_df.reset_index(drop=True)
            st.dataframe(recommendations_df, use_container_width=True, hide_index=True)


def render_log_tab(final_state, tab):
    with tab:
        st.subheader("📝 Progress Log")
        st.text_area("Processing Log", final_state.get("progress_log", ""), height=300, disabled=True)


# Results entrypoint that wires tabs (keeps expanded tabs list from 'right' branch)
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
    # Debug tab intentionally left commented in UI


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


def render_footer():
    st.divider()
    st.markdown("<div style='text-align:center;color:#888;padding:15px'>🏛️ Historical Landmark Story Generator</div>", unsafe_allow_html=True)
