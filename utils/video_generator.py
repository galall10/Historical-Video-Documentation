import os
import time
from google import genai
from config import VEO_MODEL


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

    # Initialize the Google GenAI client
    client = genai.Client(api_key=api_key)

    # Start Veo video generation
    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=prompt,
    )

    # Poll the operation until it finishes or times out
    elapsed = 0
    timeout = timeout_minutes * 60

    while not operation.done:
        if elapsed >= timeout:
            raise TimeoutError(f"⚠️ Timeout reached ({timeout_minutes} minutes). Generation aborted.")
        print("⏳ Waiting for video generation to complete...")
        time.sleep(poll_interval)
        elapsed += poll_interval
        operation = client.operations.get(operation)

    # Download the generated video.
    generated_video = operation.response.generated_videos[0]
    client.files.download(file=generated_video.video)
    generated_video.video.save(output_path)

    print(f"💾 Video saved to {output_path}")
    return output_path
