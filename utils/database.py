import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "landmark_db"
LANDMARKS_COLLECTION_NAME = "landmarks"
VIDEOS_COLLECTION_NAME = "cached_videos"

# --- Global Variables ---
client = None
db = None
landmarks_collection = None
videos_collection = None

def connect_to_db():
    """Establishes a connection to MongoDB and returns collections."""
    global client, db, landmarks_collection, videos_collection

    if not MONGO_URI:
        print("ERROR: MONGO_URI is not set in the .env file.")
        print("Please make sure your .env file contains: MONGO_URI=mongodb://localhost:27017")
        return None, None, None

    try:
        print(f"Attempting to connect to MongoDB at {MONGO_URI}...")
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,  # 5 seconds timeout
            connectTimeoutMS=30000,         # 30 seconds connection timeout
            socketTimeoutMS=None,           # No timeout for operations
            connect=False                   # Defer connection until first operation
        )
        client.admin.command('ismaster')
        print("Successfully connected to MongoDB Atlas!")

        db = client[DB_NAME]
        landmarks_collection = db[LANDMARKS_COLLECTION_NAME]
        videos_collection = db[VIDEOS_COLLECTION_NAME]
        print(f"Database '{DB_NAME}' and collections '{LANDMARKS_COLLECTION_NAME}', '{VIDEOS_COLLECTION_NAME}' are ready.")

        return landmarks_collection, videos_collection, db

    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Database connection failed: {e}")
        print("\nPlease check the following:")
        print("1. Your internet connection.")
        print("2. The MONGO_URI in your .env file is correct.")
        print("3. Your current IP address is whitelisted in MongoDB Atlas Network Access.")
        print("4. Your system's DNS settings are correct (try using 8.8.8.8).")
        client = None
        db = None
        landmarks_collection = None
        videos_collection = None
        return None, None, None


def get_collections():
    """Get current collections, connecting if necessary."""
    if landmarks_collection is None or videos_collection is None:
        print("Reconnecting to database...")
        connect_to_db()
    return landmarks_collection, videos_collection, db

# --- Video Caching Functions ---

def get_cached_video(landmark_name, story_type="default"):
    """Check if a video exists in cache for the given landmark and story type."""
    if videos_collection is None:
        return None

    try:
        video_doc = videos_collection.find_one({
            "landmark_name": landmark_name.lower(),
            "story_type": story_type
        })
        return video_doc
    except Exception as e:
        print(f"Error retrieving cached video: {e}")
        return None

def save_cached_video(landmark_name, story_type, video_path, metadata=None):
    """Save a generated video to cache."""
    if videos_collection is None:
        print("Videos collection not available")
        return False

    try:
        video_doc = {
            "landmark_name": landmark_name.lower(),
            "story_type": story_type,
            "video_path": video_path,
            "metadata": metadata or {},
            "created_at": __import__('datetime').datetime.utcnow()
        }

        result = videos_collection.insert_one(video_doc)
        print(f"Video cached successfully with ID: {result.inserted_id}")
        return True
    except Exception as e:
        print(f"Error saving cached video: {e}")
        return False

def update_cached_video(landmark_name, story_type, video_path, metadata=None):
    """Update an existing cached video."""
    if videos_collection is None:
        return False

    try:
        result = videos_collection.update_one(
            {
                "landmark_name": landmark_name.lower(),
                "story_type": story_type
            },
            {
                "$set": {
                    "video_path": video_path,
                    "metadata": metadata or {},
                    "updated_at": __import__('datetime').datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating cached video: {e}")
        return False

def delete_cached_video(landmark_name, story_type):
    """Delete a cached video."""
    if videos_collection is None:
        return False

    try:
        result = videos_collection.delete_one({
            "landmark_name": landmark_name.lower(),
            "story_type": story_type
        })
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting cached video: {e}")
        return False

def get_video_cache_stats():
    """Get statistics about the video cache."""
    if videos_collection is None:
        return None

    try:
        total_videos = videos_collection.count_documents({})
        unique_landmarks = len(videos_collection.distinct("landmark_name"))

        return {
            "total_videos": total_videos,
            "unique_landmarks": unique_landmarks
        }
    except Exception as e:
        print(f"Error getting cache stats: {e}")
        return None

