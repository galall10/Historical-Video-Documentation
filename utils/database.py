import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
def get_mongo_uri():
    """Get MongoDB URI, reloading from environment each time."""
    load_dotenv()  # Reload environment variables
    return os.getenv("MONGO_URI", "mongodb://localhost:27017/historical_videos")

MONGO_URI = get_mongo_uri()
DB_NAME = "landmark_db"
LANDMARKS_COLLECTION_NAME = "landmarks"
VIDEOS_COLLECTION_NAME = "cached_videos"

# --- Global Variables ---
client = None
db = None
landmarks_collection = None

def connect_to_db():
    """Establishes a connection to MongoDB and returns collections."""
    global client, db, landmarks_collection, videos_collection

    # Get fresh URI each time
    current_uri = get_mongo_uri()

    if not current_uri:
        print("ERROR: MONGO_URI is not set in the .env file.")
        print("Please make sure your .env file contains: MONGO_URI=mongodb://localhost:27017/historical_videos")
        return None, None, None

    try:
        print(f"Attempting to connect to MongoDB at {current_uri}...")

        # Close existing connection if any
        if client:
            try:
                client.close()
            except:
                pass

        # Create new connection
        client = MongoClient(current_uri)
        db = client[DB_NAME]

        # Test the connection
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB!")

        # Get collections
        landmarks_collection = db[LANDMARKS_COLLECTION_NAME]
        videos_collection = db[VIDEOS_COLLECTION_NAME]

        # Create collections if they don't exist
        try:
            db.create_collection(LANDMARKS_COLLECTION_NAME)
            db.create_collection(VIDEOS_COLLECTION_NAME)
            print(f"Database '{DB_NAME}' and collections '{LANDMARKS_COLLECTION_NAME}', '{VIDEOS_COLLECTION_NAME}' are ready.")
        except:
            print(f"Collections already exist in database '{DB_NAME}'.")

        return landmarks_collection, videos_collection, db

    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please check your internet connection and MongoDB server status.")
        landmarks_collection, videos_collection, db = None, None, None
        return None, None, None
    except ConfigurationError as e:
        print(f"MongoDB configuration error: {e}")
        landmarks_collection, videos_collection, db = None, None, None
        return None, None, None
    except Exception as e:
        print(f"Unexpected error connecting to MongoDB: {e}")
        landmarks_collection, videos_collection, db = None, None, None
        return None, None, None


def get_collections():
    """Get current collections, connecting if necessary."""
    global landmarks_collection, videos_collection, db

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
    landmarks_collection, videos_collection, db = get_collections()
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

