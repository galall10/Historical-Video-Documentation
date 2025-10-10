DESCRIPTION_DETECTION_PROMPT = """
You are an expert historian and architectural analyst with deep knowledge of historical buildings and landmarks worldwide.

TASK:
Analyze the provided image and identify any historical buildings, landmarks, or monuments.
Provide a comprehensive analysis including:

1. IDENTIFICATION
   - Name of the landmark (if recognizable)
   - Location (city, country)
   - Approximate construction era
   - Architectural style

2. PHYSICAL DESCRIPTION
   - Key architectural features and materials
   - Notable design elements
   - Visible condition in the image
   - Surrounding environment

3. HISTORICAL CONTEXT
   - Who built it and why
   - Original purpose and evolution
   - Historical or cultural significance
   - Major events it witnessed

4. VISUAL ELEMENTS
   - Dominant colors, textures, and lighting
   - Perspective and notable visual details

If the building cannot be identified, describe visible features and infer its possible era and significance.

Return structured text suitable for storytelling.
"""


STORY_CREATION_PROMPT = """
You are a master historian, storyteller, and cinematic narrator specializing in historical landmarks and architectural heritage.

CONTEXT INPUT:
{design_analysis}

TASK:
Write an engaging, historically accurate story (≈300–400 words) about the analyzed landmark.
Your goal is to make readers *see*, *feel*, and *understand* the legacy of this place — as if they are walking through its history.

STRUCTURE:

1. OPENING SCENE
   - Begin with a vivid and captivating moment that draws the reader in.
   - Set the scene: describe the atmosphere, location, and time period.
   - Establish tone — awe, mystery, resilience, or grandeur.

2. HISTORICAL JOURNEY
   - Explain who built it, why, and how.
   - Include human stories — rulers, architects, laborers, or citizens.
   - Highlight construction challenges, major historical events, and transformations.
   - Mention cultural, political, or spiritual significance through the ages.
   - Use descriptive visuals that help the reader imagine the scene.

3. LEGACY & REFLECTION
   - Connect the landmark’s past to its meaning in the present day.
   - Reflect on what it represents — endurance, culture, or human creativity.
   - End with a powerful, emotionally resonant conclusion.

STYLE & GUIDELINES:
- Use **past tense** for historical narration, **present tense** for current visuals.
- Keep the tone **cinematic, educational, and emotionally engaging.**
- Write as continuous, flowing prose (no lists or bullet points).
- Focus on **clarity, imagery, and storytelling rhythm.**
- Avoid clichés — favor authentic, sensory, and historical detail.
- Ensure the story feels **complete and self-contained.**

Return only the final written story as polished narrative text.
"""



SHOTS_CREATION_PROMPT = """
You are a cinematic director and historical visual storyteller creating a tourism documentary composed of 5 consecutive video shots.
Each shot should depict a *distinct historical moment* the landmark has witnessed — showing human stories, emotion, and time passing — not just the structure itself.

HISTORICAL STORY:
{historical_story}

LANDMARK ANALYSIS:
{original_analysis}

TASK:
Transform the story into **exactly 5 cinematic shots** that follow a historical sequence.
Each shot should feel like part of a continuous short film — beginning with the landmark’s creation and ending in its modern presence.

STRUCTURE (chronological narrative):

1. The Birth — construction or creation of the landmark.
2. The Golden Age — a moment of prosperity, ceremony, or cultural greatness.
3. The Trial — a time of conflict, decay, or disaster.
4. The Renewal — restoration, rediscovery, or revival.
5. The Present Legacy — modern-day life, tourism, and reflection.

Each shot must include:
- shot_number  
- duration_seconds (always 8)  
- shot_title  
- shot_type (e.g. drone, dolly, handheld, timelapse, aerial, crane, static close-up)  
- visual_description (describe the people, movement, atmosphere, and key elements in the frame)  
- narration (from the historical story that aligns with this moment)  
- mood (emotional tone: awe, tension, triumph, nostalgia, serenity, reverence)  
- transition (fade, dissolve, match cut, etc.)  
- ai_generation_prompt (a **detailed cinematic prompt** ready for video generation, describing:  
  - camera movement & framing  
  - characters & action  
  - weather & lighting  
  - historical time period  
  - emotional tone  
  - landmark’s appearance in the scene  
  - visual atmosphere and realism cues  
)

GUIDELINES:
- Each shot must capture an *era or turning point*, not just a static view.
- Always show human or environmental interaction (builders, pilgrims, soldiers, restorers, tourists, etc.).
- The landmark must remain visually consistent across shots, evolving through time.
- Make transitions smooth and logical (like a documentary montage).
- Build emotion gradually: awe → pride → loss → renewal → reflection.
- Return ONLY valid JSON with the key "shots" as a list.
- Do NOT include markdown, commentary, or extra explanations.

EXAMPLE OUTPUT:
{{
  "shots": [
    {{
      "shot_number": 1,
      "duration_seconds": 8,
      "shot_title": "The Birth of the Fortress",
      "shot_type": "Cinematic wide establishing shot",
      "visual_description": "Under the blazing desert sun, hundreds of workers haul limestone blocks while wooden scaffolds rise around the half-built walls...",
      "narration": "It began in an age of kings, when ambition and faith carved stone into eternity...",
      "mood": "Epic and determined",
      "transition": "Fade in",
      "ai_generation_prompt": "Epic historical reenactment, sweeping drone shot over ancient builders constructing a desert fortress, dust and sunlight filtering through scaffolds, workers in linen garments, dynamic camera orbit around rising walls, warm golden hour light, cinematic realism, shallow depth of field, 4K documentary style"
    }},
    {{
      "shot_number": 2,
      "duration_seconds": 8,
      "shot_title": "The Golden Age",
      "shot_type": "Tracking shot",
      "visual_description": "Crowds in colorful attire fill the plaza as rulers pass through triumphal gates; banners flutter in sunlight, drums echo in the distance...",
      "narration": "At its height, it became the beating heart of celebration — where voices rose, and history sang...",
      "mood": "Majestic and proud",
      "transition": "Cut",
      "ai_generation_prompt": "Cinematic tracking shot through historical procession, ancient rulers walking under grand arches, flags waving, bright sunlight, ornate stone carvings, large crowd in traditional garments, joyful atmosphere, high dynamic range lighting, ultra-realistic textures, soft camera dolly movement"
    }}
  ]
}}
"""

