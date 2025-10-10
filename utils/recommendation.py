import pandas as pd
from haversine import haversine, Unit
import json
import os

# Try to import MongoDB, but don't fail if not available
try:
    from .database import get_collections
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    get_collections = None

def load_landmarks():
    """Load landmarks from MongoDB."""
    print("Loading landmarks from database...")

    if not MONGODB_AVAILABLE or get_collections is None:
        print("MongoDB not available")
        return pd.DataFrame()

    try:
        # Get fresh collections directly
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
    ]

    # Find the landmark by name in the database (case-insensitive)
    target_landmark = None

    for variation in name_variations:
        # Exact match first
        target_landmark = landmarks_df[landmarks_df["name"].str.lower() == variation]
        if not target_landmark.empty:
            break

        # Partial match (contains)
        target_landmark = landmarks_df[landmarks_df["name"].str.lower().str.contains(variation, na=False)]
        if not target_landmark.empty:
            break

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
