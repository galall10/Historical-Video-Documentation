import pandas as pd
from haversine import haversine, Unit
import json
import os
from difflib import SequenceMatcher

# Import MongoDB - required for the system to work
try:
    from .database import get_collections
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    get_collections = None

def load_landmarks():
    """Load landmarks from MongoDB - no fallback system."""
    print("Loading landmarks from database...")

    if not MONGODB_AVAILABLE or get_collections is None:
        print("MongoDB not available - cannot load landmarks")
        return pd.DataFrame()

    try:
        # Get collections
        landmarks_collection, videos_collection, db = get_collections()

        if landmarks_collection is None:
            print("Failed to get landmarks collection")
            return pd.DataFrame()

        print("Fetching data from MongoDB...")
        landmarks = list(landmarks_collection.find({}, {"_id": 0}))
        print(f"Successfully loaded {len(landmarks)} landmarks from MongoDB")
        return pd.DataFrame(landmarks)
    except Exception as e:
        print(f"Error loading landmarks: {e}")
        print(f"   Error type: {type(e).__name__}")
        return pd.DataFrame()

def fuzzy_match_landmark(landmark_name: str, landmarks_df: pd.DataFrame, threshold: float = 0.6) -> pd.DataFrame:
    """Find landmarks using fuzzy string matching for better accuracy with Arabic/English names."""
    matches = []

    for _, landmark in landmarks_df.iterrows():
        landmark_name_db = landmark.get('name', '')

        # Calculate similarity ratio
        similarity = SequenceMatcher(None, landmark_name.lower(), landmark_name_db.lower()).ratio()

        # Also check for partial matches within words
        name_words = landmark_name.lower().split()
        db_words = landmark_name_db.lower().split()

        max_partial_similarity = 0
        for word1 in name_words:
            for word2 in db_words:
                partial_sim = SequenceMatcher(None, word1, word2).ratio()
                max_partial_similarity = max(max_partial_similarity, partial_sim)

        # Use the better of full similarity or partial similarity
        best_similarity = max(similarity, max_partial_similarity)

        if best_similarity >= threshold:
            matches.append((landmark, best_similarity))

    # Sort by similarity score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)

    if matches:
        # Return the best match
        return pd.DataFrame([matches[0][0]])

    return pd.DataFrame()


def get_recommendations(landmark_name: str, landmarks_df: pd.DataFrame, top_n: int = 5, category: str = None):
    """Get the top N closest landmarks based on a landmark name, with an optional category filter."""

    # Clean and normalize the landmark name
    cleaned_name = landmark_name.strip().lower()

    # Try different variations of the name for better matching
    name_variations = [
        cleaned_name,
        cleaned_name.replace('the ', ''),  # Remove "the" if present
        cleaned_name.replace('great ', ''),  # Remove "great" if present
        cleaned_name.replace('great pyramids of giza', 'pyramids of giza'),  # Special case for Giza
        cleaned_name.replace('the great ', ''),  # Remove "the great" if present
        cleaned_name.replace(' pyramids', ''),  # Remove "pyramids" for better matching
        cleaned_name.replace(' temple', ''),  # Remove "temple" for better matching
        cleaned_name.replace(' mosque', ''),  # Remove "mosque" for better matching
    ]

    # Find the landmark by name in the database (case-insensitive)
    target_landmark = None

    for variation in name_variations:
        # Exact match first
        target_landmark = landmarks_df[landmarks_df["name"].str.lower() == variation]
        if not target_landmark.empty:
            break

        # Partial match (contains) - more flexible
        target_landmark = landmarks_df[landmarks_df["name"].str.lower().str.contains(variation, na=False)]
        if not target_landmark.empty:
            break

    # If no match found, try fuzzy matching
    if target_landmark is None or target_landmark.empty:
        target_landmark = fuzzy_match_landmark(landmark_name, landmarks_df, threshold=0.6)

    if target_landmark is None or target_landmark.empty:
        return pd.DataFrame() # Return empty DataFrame if landmark not found

    target_landmark = target_landmark.iloc[0]
    target_coords = (target_landmark["latitude"], target_landmark["longitude"])

    # Make a copy to avoid modifying the original DataFrame
    filtered_landmarks = landmarks_df.copy()

    # Remove the target landmark itself from recommendations
    filtered_landmarks = filtered_landmarks[filtered_landmarks["name"].str.lower() != target_landmark["name"].lower()]

    # Filter by category if provided
    if category and category.lower() != 'all':
        # Case-insensitive filtering
        filtered_landmarks = filtered_landmarks[filtered_landmarks['category'].str.lower() == category.lower()]

    if filtered_landmarks.empty:
        return pd.DataFrame() # Return empty DataFrame if no landmarks match the category

    # Calculate distances
    distances = [
        haversine(target_coords, (row["latitude"], row["longitude"]), unit=Unit.KILOMETERS)
        for index, row in filtered_landmarks.iterrows()
    ]

    # Add distances to the DataFrame and sort
    filtered_landmarks['distance_km'] = distances
    recommendations = filtered_landmarks.sort_values(by="distance_km").head(top_n)

    return recommendations
