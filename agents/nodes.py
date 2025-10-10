import json
from langchain_core.messages import HumanMessage, SystemMessage
from models.state import AgentState
from utils.llm_factory import initialize_llm
from prompts.templates import *
import asyncio
import edge_tts
import os


async def generate_narration_audio(text: str, output_path: str, voice: str = "en-GB-RyanNeural"):
    """Generate audio narration using Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def narration_generation_node(state: AgentState) -> AgentState:
    """Generate audio narration for each shot using Edge TTS."""
    state["progress_log"] = state.get("progress_log", "") + "Generating narrations...\n"
    shots = state.get("shots_description", [])

    if not shots:
        state["messages"].append("Error: No shots available for narration.")
        state["progress_log"] += "ERROR: Missing shots.\n"
        return state

    os.makedirs("narrations", exist_ok=True)

    try:
        for i, shot in enumerate(shots):
            narration_text = shot.get("narration", "")
            if not narration_text:
                state["messages"].append(f"Warning: Shot {i + 1} has no narration text.")
                continue

            audio_path = f"narrations/shot_{i + 1}_narration.mp3"

            # Run async function in sync context
            asyncio.run(generate_narration_audio(narration_text, audio_path))

            # Store audio path in shot data
            shot["audio_path"] = audio_path

        state["messages"].append(f"✅ Generated {len(shots)} narration audio files.")
        state["progress_log"] += "Narration generation complete.\n"

    except Exception as e:
        state["messages"].append(f"Narration generation failed: {str(e)}")
        state["progress_log"] += f"ERROR: {str(e)}\n"

    return state

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


def extract_landmark_name_node(state: AgentState) -> AgentState:
    """Extract the landmark name from the image analysis text."""
    state["progress_log"] = state.get("progress_log", "") + "Extracting landmark name...\n"
    image_analysis = state.get("image_analysis", "")

    if not image_analysis:
        state["messages"].append("Error: No image analysis available to extract landmark name.")
        state["progress_log"] += "ERROR: Missing image analysis for name extraction.\n"
        state["landmark_name"] = "Unknown"
        return state

    landmark_name = "Unknown"

    try:
        # First, try using LLM to extract the landmark name
        llm = initialize_llm()
        prompt = LANDMARK_NAME_EXTRACTION_PROMPT.format(image_analysis=image_analysis)
        messages = [
            SystemMessage(content="You are a text analysis expert specializing in historical landmarks and monuments. Extract the specific landmark name from the description."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        llm_extracted_name = response.content.strip()

        # Clean up the response
        llm_extracted_name = llm_extracted_name.strip('"\'').strip()

        print(f"DEBUG: LLM extracted name: '{llm_extracted_name}'")
        print(f"DEBUG: Image analysis: '{image_analysis[:200]}...'")

        # If LLM gave a specific name, use it
        if llm_extracted_name and llm_extracted_name.lower() not in ["unknown", "unnamed", "unidentified", "not specified", "could not determine"]:
            landmark_name = llm_extracted_name
            state["messages"].append(f"LLM extracted landmark name: {landmark_name}")
        else:
            # If LLM couldn't extract, try keyword-based approach
            state["messages"].append("LLM extraction failed, trying keyword-based approach...")
            landmark_name = find_similar_landmark_in_db(image_analysis)

        # Use user-provided name as final fallback
        user_provided_name = state.get("user_provided_landmark_name")
        if user_provided_name and (landmark_name == "Unknown" or landmark_name.lower() in ["unknown", "unnamed", "unidentified"]):
            landmark_name = user_provided_name
            state["messages"].append(f"Using user-provided landmark name: {landmark_name}")

        # Final validation - ensure we have a valid name
        if not landmark_name or landmark_name.lower() in ["unknown", "unnamed", "unidentified"]:
            state["messages"].append("Warning: Could not extract landmark name from analysis.")
            state["progress_log"] += "WARNING: Landmark name extraction inconclusive.\n"
            landmark_name = "Unknown"
        else:
            state["messages"].append(f"Landmark name extracted: {landmark_name}")
            state["progress_log"] += f"Landmark name found: {landmark_name}\n"

    except Exception as e:
        state["messages"].append(f"Landmark name extraction failed: {str(e)}")
        state["progress_log"] += f"ERROR during name extraction: {str(e)}\n"
        landmark_name = "Unknown"

    state["landmark_name"] = landmark_name
    return state


def find_similar_landmark_in_db(image_analysis: str) -> str:
    """Find similar landmark in database based on description keywords."""
    try:
        from utils.recommendation import load_landmarks

        # Load landmarks data
        landmarks_df = load_landmarks()
        if landmarks_df.empty:
            return "Unknown"

        # Extract keywords from image analysis
        analysis_lower = image_analysis.lower()

        # Expanded keywords list - English only
        keywords = [
            # English landmark names and types
            "pyramid", "giza", "sphinx", "temple", "luxor", "karnak", "abu simbel",
            "philae", "valley of kings", "citadel", "qaitbay", "mosque", "muhammad ali",
            "ibn tulun", "al-azhar", "alexandria", "bibliotheca", "catacombs", "montaza",
            "citadel of saladin", "cairo tower", "egyptian museum", "khan el-khalili",
            "old cairo", "coptic cairo", "high dam", "aswan dam", "unfinished obelisk",
            "nubian museum", "elephantine", "aga khan", "kom ombo", "edfu", "kalabsha",
            "beit el-wali", "dakka", "maharraqa", "souk", "corniche", "nasser lake",
            "sehel", "fatimid cemetery", "pompey's pillar", "ras el-tin", "abu al-abbas",
            "kom el-dikka", "roman theater", "stanley bridge", "opera house",
            "aquarium", "shallalat gardens", "mamoura beach", "agami", "sidi abdel rahman",
            "marsa matruh", "cleopatra beach", "almaza bay", "mount sinai",
            "saint catherine", "sharm el sheikh", "ras muhammad", "dahab", "blue hole",
            "nuweiba", "taba", "hurghada", "giftun island", "el gouna", "soma bay",
            "safaga", "quseir", "marsa alam", "shalateen", "halayeb", "zafarana",
            "siwa oasis", "oracle temple", "cleopatra pool", "shali fortress", "bahariya",
            "white desert", "black desert", "crystal mountain", "farafra", "dakhla",
            "kharga", "hibis temple", "qasr village", "mut", "bagawat", "nadura",
            "labakha", "deir al-hagar", "dush", "roman necropolis", "port said lighthouse",
            "ismailia museum", "bubastis", "damietta", "natrun", "macarius",
            "mit ghamr", "tanta", "mansoura", "zagazig", "banha", "qalyub",
            "shibin", "esna", "khnum temple", "silsila", "sohag", "minya",
            "assiut", "qena", "paul's monastery", "coloured canyon", "fjord bay",
            "mahmya", "gawhara palace", "ras el bar", "manzala", "degla",
            "rayan", "faiyum", "meidum", "hawara", "lahun", "karanis",
            "madi", "qarun", "bernice", "hormos", "soknopaiou", "tebtunis",
            # Additional descriptive keywords
            "ancient", "historical", "pharaonic", "roman", "islamic", "coptic",
            "museum", "palace", "fortress", "castle", "tower", "bridge",
            "garden", "park", "beach", "desert", "oasis", "mountain",
            "valley", "river", "lake", "island", "bay", "sea",
            "monastery", "church", "cathedral"
        ]

        # Find matching landmarks with scoring
        matches = []
        for _, landmark in landmarks_df.iterrows():
            landmark_name = landmark.get('name', '').lower()
            landmark_category = landmark.get('category', '').lower()
            score = 0

            # Check for exact keyword matches
            for keyword in keywords:
                # Direct keyword matching
                if keyword in landmark_name or keyword in landmark_category:
                    score += 3  # Higher score for direct matches

                # Check if keyword appears in analysis
                if keyword in analysis_lower:
                    score += 1  # Lower score for analysis matches

            if score > 0:
                matches.append((landmark.get('name', 'Unknown'), score))

        if matches:
            # Sort by score (highest first) and return the best match
            matches.sort(key=lambda x: x[1], reverse=True)
            best_match = matches[0][0]
            print(f"DEBUG: Keyword-based match found: '{best_match}' with score {matches[0][1]}")
            return best_match

        print("DEBUG: No keyword matches found in database")

    except Exception as e:
        print(f"Error finding similar landmark: {e}")

    return "Unknown"


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


def video_generation_node(state: AgentState) -> AgentState:
    """Generate or retrieve cached video for the landmark story."""
    state["progress_log"] = state.get("progress_log", "") + "Generating video...\n"

    landmark_name = state.get("landmark_name", "Unknown")
    story_content = state.get("created_telling_story", "")

    if not story_content:
        state["messages"].append("❌ No story content available for video generation.")
        state["progress_log"] += "ERROR: Missing story content.\n"
        return state

    try:
        from utils.video_generator import generate_or_get_cached_video

        # Create video generation prompt
        video_prompt = f"""
        Create a cinematic educational video about {landmark_name}.
        The video should be visually stunning and tell the story of this historical landmark.
        Include scenes of the landmark, historical context, and educational narration.
        Video style: Documentary, educational, visually appealing.
        Duration: 30-60 seconds.
        Quality: High definition.

        Story content: {story_content[:500]}...
        """

        # Try to get cached video first, or generate new one
        video_path, was_cached = generate_or_get_cached_video(
            landmark_name=landmark_name,
            prompt=video_prompt,
            story_type="educational",
            force_regenerate=False
        )

        if was_cached:
            state["messages"].append(f"✅ Retrieved cached video for {landmark_name}")
            state["progress_log"] += f"Video retrieved from cache: {video_path}\n"
        else:
            state["messages"].append(f"🎬 Generated new video for {landmark_name}")
            state["progress_log"] += f"New video generated: {video_path}\n"

        state["generated_video_path"] = video_path
        state["video_cached"] = was_cached

    except Exception as e:
        state["messages"].append(f"❌ Video generation failed: {str(e)}")
        state["progress_log"] += f"ERROR during video generation: {str(e)}\n"
        state["generated_video_path"] = ""

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
        "generated_video": state.get("generated_video_path", ""),
        "video_cached": state.get("video_cached", False),
        "status": "complete"
    }

    state["final_output"] = json.dumps(final_output, indent=2)
    state["messages"].append("Pipeline complete.")
    state["progress_log"] += "All tasks finished successfully.\n"

    return state
