import base64
import io
import tempfile
import aiofiles
from pathlib import Path
from fastapi import FastAPI, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse


from PIL import Image

from .utils import request_image, crop_circle_fade, write_rotating_video

BASE_PATH = Path(__file__).resolve().parent

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_PATH / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get(
    "/video",
    response_class=Response,
    responses={200: {"content": {"video/mp4": {}}}},
)
async def generate_video(prompt: str) -> Response:
    response = await request_image(prompt)
    image = Image.open(io.BytesIO(base64.b64decode(response["artifacts"][0]["base64"])))
    image = crop_circle_fade(image, radius_factor=1.5)

    with tempfile.TemporaryDirectory() as tmpdir:
        await write_rotating_video(image, f"{tmpdir}/out.mp4")
        async with aiofiles.open(f"{tmpdir}/out.mp4", "rb") as f:
            video_bytes = await f.read()

    return Response(video_bytes, media_type="video/mp4")
