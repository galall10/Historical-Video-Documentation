# 1. DESCRIPTION DETECTION PROMPT
DESCRIPTION_DETECTION_PROMPT = """
You are an expert historian and architectural analyst with deep knowledge of historical buildings and landmarks worldwide.

TASK: Analyze the provided image and identify any historical buildings, landmarks, or monuments.

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

# 2. STORY CREATION PROMPT
STORY_CREATION_PROMPT = """
You are a historian and storyteller creating educational narratives for students.

BUILDING ANALYSIS:
{design_analysis}

TASK: Write a 1–2 minute story (≈300–400 words) that is engaging, cinematic, and factual.

The story should include:

1. OPENING HOOK (≈30s)
   - Introduce a captivating moment or question
   - Set the scene vividly (time, place, atmosphere)

2. HISTORICAL JOURNEY (≈1 min)
   - Explain why and how the landmark was built
   - Mention challenges, construction, and key events
   - Include notable historical figures
   - Describe restorations and evolution over time

3. EDUCATIONAL CLOSURE (≈30s)
   - Reflect on the landmark's modern significance
   - End with an inspiring and educational message

GUIDELINES:
- Use past tense for historical events, present tense for visuals
- Keep tone clear, cinematic, and educational
- Avoid jargon and ensure smooth transitions
- Return as continuous narrative text; do not use bullet points or lists
"""

# 3. VIDEO SHOTS CREATION PROMPT
SHOTS_CREATION_PROMPT = """
You are a documentary director. Convert the historical story into exactly 5 cinematic shots, each representing a distinct act or event in the landmark’s history.

HISTORICAL NARRATIVE:
{historical_story}

BUILDING ANALYSIS:
{original_analysis}

TASK:
- Generate exactly 5 shots corresponding to key acts or events:
  1. Vision & Construction
  2. Time of Greatness
  3. Challenges & Decline
  4. Rediscovery & Preservation
  5. Legacy & Learning
- Each shot = 5 seconds
- Include for each shot: shot_number, duration_seconds, shot_type, visual_description, narration, mood, transition, ai_generation_prompt
- Use narration directly from the story
- Shots must show action, human activity, or changes over time — not static landmarks
- Include a variety of shot types (wide, medium, close-up, aerial/establishing)
- Return ONLY valid JSON with key "shots" as a list
- Do NOT include explanations, Markdown, or extra text

OUTPUT EXAMPLE:
{{
  "shots": [
    {{
      "shot_number": 1,
      "duration_seconds": 5,
      "shot_type": "Establishing shot",
      "visual_description": "Pharaoh overseeing the initial construction site, workers hauling stone, dust in the sunlight...",
      "narration": "At the dawn of its creation, the vision of the great monument began...",
      "mood": "Epic and ambitious",
      "transition": "Fade in",
      "ai_generation_prompt": "Wide aerial shot, ancient construction site, workers, sunlight, cinematic"
    }},
    {{
      "shot_number": 2,
      "duration_seconds": 5,
      "shot_type": "Medium shot",
      "visual_description": "People celebrating during the golden age, rituals and festivities around the landmark...",
      "narration": "During its golden age, the landmark stood as a symbol of culture and power...",
      "mood": "Festive and majestic",
      "transition": "Cut",
      "ai_generation_prompt": "Medium shot, people celebrating, landmark in background, daytime"
    }},
    ... 3 more shots for the remaining acts
  ]
}}
"""


# 4. LANDMARK NAME EXTRACTION PROMPT
LANDMARK_NAME_EXTRACTION_PROMPT = """
You are a text analysis expert specializing in historical landmarks and monuments.

ANALYSIS TEXT:
{image_analysis}

TASK:
- Carefully read the analysis text and identify the name of the historical landmark or monument mentioned.
- Look for: building names, monument names, site names, or any specific historical structures.
- Return ONLY the landmark name in English if possible, or the most specific name mentioned.
- If multiple landmarks are mentioned, choose the primary/main one.
- If no specific landmark name is found, return "Unknown".

IMPORTANT:
- Return just the name, nothing else
- Be specific: prefer "Great Pyramid of Giza" over just "pyramid"
- If the text mentions "the pyramid" or similar generic terms, look for more context
- Check for Arabic names and transliterate them to English if needed

EXAMPLES:
- Input: "This is the Great Pyramid of Giza in Egypt, built by Pharaoh Khufu..."
- Output: "Great Pyramid of Giza"

- Input: "The image shows a large ancient pyramid structure..."
- Output: "Unknown"

- Input: "هرم سقارة في مصر يُعد من أقدم الأهرامات في التاريخ..."
- Output: "Saqqara Pyramid"
"""

