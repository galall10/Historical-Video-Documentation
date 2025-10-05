"""
Agent state definitions for the LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """State for the Historical Building to Video Story workflow"""

    # Input
    image_base64: str  # Base64 encoded image of the historical building
    api_provider: str  # API provider (openrouter, openai, anthropic, etc.)

    # Processing stages
    image_analysis: str  # Detection and detailed description of the building
    created_telling_story: str  # Generated historical narrative
    shots_description: List[Dict[str, Any]]  # List of video shots with details

    # Refinement
    refinement_notes: List[str]  # Feedback for shot refinement
    iteration_count: int  # Number of refinement iterations

    # Output
    final_output: str  # JSON string of complete output

    # Workflow management
    messages: List[str]  # Status messages - REMOVED operator.add!
    progress_log: str  # Detailed progress tracking

    # Debug fields (optional)
    _debug_raw_response: str  # Raw LLM response for debugging
    _debug_cleaned_response: str  # Cleaned response for debugging