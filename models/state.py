"""
Agent state definitions for the LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    """Workflow state for the Historical Building → Video Story process"""

    # Input
    image_base64: str          # Base64-encoded image of the landmark
    api_provider: str          # Selected API provider (e.g., gemini, openrouter)

    # Processing stages
    image_analysis: str        # Historical and architectural analysis
    landmark_name: str         # Name of the detected landmark
    created_telling_story: str # Generated educational narrative
    shots_description: List[Dict[str, Any]]  # List of generated video shots

    # Refinement
    refinement_notes: List[str] # Notes or feedback for improving shots
    iteration_count: int        # Number of refinement iterations completed

    # Output
    final_output: str           # Final combined output in JSON

    # Workflow tracking
    messages: List[str]         # Status messages through pipeline stages
    progress_log: str           # Text log for progress updates

    # Debug fields (optional)
    _debug_raw_response: str    # Raw LLM output for debugging
    _debug_cleaned_response: str# Parsed or cleaned response for debugging
