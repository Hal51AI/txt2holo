import tempfile
import aiofiles

from pathlib import Path
from fastapi import FastAPI, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse


from .config import settings
from .utils import crop_circle_fade, write_rotating_video

if settings.IMAGE_API == "stability":
    from .utils import request_stability_image as request_image
elif settings.IMAGE_API == "dalle":
    from .utils import request_dalle_image as request_image
else:
    raise ValueError(f"Unknown IMAGE_API name, got: {settings.IMAGE_API}")

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
    image = await request_image(prompt)
    image = crop_circle_fade(image, radius_factor=1.5)

    with tempfile.TemporaryDirectory() as tmpdir:
        await write_rotating_video(image, f"{tmpdir}/out.mp4")
        async with aiofiles.open(f"{tmpdir}/out.mp4", "rb") as f:
            video_bytes = await f.read()

    return Response(video_bytes, media_type="video/mp4")
