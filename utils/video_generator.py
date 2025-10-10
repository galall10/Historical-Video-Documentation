import os
import time
from google import genai
from config import VEO_MODEL
from .database import get_cached_video, save_cached_video, get_video_cache_stats


def generate_video_with_veo(
    prompt: str,
    output_path: str = "generated_video.mp4",
    poll_interval: int = 10,
    timeout_minutes: int = 10
):
    """
    Generates a cinematic video using Google's Veo model (veo-3.0-generate-001).
    Saves the final video to `output_path` and returns its path.
    """

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ GOOGLE_API_KEY not found. Please add it to your .env file.")

    print(f"🎬 Generating video with {VEO_MODEL}...")

    client = genai.Client(api_key=api_key)

    # Start Veo job
    operation = client.models.generate_videos(model=VEO_MODEL, prompt=prompt)
    print(f"Operation ID: {operation.name}")

    elapsed = 0
    timeout = timeout_minutes * 60

    # Poll until done
    while not operation.done:
        if elapsed >= timeout:
            raise TimeoutError(f"⚠️ Timeout reached after {timeout_minutes} minutes.")
        print(f"⏳ Waiting... {elapsed}s")
        time.sleep(poll_interval)
        elapsed += poll_interval
        operation = client.operations.get(name=operation.name)

    if not getattr(operation.response, "generated_videos", None):
        raise RuntimeError("❌ No video generated. Maybe Veo filtered your prompt.")

    # Download file
    generated_video = operation.response.generated_videos[0]
    response = client.files.download(file=generated_video.video)
    with open(output_path, "wb") as f:
        f.write(response.read())

    print(f"✅ Video saved to {output_path}")
    return output_path


# CACHING WRAPPER FUNCTION
def generate_or_get_cached_video(
    landmark_name: str,
    prompt: str,
    story_type: str = "default",
    size: str = "832*480",
    force_regenerate: bool = False
):
    """
    Generate a video or retrieve from cache if it exists.

    Args:
        landmark_name: Name of the landmark
        prompt: Video generation prompt
        story_type: Type of story (e.g., "historical", "cultural", "modern")
        size: Video size
        force_regenerate: If True, generate new video even if cached version exists

    Returns:
        tuple: (video_path, was_cached)
    """

    print(f"🔍 Checking cache for video: {landmark_name} ({story_type})")

    # Check cache first (unless forced regeneration)
    if not force_regenerate:
        cached_video = get_cached_video(landmark_name, story_type)
        if cached_video:
            print(f"✅ Found cached video for {landmark_name}")
            return cached_video["video_path"], True

    # Generate new video
    print(f"🎬 Generating new video for {landmark_name}")
    output_path = f"temp_video_{int(time.time())}.mp4"

    try:
        # Generate the video using Veo
        video_path = generate_video_with_veo(prompt, output_path)

        # Save to cache
        metadata = {
            "prompt": prompt,
            "size": size,
            "landmark": landmark_name,
            "story_type": story_type,
            "original_filename": os.path.basename(video_path)
        }

        if save_cached_video(landmark_name, story_type, video_path, metadata):
            print(f"💾 Video cached successfully for {landmark_name}")
        else:
            print(f"⚠️ Failed to cache video for {landmark_name}")

        return video_path, False

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        # Clean up temp file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        raise


def get_video_cache_info():
    """Get information about the video cache."""
    return get_video_cache_stats()


def clear_video_cache(landmark_name: str = None, story_type: str = None):
    """Clear video cache for specific landmark or all videos."""
    from .database import videos_collection

    if videos_collection is None:
        print("❌ Videos collection not available")
        return False

    try:
        if landmark_name and story_type:
            # Delete specific video
            result = videos_collection.delete_one({
                "landmark_name": landmark_name.lower(),
                "story_type": story_type
            })
            print(f"🗑️ Deleted cached video: {landmark_name} ({story_type})")
            return result.deleted_count > 0
        else:
            # Delete all videos
            result = videos_collection.delete_many({})
            print(f"🗑️ Cleared all cached videos ({result.deleted_count} videos)")
            return result.deleted_count > 0

    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False
