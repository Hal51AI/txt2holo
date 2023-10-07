import tempfile
import aiofiles

from pathlib import Path
from fastapi import FastAPI, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse


from .utils import (
    crop_circle_fade,
    write_rotating_video,
    request_dalle_image,
    request_stability_image,
)
from .models import PromptBody


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
    if body.backend == "dalle":
        image = await request_dalle_image(body.prompt)
    elif body.backend == "stability":
        image = await request_stability_image(body.prompt)
    else:
        raise ValueError(f"Invalid image backend: {body.backend}")

    image = crop_circle_fade(image, radius_factor=1.5)

    with tempfile.TemporaryDirectory() as tmpdir:
        await write_rotating_video(image, f"{tmpdir}/out.mp4")
        async with aiofiles.open(f"{tmpdir}/out.mp4", "rb") as f:
            video_bytes = await f.read()

    return Response(video_bytes, media_type="video/mp4")
