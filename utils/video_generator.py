import os
import time
import requests
from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
from .database import get_cached_video, save_cached_video, get_video_cache_stats


# CONFIGURATION
dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"


# MAIN FUNCTION
def generate_video_with_wan(
    prompt: str,
    output_path: str = "generated_video.mp4",
    size: str = "832*480",
    retries: int = 3,
    wait_between_retries: int = 3
):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ DASHSCOPE_API_KEY not found. Please add it to your .env file.")

    print("🎬 Generating video with WAN 2.2-t2v-plus...")
    print(f"🧠 Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print(f"📐 Target size: {size}")

    # Send generation request
    rsp = VideoSynthesis.call(
        api_key=api_key,
        model="wan2.2-t2v-plus",
        prompt=prompt,
        prompt_extend=True,
        size=size,
        negative_prompt="",
        watermark=False,
        seed=12345
    )

    if rsp.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f"❌ Video generation failed.\n"
            f"Status Code: {rsp.status_code}\n"
            f"Error Code: {rsp.code}\n"
            f"Message: {rsp.message}"
        )

    video_url = getattr(rsp.output, "video_url", None)
    if not video_url:
        raise RuntimeError("⚠️ No video URL returned by DashScope API.")

    print("✅ Video generated successfully!")
    print("🔗 Video URL:", video_url)

    # Attempt to download the video file
    for attempt in range(1, retries + 1):
        try:
            print(f"⬇️ Downloading video (attempt {attempt}/{retries})...")
            response = requests.get(video_url, timeout=60)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"💾 Video saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"⚠️ Download attempt {attempt} failed: {e}")
            if attempt < retries:
                print(f"⏳ Retrying in {wait_between_retries} seconds...")
                time.sleep(wait_between_retries)
            else:
                raise RuntimeError(f"❌ Failed to download video after {retries} attempts: {e}")

    raise RuntimeError("❌ Unknown error: Video generation process did not complete successfully.")


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
        # Generate the video
        video_path = generate_video_with_wan(prompt, output_path, size)

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
