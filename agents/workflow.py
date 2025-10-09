"""
LangGraph Workflow Definition
"""
from langgraph.graph import StateGraph, END
from models.state import AgentState
from agents.nodes import (
    detect_description_node,
    story_telling_node,
    shots_creation_node,
    refine_shots_node,
    video_generation_node,
    output_node
)


def should_refine(state: AgentState) -> str:
    """
    Conditional edge to determine if refinement is needed

    Args:
        state: Current agent state

    Returns:
        "refine" if refinement needed, "video_generation" otherwise
    """
    refinement_notes = state.get("refinement_notes", [])
    iteration_count = state.get("iteration_count", 0)

    # Skip refinement if no notes or max iterations reached
    if not refinement_notes or iteration_count >= 3:
        return "video_generation"
    return "refine"


def create_workflow() -> StateGraph:
    """
    Create and configure the LangGraph workflow for historical building video generation

    Workflow steps:
    1. Detect and analyze the building from image
    2. Create a historical narrative story
    3. Generate video shot descriptions
    4. Optional: Refine shots based on user feedback
    5. Generate video clips from shots
    6. Compile final output

    Returns:
        Compiled StateGraph workflow
    """
    # Initialize the graph with AgentState
    workflow = StateGraph(AgentState)

    # Add all nodes to the workflow
    workflow.add_node("detect", detect_description_node)
    workflow.add_node("story", story_telling_node)
    workflow.add_node("shots", shots_creation_node)
    workflow.add_node("refine", refine_shots_node)
    workflow.add_node("video_generation", video_generation_node)
    workflow.add_node("output", output_node)

    # Define the workflow edges
    # Start with detection
    workflow.set_entry_point("detect")

    # Linear flow from detection to story to shots
    workflow.add_edge("detect", "story")
    workflow.add_edge("story", "shots")

    # Conditional edge: decide whether to refine or go to video generation
    workflow.add_conditional_edges(
        "shots",
        should_refine,
        {
            "refine": "refine",
            "video_generation": "video_generation"
        }
    )

    # After refinement, go to video generation
    workflow.add_edge("refine", "video_generation")

    # After video generation, create final output
    workflow.add_edge("video_generation", "output")

    # End after output
    workflow.add_edge("output", END)

    # Compile and return the workflow
    return workflow.compile()
