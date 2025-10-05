"""
LangGraph workflow for Historical Building Video Story Generation
"""
from langgraph.graph import StateGraph, END
from models.state import AgentState
from agents.nodes import (
    detect_description_node,
    story_telling_node,
    shots_creation_node,
    refine_shots_node,
    output_node
)


def should_refine(state: AgentState) -> str:
    """Conditional edge to determine if refinement is needed"""
    refinement_notes = state.get("refinement_notes", [])
    iteration_count = state.get("iteration_count", 0)

    # Skip refinement if no notes or max iterations reached
    if not refinement_notes or iteration_count >= 3:
        return "output"
    return "refine"


def create_workflow() -> StateGraph:
    """Create and configure the LangGraph workflow"""

    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("detect", detect_description_node)
    workflow.add_node("story", story_telling_node)
    workflow.add_node("shots", shots_creation_node)
    workflow.add_node("refine", refine_shots_node)
    workflow.add_node("output", output_node)

    # Define edges - IMPORTANT: Each node should only be called once per path
    workflow.set_entry_point("detect")
    workflow.add_edge("detect", "story")
    workflow.add_edge("story", "shots")

    # Conditional edge for refinement
    workflow.add_conditional_edges(
        "shots",
        should_refine,
        {
            "refine": "refine",
            "output": "output"
        }
    )

    # After refinement, go to output
    workflow.add_edge("refine", "output")

    # Output is the end
    workflow.add_edge("output", END)

    return workflow.compile()