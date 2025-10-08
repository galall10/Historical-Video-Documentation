import os
import requests
from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

def generate_video_with_wan(prompt: str, output_path: str = "generated_video.mp4", size: str = "832*480"):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ DASHSCOPE_API_KEY not found. Please add it to your .env file.")

    print("🎬 Generating video with Wan2.5-t2v-preview... Please wait...")

    rsp = VideoSynthesis.call(
        api_key=api_key,
        model="wan2.5-t2v-preview",
        prompt=prompt,
        prompt_extend=True,
        size=size,
        negative_prompt="",
        watermark=False,
        seed=12345
    )

    if rsp.status_code == HTTPStatus.OK:
        video_url = rsp.output.video_url
        print("✅ Video generated successfully!")
        print("🔗 Video URL:", video_url)

        try:
            response = requests.get(video_url)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"💾 Video saved to {output_path}")
            return output_path
        except Exception as e:
            raise RuntimeError(f"⚠️ Failed to download video: {e}")

    else:
        raise RuntimeError(
            f"❌ Video generation failed.\n"
            f"Status Code: {rsp.status_code}\n"
            f"Error Code: {rsp.code}\n"
            f"Message: {rsp.message}\n"
        )
