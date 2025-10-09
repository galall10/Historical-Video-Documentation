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
    """
    Create video shots based on the actual building analysis and story
    Uses LLM to generate contextually accurate shots
    """
    print("\n=== SHOTS NODE START ===")

    progress_msg = "Creating video shots based on analysis...\n"
    state["progress_log"] = state.get("progress_log", "") + progress_msg

    # Get the actual analysis and story
    image_analysis = state.get("image_analysis", "")
    story = state.get("created_telling_story", "")
    api_provider = state.get("api_provider", "gemini")

    if not image_analysis or not story:
        state["messages"].append("Error: Missing analysis or story for shot creation")
        state["progress_log"] += "ERROR: Cannot create shots without analysis and story\n"
        return state

    # EXTRACT BUILDING INFO MORE RELIABLY
    def extract_building_info(analysis_text):
        """Extract key building details from analysis"""
        info = {
            "name": "historical building",
            "location": "its location",
            "style": "architectural",
            "features": "ancient stonework",
            "period": "historical"
        }

        # Look for common patterns in analysis
        lines = analysis_text.split('\n')
        for line in lines:
            line_lower = line.lower()

            # Extract name
            if 'name:' in line_lower or 'building:' in line_lower or 'structure:' in line_lower:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    info["name"] = parts[1].strip().split('.')[0].strip()

            # Extract location
            if 'location:' in line_lower or 'where:' in line_lower:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    info["location"] = parts[1].strip().split('.')[0].strip()

            # Extract architectural style
            if 'style:' in line_lower or 'architecture:' in line_lower:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    info["style"] = parts[1].strip().split('.')[0].strip()

            # Extract time period
            if 'period:' in line_lower or 'era:' in line_lower or 'built:' in line_lower:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    info["period"] = parts[1].strip().split('.')[0].strip()

        # Extract features from full text
        if 'dome' in analysis_text.lower():
            info["features"] = "domes and arches"
        elif 'tower' in analysis_text.lower() or 'spire' in analysis_text.lower():
            info["features"] = "towers and spires"
        elif 'column' in analysis_text.lower():
            info["features"] = "columns and pillars"
        elif 'facade' in analysis_text.lower():
            info["features"] = "ornate facade"

        return info

    building_info = extract_building_info(image_analysis)

    try:
        llm = initialize_llm(api_provider)

        # Create a MORE SPECIFIC prompt with clearer instructions
        shot_creation_prompt = f"""You are a professional cinematographer creating a documentary video.

BUILDING INFORMATION:
{image_analysis}

HISTORICAL NARRATIVE:
{story}

CRITICAL INSTRUCTIONS:
- Create 3 shots about THIS SPECIFIC BUILDING: {building_info['name']}
- Use details from the analysis above (architectural features, location, style)
- Each shot must reference the actual building name
- Narration must come from the provided story
- Duration: 5-8 seconds per shot

OUTPUT FORMAT (respond with ONLY this JSON, no other text):
{{
  "shots": [
    {{
      "shot_number": 1,
      "duration_seconds": 8,
      "shot_type": "Establishing shot",
      "visual_description": "Wide view showing [SPECIFIC BUILDING] in [LOCATION] with [FEATURES]",
      "narration": "Quote from story, max 200 characters",
      "mood": "Epic/Majestic/Mysterious",
      "transition": "Fade in",
      "ai_generation_prompt": "Cinematic establishing shot of [BUILDING NAME], [LOCATION], [ARCHITECTURAL STYLE], [SPECIFIC FEATURES], golden hour lighting, professional cinematography, 8k, realistic"
    }},
    {{
      "shot_number": 2,
      "duration_seconds": 6,
      "shot_type": "Medium shot",
      "visual_description": "Medium shot of [SPECIFIC ARCHITECTURAL FEATURES]",
      "narration": "Another story excerpt, max 200 chars",
      "mood": "Dramatic/Grand",
      "transition": "Cut",
      "ai_generation_prompt": "Medium shot of [BUILDING NAME], focus on [SPECIFIC FEATURES], detailed architecture, dramatic lighting"
    }},
    {{
      "shot_number": 3,
      "duration_seconds": 5,
      "shot_type": "Close-up",
      "visual_description": "Close detail of [SPECIFIC ELEMENT]",
      "narration": "Final story excerpt, max 200 chars",
      "mood": "Intimate/Ancient",
      "transition": "Dissolve",
      "ai_generation_prompt": "Close-up of [BUILDING NAME] [SPECIFIC DETAIL], craftsmanship, texture, weathering"
    }}
  ]
}}"""

        messages = [
            SystemMessage(content=shot_creation_prompt),
            HumanMessage(content=f"Generate 3 shots for {building_info['name']}. Return ONLY JSON, no markdown.")
        ]

        state["progress_log"] += f"Generating shots for {building_info['name']}...\n"
        response = llm.invoke(messages)

        # Extract JSON from response
        content = response.content.strip()

        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Remove any text before { or after }
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx]

        try:
            shots_data = json.loads(content)

            # Extract shots array
            if isinstance(shots_data, dict) and "shots" in shots_data:
                shots = shots_data["shots"]
            elif isinstance(shots_data, list):
                shots = shots_data
            else:
                raise ValueError("Invalid JSON structure")

            # Validate shots
            if not shots or len(shots) == 0:
                raise ValueError("No shots generated")

            # Ensure all required fields exist
            for i, shot in enumerate(shots):
                shot.setdefault("shot_number", i + 1)
                shot.setdefault("duration_seconds", 5)
                shot.setdefault("shot_type", "Medium shot")
                shot.setdefault("visual_description", "")
                shot.setdefault("narration", "")
                shot.setdefault("mood", "Dramatic")
                shot.setdefault("transition", "Cut")
                shot.setdefault("ai_generation_prompt", "")

            state["shots_description"] = shots
            state["messages"].append(f"✓ Created {len(shots)} shots for {building_info['name']}")
            state["progress_log"] += f"✓ Generated {len(shots)} contextual shots\n"

        except (json.JSONDecodeError, ValueError) as e:
            # IMPROVED FALLBACK: Use extracted building info
            state["messages"].append(f"Warning: JSON parse failed, creating contextual fallback shots")
            state["progress_log"] += f"WARNING: Using fallback with extracted info\n"

            # Split story into chunks for narration
            story_chunks = []
            if story:
                # Try to split by sentences
                import re
                sentences = re.split(r'[.!?]+', story)
                sentences = [s.strip() for s in sentences if s.strip()]

                # Group into ~150 char chunks
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < 180:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            story_chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                if current_chunk:
                    story_chunks.append(current_chunk.strip())

            # Ensure we have 3 chunks
            while len(story_chunks) < 3:
                story_chunks.append(f"A glimpse into the history of {building_info['name']}.")

            # CREATE BUILDING-SPECIFIC FALLBACK SHOTS
            state["shots_description"] = [
                {
                    "shot_number": 1,
                    "duration_seconds": 8,
                    "shot_type": "Establishing shot",
                    "visual_description": f"Wide panoramic view of {building_info['name']} in {building_info['location']}, showing its {building_info['style']} architecture",
                    "narration": story_chunks[0][:200],
                    "mood": "Epic",
                    "transition": "Fade in",
                    "ai_generation_prompt": f"Cinematic establishing shot of {building_info['name']}, {building_info['location']}, {building_info['style']} architecture, wide angle, golden hour lighting, professional cinematography, 8k quality, realistic, architectural photography"
                },
                {
                    "shot_number": 2,
                    "duration_seconds": 6,
                    "shot_type": "Medium shot",
                    "visual_description": f"Medium shot focusing on the {building_info['features']} of {building_info['name']}",
                    "narration": story_chunks[1][:200],
                    "mood": "Majestic",
                    "transition": "Cut",
                    "ai_generation_prompt": f"Medium shot of {building_info['name']}, {building_info['style']} architecture, {building_info['features']}, {building_info['period']} era, dramatic lighting, architectural details, historical monument"
                },
                {
                    "shot_number": 3,
                    "duration_seconds": 5,
                    "shot_type": "Close-up",
                    "visual_description": f"Close-up of the intricate details and craftsmanship of {building_info['name']}",
                    "narration": story_chunks[2][:200],
                    "mood": "Ancient",
                    "transition": "Dissolve",
                    "ai_generation_prompt": f"Close-up shot of {building_info['name']}, {building_info['period']} craftsmanship, architectural details, {building_info['features']}, weathered texture, historical monument, intricate details, high detail photography"
                }
            ]

            state["messages"].append(
                f"✓ Created {len(state['shots_description'])} fallback shots for {building_info['name']}")
            state["progress_log"] += f"✓ Fallback shots created with building-specific context\n"

    except Exception as e:
        state["messages"].append(f"Error creating shots: {str(e)}")
        state["progress_log"] += f"ERROR in shot creation: {str(e)}\n"

        # Ultimate fallback - still try to use building info
        building_name = building_info.get('name', 'historical monument')
        state["shots_description"] = [
            {
                "shot_number": 1,
                "duration_seconds": 8,
                "shot_type": "Establishing shot",
                "visual_description": f"Wide view of {building_name}",
                "narration": story[:180] if story else f"Exploring {building_name}.",
                "mood": "Grand",
                "transition": "Fade in",
                "ai_generation_prompt": f"Cinematic wide shot of {building_name}, dramatic lighting, professional cinematography, historical architecture"
            }
        ]

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
