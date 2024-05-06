import tempfile
from pathlib import Path

import aiofiles
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from .config import settings
from .models import PromptBody
from .utils import (
    crop_circle_fade,
    request_dalle_image,
    request_stability_image,
    write_rotating_video,
)

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


@app.post(
    "/video",
    response_class=Response,
    responses={200: {"content": {"video/mp4": {}}}},
)
async def generate_video(body: PromptBody) -> Response:
    if settings.IMAGE_BACKEND == 'dalle':
        image = await request_dalle_image(body.prompt)
    elif settings.IMAGE_BACKEND == 'stability':
        image = await request_stability_image(body.prompt)
    else:
        raise ValueError(f"Invalid image backend: {settings.IMAGE_BACKEND}")

    image = crop_circle_fade(image, radius_factor=1.5)

    with tempfile.TemporaryDirectory() as tmpdir:
        await write_rotating_video(image, f"{tmpdir}/out.mp4")
        async with aiofiles.open(f"{tmpdir}/out.mp4", "rb") as f:
            video_bytes = await f.read()

    return Response(video_bytes, media_type="video/mp4")
