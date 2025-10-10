from langgraph.graph import StateGraph, END
from models.state import AgentState
from agents.nodes import (
    detect_description_node,
    extract_landmark_name_node,
    story_telling_node,
    shots_creation_node,
    refine_shots_node,
    video_generation_node,
    narration_generation_node,
    output_node
)


# Conditional Function for Refinement Control
def should_refine(state: AgentState) -> str:
    """
    Determine whether the system should refine shots.

    Refinement happens only if:
      - There are refinement notes (feedback or quality checks)
      - And iteration count < 3 to prevent infinite loops
    """
    notes = state.get("refinement_notes", [])
    iteration = state.get("iteration_count", 0)

    if not notes or iteration >= 3:
        return "output"
    return "refine"


def create_workflow() -> StateGraph:
    """
    Builds and compiles the storytelling generation pipeline with narration.
    """

    workflow = StateGraph(AgentState)

    # --- Stage 1: Image/Scene Understanding ---
    # Extracts historical and visual details from input image
    workflow.add_node("detect", detect_description_node)

    # --- Stage 2: Landmark Name Extraction ---
    # Extracts the specific landmark name from the image analysis
    workflow.add_node("extract_name", extract_landmark_name_node)

    # --- Stage 3: Story Creation ---
    # Generates educational story using the historical context
    workflow.add_node("story", story_telling_node)

    # --- Stage 3: Cinematic Shot Breakdown ---
    # Converts story into visual shots for video generation
    workflow.add_node("shots", shots_creation_node)

    # --- Stage 4: Optional Refinement ---
    # Refines the shots based on feedback or iteration notes
    workflow.add_node("refine", refine_shots_node)

    # --- Stage 5: Video Generation ---
    # Generates or retrieves cached video for the landmark
    workflow.add_node("video", video_generation_node)

    # --- Stage 6: Narration Generation ---
    # Generates audio narration for the video
    workflow.add_node("narration", narration_generation_node)

    # --- Stage 7: Final Output ---
    # Packages all results for video generation or export
    workflow.add_node("output", output_node)

    # Define Flow
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "extract_name")
    workflow.add_edge("extract_name", "story")
    workflow.add_edge("story", "shots")

    # Conditional branching between refinement and output
    workflow.add_conditional_edges(
        "shots",
        should_refine,
        {
            "refine": "refine",
            "output": "video"  # Go to video generation instead of narration
        }
    )

    # After refinement, generate video
    workflow.add_edge("refine", "video")

    # Video goes to narration
    workflow.add_edge("video", "narration")

    # Narration goes to output
    workflow.add_edge("narration", "output")
    workflow.add_edge("output", END)

    return workflow.compile()