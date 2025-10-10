import os
import json
import time
from PIL import Image
import config
from agents.workflow import create_workflow
from utils.image_utils import image_to_base64
from utils.video_generator import generate_video_with_veo
import streamlit as st
from moviepy.editor import concatenate_videoclips, VideoFileClip, AudioFileClip
from slugify import slugify


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

        # Model Info
        # st.divider()
        # st.subheader("⚙️ Model Settings")
        st.info(f"**LLM Model:** {config.GEMINI_MODEL}")
        st.info(f"**Video Model:** {config.VIDEO_MODEL}")

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
    st.header("🎬 Generate the Story & Videos")
    if not uploaded_file:
        st.info("👆 Upload an image to begin.")
        return
    if st.button("🚀 Generate landmark analysis", type="primary", use_container_width=True):
        process_generation(uploaded_file, refinement_input, api_provider)


def process_generation(uploaded_file, refinement_input, api_provider):
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
            "progress_log": ""
        }

        status.info("🔄 Initializing workflow...")
        progress.progress(10)
        workflow = create_workflow()

        status.info("🔍 Analyzing image and generating story...")
        progress.progress(30)
        final_state = workflow.invoke(initial_state)

        analysis_text = final_state.get("image_analysis", "")
        import re

        match = re.search(r"Name\s*:\s*(.+)", analysis_text)
        if match:
            landmark_name = match.group(1).strip()
            # Remove Markdown symbols like ** or *
            landmark_name = re.sub(r"\*+", "", landmark_name)
        else:
            landmark_name = "Unknown Landmark"

        final_state["landmark_name"] = landmark_name

        progress.progress(100)
        status.success("✅ Completed successfully!")

        # ✅ Save final state with detected landmark name
        st.session_state.processing_complete = True
        st.session_state.final_state = final_state

    except Exception as e:
        st.error(f"❌ Workflow failed: {e}")
    finally:
        time.sleep(1)
        progress.empty()
        status.empty()


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


def generate_tour_shot(shot, landmark):
    """
    Generate a single cinematic video shot for a landmark.
    Handles:
      - Cinematic prompt generation
      - Video generation via Veo
      - Optional narration merge
    Returns the final video path.
    """

    def build_prompt(shot):
        """Construct cinematic AI prompt for the shot."""
        title = shot.get("shot_title", "Unnamed Scene")
        desc = shot.get("visual_description", "No visual description provided.")
        mood = shot.get("mood", "Neutral")
        return f"""
Cinematic historical reenactment of {landmark}.
Scene Title: {title}
Description: {desc}
Mood: {mood}
Include the landmark prominently in the frame.
Dynamic camera motion, realistic atmosphere, natural lighting.
""".strip()

    def merge_audio(video_path, audio_path, out_path):
        """Merge narration audio into video."""
        try:
            v = VideoFileClip(video_path)
            a = AudioFileClip(audio_path)
            v = v.set_audio(a)
            v.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
            v.close(); a.close()
            return out_path
        except Exception as e:
            print(f"[WARN] Audio merge failed for {video_path}: {e}")
            return video_path

    # ---- Step 1: Build cinematic prompt ---- #
    filename = f"{slugify(landmark)}_shot_{shot['shot_number']}.mp4"
    full_prompt = build_prompt(shot)
    shot["full_prompt"] = full_prompt  # store for reference/display

    print(f"\n🎬 Generating shot {shot['shot_number']} for {landmark}")
    print(f"📝 Prompt:\n{full_prompt}\n")

    # ---- Step 2: Generate base video via Veo ---- #
    try:
        video_path = generate_video_with_veo(full_prompt, filename)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found at {video_path}")
    except Exception as e:
        print(f"❌ Veo generation failed for shot {shot['shot_number']}: {e}")
        raise e

    # ---- Step 3: Add narration audio if exists ---- #
    audio_path = shot.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        out_path = f"narrated_{filename}"
        video_path = merge_audio(video_path, audio_path, out_path)

    print(f"✅ Finished shot {shot['shot_number']}: {video_path}")
    return video_path


def render_shots_tab(final_state, tab):
    with tab:
        # Get recognized landmark name
        landmark = final_state.get("landmark_name", "a historical landmark")
        shots = final_state.get("shots_description", [])

        st.subheader(f"🎬 {landmark} — {len(shots)} Cinematic Shots")

        for shot in shots:
            # Use the shot title if available, fallback to "Unnamed Scene"
            shot_title = shot.get("shot_title", "Unnamed Scene")
            with st.expander(f"Shot {shot['shot_number']}: {shot_title}", expanded=False):
                # Show visual, narration, mood, transition
                st.markdown(f"""
                **Visual:** {shot.get('visual_description','')}  
                **Narration:** {shot.get('narration','')}  
                **Mood:** {shot.get('mood','')} | **Transition:** {shot.get('transition','')}
                """)

                # Show audio if exists
                if shot.get("audio_path") and os.path.exists(shot["audio_path"]):
                    st.audio(shot["audio_path"])
                else:
                    st.caption("No narration audio available.")

                # --- Display AI Prompt above the button ---
                full_prompt = f"""
Cinematic historical reenactment of {landmark}.
Scene Title: {shot_title}
Description: {shot.get("visual_description","No visual description provided.")}
Mood: {shot.get("mood","Neutral")}
Include the landmark prominently in the frame.
Dynamic camera motion, realistic atmosphere, natural lighting.
"""
                with st.expander("📝 AI Prompt", expanded=True):
                    st.code(full_prompt, language="text")

                # --- Generate shot button ---
                if st.button(f"🎞 Generate Shot {shot['shot_number']}", key=f"gen_{shot['shot_number']}"):
                    with st.spinner("Generating cinematic video..."):
                        try:
                            video_path = generate_tour_shot(shot, landmark)
                            st.video(video_path)
                            st.success("✅ Shot generated successfully!")
                        except Exception as e:
                            st.error(f"❌ Generation failed: {e}")

        # ---------- DOWNLOAD JSON ----------
        st.download_button(
            "📥 Download Shots JSON",
            json.dumps(shots, indent=2),
            "shots.json",
            mime="application/json"
        )

        st.divider()

        # ---------- COMBINE ALL SHOTS ----------
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
