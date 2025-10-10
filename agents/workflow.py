from langgraph.graph import StateGraph, END
from models.state import AgentState
from agents.nodes import (
    detect_description_node,
    story_telling_node,
    shots_creation_node,
    refine_shots_node,
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


    workflow.add_node("detect", detect_description_node)
    workflow.add_node("story", story_telling_node)
    workflow.add_node("shots", shots_creation_node)
    workflow.add_node("refine", refine_shots_node)


    workflow.add_node("narration", narration_generation_node)

    workflow.add_node("output", output_node)

    # Define Flow
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "story")
    workflow.add_edge("story", "shots")

    # Conditional branching
    workflow.add_conditional_edges(
        "shots",
        should_refine,
        {
            "refine": "refine",
            "output": "narration"  # Go to narration instead of output
        }
    )

    # After refinement, generate narrations
    workflow.add_edge("refine", "narration")

    # Narration goes to output
    workflow.add_edge("narration", "output")
    workflow.add_edge("output", END)

    return workflow.compile()