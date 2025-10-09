import json
from langchain_core.messages import HumanMessage, SystemMessage
from models.state import AgentState
from utils.llm_factory import initialize_llm
from prompts.templates import *


def detect_description_node(state: AgentState) -> AgentState:
    """Analyze the image and extract historical, architectural, and cultural context."""
    state["progress_log"] = state.get("progress_log", "") + "Analyzing image for historical content...\n"
    image_data = state.get("image_base64", "")

    if not image_data:
        state["messages"].append("Error: No image data provided.")
        state["progress_log"] += "ERROR: Missing image data.\n"
        return state

    api_provider = state.get("api_provider", "openrouter")

    try:
        llm = initialize_llm()
        response = llm.invoke([
            HumanMessage(content=[
                {"type": "text", "text": DESCRIPTION_DETECTION_PROMPT},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_data}"}
            ])
        ])

        state["image_analysis"] = response.content
        state["messages"].append("Image successfully analyzed.")
        state["progress_log"] += "Image analysis complete.\n"

    except Exception as e:
        state["messages"].append(f"Image analysis failed: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"
        state["image_analysis"] = ""

    return state


def story_telling_node(state: AgentState) -> AgentState:
    """Generate an educational cinematic story about the analyzed landmark."""
    state["progress_log"] = state.get("progress_log", "") + "Generating educational story...\n"
    image_analysis = state.get("image_analysis", "")

    if not image_analysis:
        state["messages"].append("Error: No image analysis available for story creation.")
        state["progress_log"] += "ERROR: Missing image analysis.\n"
        return state

    api_provider = state.get("api_provider", "openrouter")

    try:
        llm = initialize_llm()

        story_prompt = f"{STORY_CREATION_PROMPT.format(design_analysis=image_analysis)}"
        messages = [
            SystemMessage(content=story_prompt),
            HumanMessage(content="Generate the educational cinematic story now.")
        ]

        response = llm.invoke(messages)
        story_content = response.content.strip()

        state["created_telling_story"] = story_content
        state["messages"].append("Story created successfully.")
        state["progress_log"] += "Educational story generated.\n"

    except Exception as e:
        state["messages"].append(f"Story creation failed: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"
        state["created_telling_story"] = ""

    return state


def shots_creation_node(state: AgentState) -> AgentState:
    """Generate cinematic educational shots from the story."""
    import json, re
    from langchain.schema import SystemMessage, HumanMessage
    from utils.llm_factory import initialize_llm
    from prompts.templates import SHOTS_CREATION_PROMPT

    state["progress_log"] = state.get("progress_log", "") + "Creating cinematic shots...\n"
    story = state.get("created_telling_story", "")

    if not story:
        state["messages"].append("❌ No story available for shot creation.")
        state["progress_log"] += "ERROR: Missing story content.\n"
        return state

    try:
        llm = initialize_llm()
        prompt = SHOTS_CREATION_PROMPT.format(
            historical_story=story,
            original_analysis=state.get("image_analysis", "")
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content="Generate the cinematic shots as JSON only.")
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        # Debug: check what model returned
        print("\n===== RAW LLM RESPONSE (shots node) =====")
        print(content[:2000])
        print("========================================\n")

        # Extract JSON safely
        json_match = re.search(r"\{[\s\S]*\}", content)
        if not json_match:
            state["messages"].append("⚠️ No valid JSON found in LLM response.")
            state["progress_log"] += "ERROR: No JSON detected.\n"
            return state

        try:
            parsed = json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            state["messages"].append(f"⚠️ JSON parse error: {e}")
            state["progress_log"] += "ERROR: Failed to parse JSON.\n"
            return state

        shots = parsed.get("shots")
        if not shots or not isinstance(shots, list):
            state["messages"].append("⚠️ Parsed JSON but no shots found.")
            state["progress_log"] += "ERROR: 'shots' key missing or empty in JSON.\n"
            print("Parsed JSON content:", parsed)
            return state

        # Success
        state["shots_description"] = shots
        state["messages"].append(f"✅ Generated {len(shots)} cinematic shots.")
        state["progress_log"] += f"Generated {len(shots)} cinematic shots successfully.\n"

    except Exception as e:
        state["messages"].append(f"❌ Shot generation failed: {e}")
        state["progress_log"] += f"ERROR: {str(e)}\n"

    return state



def refine_shots_node(state: AgentState) -> AgentState:
    """Refine the generated shots if feedback is available."""
    state["progress_log"] = state.get("progress_log", "") + "Refining shots...\n"
    refinement_notes = state.get("refinement_notes", [])
    current_shots = state.get("shots_description", [])
    iteration_count = state.get("iteration_count", 0)

    if not refinement_notes or iteration_count >= 3:
        state["messages"].append("No refinement needed or max iterations reached.")
        state["progress_log"] += "Refinement skipped.\n"
        return state

    if not current_shots:
        state["messages"].append("Error: No shots available to refine.")
        state["progress_log"] += "ERROR: No shots found.\n"
        return state

    try:
        llm = initialize_llm()

        refinement_prompt = f"""
Refine the following cinematic shots based on the feedback provided.
Return only valid JSON.

Original shots:
{json.dumps(current_shots, indent=2)}

Feedback:
{chr(10).join(refinement_notes)}
"""

        messages = [
            SystemMessage(content=refinement_prompt),
            HumanMessage(content="Apply the refinements now.")
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            refined_shots = json.loads(content)
            state["shots_description"] = refined_shots.get("shots", current_shots)
            state["iteration_count"] = iteration_count + 1
            state["messages"].append(f"Shots refined (iteration {iteration_count + 1}).")
            state["progress_log"] += f"Refinement {iteration_count + 1} complete.\n"

        except json.JSONDecodeError:
            state["messages"].append("Refinement failed, keeping original shots.")
            state["progress_log"] += "WARNING: Refinement parsing failed.\n"

    except Exception as e:
        state["messages"].append(f"Refinement error: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"

    return state


def output_node(state: AgentState) -> AgentState:
    """Prepare the final structured output of all results."""
    state["progress_log"] = state.get("progress_log", "") + "Preparing final output...\n"

    final_output = {
        "building_analysis": state.get("image_analysis", ""),
        "historical_story": state.get("created_telling_story", ""),
        "video_shots": state.get("shots_description", []),
        "total_shots": len(state.get("shots_description", [])),
        "iterations": state.get("iteration_count", 0),
        "status": "complete"
    }

    state["final_output"] = json.dumps(final_output, indent=2)
    state["messages"].append("Pipeline complete.")
    state["progress_log"] += "All tasks finished successfully.\n"

    return state
