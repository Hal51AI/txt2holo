import base64
import io
import tempfile
from fastapi import FastAPI, Response
from PIL import Image

from .utils import request_image, crop_circle_fade, write_rotating_video

app = FastAPI()


@app.get(
    "/video",
    response_class=Response,
    responses={200: {"content": {"application/octet-stream": {}}}},
)
async def generate_video(prompt: str):
    response = request_image(prompt)
    image = Image.open(io.BytesIO(base64.b64decode(response["artifacts"][0]["base64"])))
    image = crop_circle_fade(image, radius_factor=1.5)
    with tempfile.TemporaryDirectory() as tmpdir:
        write_rotating_video(image, f"{tmpdir}/out.mp4")
        with open(f"{tmpdir}/out.mp4", "rb") as f:
            video_bytes = f.read()
    return Response(video_bytes, media_type="application/octet-stream")
