import os
import time
import requests
from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope


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

    print("🎬 Generating video with wan2.1-t2v-turbo...")
    print(f"🧠 Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print(f"📐 Target size: {size}")

    # Send generation request
    rsp = VideoSynthesis.call(
        api_key=api_key,
        model="wan2.1-t2v-turbo",
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
