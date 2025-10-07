"""
Video generation utility using the free Wan2.1 model hosted on Hugging Face.
No API key is needed.
"""

from gradio_client import Client
import time
import requests

def generate_video_with_wan(prompt: str, output_path: str = "generated_video.mp4"):
    """
    Generate a short video from a text prompt using Wan2.1.
    Returns the path or URL to the generated video.
    """
    try:
        print("🎬 Starting Wan2.1 video generation...")
        client = Client("Wan-AI/Wan2.1")

        # Start video generation asynchronously
        task_info = client.predict(
            prompt=prompt,
            size="1280*720",
            watermark_wan=True,
            seed=-1,
            api_name="/t2v_generation_async"
        )

        task_id = task_info.get("task_id", None)
        if not task_id:
            raise RuntimeError("❌ No task_id returned from model")

        print(f"⏳ Task started (ID: {task_id}). Waiting for video to be ready...")

        # Poll for status until the video is ready
        for _ in range(20):
            time.sleep(10)
            status = client.predict(task_id, api_name="/status_refresh")
            video_url = status.get("video", None)

            if video_url:
                print("✅ Video generation complete:", video_url)
                # Download the video
                video_data = requests.get(video_url).content
                with open(output_path, "wb") as f:
                    f.write(video_data)
                print(f"💾 Saved locally to {output_path}")
                return output_path

        raise TimeoutError("⏰ Video generation timed out after waiting too long.")

    except Exception as e:
        print(f"❌ Failed to generate video: {e}")
        return None
