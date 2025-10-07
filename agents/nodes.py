"""
Agent nodes for the LangGraph workflow - With Video Generation
"""
import json
import os
from langchain_core.messages import HumanMessage, SystemMessage
from models.state import AgentState
from utils.llm_factory import initialize_llm
from prompts.templates import *


def detect_description_node(state: AgentState) -> AgentState:
    """Detect and analyze the historical building/object in the image"""
    progress_msg = "Analyzing image for historical content...\n"
    state["progress_log"] = state.get("progress_log", "") + progress_msg

    image_data = state.get("image_base64", "")
    if not image_data:
        state["messages"].append("Error: No image data provided")
        state["progress_log"] += "ERROR: No image data\n"
        return state

    api_provider = state.get("api_provider", "openrouter")

    try:
        llm = initialize_llm(api_provider)

        response = llm.invoke([
            HumanMessage(content=[
                {"type": "text", "text": DESCRIPTION_DETECTION_PROMPT},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_data}"}
            ])
        ])

        state["image_analysis"] = response.content
        state["messages"].append("Historical content detected and analyzed")
        state["progress_log"] += "Analysis complete\n"

    except Exception as e:
        state["messages"].append(f"Error in image analysis: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"
        state["image_analysis"] = ""

    return state


def story_telling_node(state: AgentState) -> AgentState:
    """Create a compelling historical narrative"""
    progress_msg = "Creating historical narrative...\n"
    state["progress_log"] = state.get("progress_log", "") + progress_msg

    if not state.get("image_analysis"):
        state["messages"].append("Error: No image analysis available for story creation")
        state["progress_log"] += "ERROR: Missing image analysis\n"
        return state

    api_provider = state.get("api_provider", "openrouter")

    try:
        llm = initialize_llm(api_provider)

        story_telling_prompt = STORY_CREATION_PROMPT.format(
            design_analysis=state['image_analysis']
        )

        messages = [
            SystemMessage(content=story_telling_prompt),
            HumanMessage(content="Create an engaging historical story for the detected building/landmark now.")
        ]

        response = llm.invoke(messages)

        state["created_telling_story"] = response.content
        state["messages"].append("Historical narrative created")
        state["progress_log"] += "Story created\n"

    except Exception as e:
        state["messages"].append(f"Error in story creation: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"
        state["created_telling_story"] = ""

    return state


def shots_creation_node(state: AgentState) -> AgentState:
    """Simple reliable shot creation"""
    print("\n=== SHOTS NODE START ===")

    # Always create some basic shots
    state["shots_description"] = [
        {
            "shot_number": 1,
            "duration_seconds": 8,
            "shot_type": "Establishing shot",
            "visual_description": "Wide panoramic view of the historical building in its environment",
            "narration": state.get("created_telling_story", "This historic building stands as a testament to time.")[:200],
            "mood": "Grand",
            "transition": "Fade in",
            "ai_generation_prompt": "Cinematic establishing shot of historical building, wide angle, golden hour lighting"
        },
        {
            "shot_number": 2,
            "duration_seconds": 6,
            "shot_type": "Medium shot",
            "visual_description": "Focus on main architectural features and facade details",
            "narration": state.get("created_telling_story", "Its architecture tells stories of different eras.")[200:400] if len(state.get("created_telling_story", "")) > 200 else "The architecture reflects its historical period.",
            "mood": "Detailed",
            "transition": "Cut",
            "ai_generation_prompt": "Medium shot of historical building facade, architectural details, professional photography"
        },
        {
            "shot_number": 3,
            "duration_seconds": 5,
            "shot_type": "Close-up",
            "visual_description": "Detailed close-up of unique architectural elements and craftsmanship",
            "narration": state.get("created_telling_story", "Every detail has a story to tell.")[400:600] if len(state.get("created_telling_story", "")) > 400 else "Detailed craftsmanship reveals the building's history.",
            "mood": "Intimate",
            "transition": "Dissolve",
            "ai_generation_prompt": "Close-up shot of historical building details, intricate stonework or features"
        }
    ]

    state["messages"].append(f"Created {len(state['shots_description'])} basic shots")
    state["progress_log"] += f"✓ Created {len(state['shots_description'])} shots\n"

    return state


def refine_shots_node(state: AgentState) -> AgentState:
    """Refine shots based on feedback or quality checks"""
    progress_msg = "Refining video shots...\n"
    state["progress_log"] = state.get("progress_log", "") + progress_msg

    api_provider = state.get("api_provider", "openrouter")
    refinement_notes = state.get("refinement_notes", [])
    current_shots = state.get("shots_description", [])
    iteration_count = state.get("iteration_count", 0)

    if not refinement_notes or iteration_count >= 3:
        state["messages"].append("Shots finalized (no refinement needed or max iterations reached)")
        state["progress_log"] += "Shots finalized\n"
        return state

    if not current_shots:
        state["messages"].append("Error: No shots to refine")
        state["progress_log"] += "ERROR: No shots available\n"
        return state

    try:
        llm = initialize_llm(api_provider)

        refinement_prompt = f"""
You are refining video shots for a historical narrative.

ORIGINAL SHOTS:
{json.dumps(current_shots, indent=2)}

REFINEMENT FEEDBACK:
{chr(10).join(refinement_notes)}

TASK: Improve the shots based on the feedback. Return ONLY JSON.
"""

        messages = [
            SystemMessage(content=refinement_prompt),
            HumanMessage(content="Refine the shots now.")
        ]

        response = llm.invoke(messages)

        # Same extraction pattern
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            refined_shots = json.loads(content)
            state["shots_description"] = refined_shots.get("shots", current_shots)
            state["iteration_count"] = iteration_count + 1
            state["messages"].append(f"Shots refined (iteration {iteration_count + 1})")
            state["progress_log"] += f"Refinement iteration {iteration_count + 1} complete\n"
        except json.JSONDecodeError:
            state["messages"].append("Refinement failed, keeping original shots")
            state["progress_log"] += "WARNING: Refinement parse failed\n"

    except Exception as e:
        state["messages"].append(f"Error in refinement: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"

    return state


def video_generation_node(state: AgentState) -> AgentState:
    """Generate video clips from shot descriptions using Hugging Face Replicate"""
    progress_msg = "Generating video clips from shots...\n"
    state["progress_log"] += progress_msg
    state["messages"].append("Starting video generation...")

    # Check for HF_TOKEN
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        state["messages"].append("Error: HF_TOKEN environment variable not set")
        state["progress_log"] += "ERROR: Missing HF_TOKEN\n"
        return state

    try:
        from huggingface_hub import InferenceClient
        from moviepy.editor import VideoFileClip, concatenate_videoclips

        client = InferenceClient(
            provider="replicate",
            api_key=hf_token
        )

        shots = state.get("shots_description", [])
        if not shots:
            state["messages"].append("Error: No shots available for video generation")
            state["progress_log"] += "ERROR: No shots\n"
            return state

        video_files = []
        output_dir = "generated_clips"
        os.makedirs(output_dir, exist_ok=True)

        # Generate each shot
        for i, shot in enumerate(shots):
            shot_num = shot.get("shot_number", i + 1)
            prompt = shot.get("ai_generation_prompt", "")

            if not prompt:
                state["messages"].append(f"Warning: Shot {shot_num} has no prompt, skipping")
                continue

            state["progress_log"] += f"Generating clip {shot_num}/{len(shots)}...\n"

            try:
                # Generate video using Hugging Face
                video_bytes = client.text_to_video(
                    prompt,
                    model="Wan-AI/Wan2.2-TI2V-5B"
                )

                # Save the video file
                filename = os.path.join(output_dir, f"clip_{shot_num}.mp4")
                with open(filename, 'wb') as f:
                    f.write(video_bytes)

                video_files.append(filename)
                state["messages"].append(f"✓ Clip {shot_num} generated successfully")
                state["progress_log"] += f"✓ Clip {shot_num} saved\n"

            except Exception as clip_error:
                state["messages"].append(f"Error generating clip {shot_num}: {str(clip_error)}")
                state["progress_log"] += f"ERROR on clip {shot_num}: {str(clip_error)}\n"

        # Concatenate all clips if we have any
        if video_files:
            state["progress_log"] += "Combining clips into final video...\n"

            try:
                clips = [VideoFileClip(f) for f in video_files]
                final_clip = concatenate_videoclips(clips, method="compose")

                output_path = "final_video.mp4"
                final_clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio=False,
                    fps=24
                )

                # Clean up individual clips
                for clip in clips:
                    clip.close()

                state["final_video_path"] = output_path
                state["messages"].append(f"🎬 Final video created: {output_path}")
                state["progress_log"] += f"✓ Final video saved: {output_path}\n"

            except Exception as concat_error:
                state["messages"].append(f"Error combining clips: {str(concat_error)}")
                state["progress_log"] += f"ERROR: {str(concat_error)}\n"
                # Store individual clips info if concatenation fails
                state["video_clips"] = video_files
        else:
            state["messages"].append("No video clips were generated")
            state["progress_log"] += "ERROR: No clips generated\n"

    except ImportError as ie:
        state["messages"].append(f"Error: Missing required library - {str(ie)}")
        state["progress_log"] += f"ERROR: Install huggingface_hub and moviepy\n"
    except Exception as e:
        state["messages"].append(f"Error in video generation: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"

    return state


def output_node(state: AgentState) -> AgentState:
    """Prepare final output with all generated content"""
    progress_msg = "Preparing final output...\n"
    state["progress_log"] = state.get("progress_log", "") + progress_msg

    final_output = {
        "building_analysis": state.get("image_analysis", ""),
        "historical_story": state.get("created_telling_story", ""),
        "video_shots": state.get("shots_description", []),
        "total_shots": len(state.get("shots_description", [])),
        "iterations": state.get("iteration_count", 0),
        "final_video_path": state.get("final_video_path", ""),
        "video_clips": state.get("video_clips", []),
        "status": "complete"
    }

    state["final_output"] = json.dumps(final_output, indent=2)
    state["messages"].append("Pipeline complete!")
    state["progress_log"] += "All tasks completed successfully\n"

    return state
