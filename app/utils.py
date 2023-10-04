import os
import cv2
import io
import aiohttp
import aiofiles
import base64
import numpy as np

from PIL import Image, ImageDraw, ImageFilter
from math import pi
from urllib.request import urlretrieve
from typing import Union
from ffmpeg.asyncio import FFmpeg

from .config import settings
from .types import Numeric


async def request_dalle_image(prompt: str) -> Image.Image:
    """
    Requests an image from the DALL-E API.

    Parameters
    ----------
    prompt: str
        Prompt to generate the image from

    Returns
    -------
    PIL.Image.Image
        Generated image
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("API key is not set in environment variable OPENAI_API_KEY")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            },
            json={
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
            },
        ) as response:
            if not response.ok:
                response.raise_for_status()
            json_result = await response.json()

        async with session.get(json_result["data"][0]["url"]) as response:
            if not response.ok:
                response.raise_for_status()
            image_bytes = await response.content.read()

    return Image.open(io.BytesIO(image_bytes))


async def request_stability_image(prompt: str) -> Image.Image:
    """
    Requests an image from the Stability API.

    Parameters
    ----------
    prompt: str
        Prompt to generate the image from

    Returns
    -------
    dict[str, str]
        Dictionary containing the base64 encoded image
    """
    if not settings.STABILITY_API_KEY:
        raise ValueError("API key is not set in environment variable STABILITY_API_KEY")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
            },
            json={
                "steps": 40,
                "width": 1024,
                "height": 1024,
                "seed": 0,
                "cfg_scale": 5,
                "samples": 1,
                "text_prompts": [
                    {"text": prompt, "weight": 1},
                    {"text": "blurry, bad", "weight": -1},
                ],
            },
        ) as response:
            if not response.ok:
                raise Exception("Non-200 response: " + str(response.text))
            json_result = await response.json()

    return Image.open(
        io.BytesIO(base64.b64decode(json_result["artifacts"][0]["base64"]))
    )


def get_dnn_superres(upscale_factor: int = 3) -> cv2.dnn_superres.DnnSuperResImpl:
    """
    Returns a DNN Super Resolution model for the given upscale factor.

    Parameters
    ----------
    upscale_factor: int
        Upscale factor for the model (only 2x, 3x, and 4x are supported)

    Returns
    -------
    cv2.dnn_superres.DnnSuperResImpl
        Super Resolution Model
    """
    if upscale_factor not in range(2, 5):
        raise ValueError(
            f"Upscale factor must be between 2 and 4, got {upscale_factor}"
        )

    # Download the pretrained model
    filename = f"ESPCN_x{upscale_factor}.pb"
    if not os.path.exists(f"/tmp/{filename}"):
        urlretrieve(
            f"https://github.com/fannymonori/TF-ESPCN/raw/master/export/{filename}",
            f"/tmp/{filename}",
        )

    sr = cv2.dnn_superres.DnnSuperResImpl().create()
    sr.readModel(f"/tmp/{filename}")
    sr.setModel("espcn", upscale_factor)

    return sr


def crop_circle_fade(
    image: Image.Image, blur_factor: Numeric = 4.0, radius_factor: Numeric = 1.4
) -> Image.Image:
    """
    Crops a circle from the center of the image and applies a Gaussian blur to the edges.

    Parameters
    ----------
    image: PIL.Image.Image
        Image to crop
    blur_factor: float
        Factor to control the amount of blur applied to the edges of the circle
    radius_factor: float
        Factor to control the size of the circle to crop

    Returns
    -------
    PIL.Image.Image
        Cropped and blurred image
    """
    # Create a blank white mask the size of the image
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # Calculate the center and the radius for the circle
    width, height = image.size
    center_x, center_y = width // 2, height // 2
    radius = (
        min(center_x, center_y) / radius_factor
    )  # so that the circle fits completely in the image

    # Draw a filled circle in the mask
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=255,
    )

    # Apply a Gaussian blur to the mask to create a fade effect
    mask = mask.filter(ImageFilter.GaussianBlur(radius // blur_factor))

    # Create a black image of the same size as the original image
    black = Image.new("RGB", image.size, (0, 0, 0))

    # Composite the original image with the black image using the blurred mask
    result = Image.composite(image, black, mask)

    return result


def get_rad(theta: Numeric, phi: Numeric, gamma: Numeric) -> tuple[float, float, float]:
    return (
        deg_to_rad(theta),
        deg_to_rad(phi),
        deg_to_rad(gamma),
    )


def deg_to_rad(deg: Numeric) -> float:
    return deg * pi / 180.0


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Converts a PIL image to an OpenCV image.

    Parameters
    ----------
    pil_image: PIL.Image.Image
        PIL image to convert

    Returns
    -------
    np.ndarray
        OpenCV image
    """
    # Convert PIL image to numpy array
    numpy_image = np.array(pil_image)

    # Convert RGB to BGR
    cv2_image = numpy_image[:, :, ::-1].copy()

    return cv2_image


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """
    Converts a OpenCV image to a PIL image.

    Parameters
    ----------
    cv2_image: np.ndarray
        OpenCV image to convert

    Returns
    -------
    PIL.Image.Image
        PIL image
    """
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

    # Convert the opencv image to PIL format
    pil_image = Image.fromarray(rgb_image)

    return pil_image


async def write_rotating_video(
    image: np.ndarray | Image.Image, output_video_path: str
) -> None:
    """
    Output a rotating video of the image rotating around the y-axis

    Parameters
    ----------
    image: np.ndarray | PIL.Image.Image
        Base image to convert into video
    output_video_path: str
        Path to output video
    """
    if isinstance(image, Image.Image):
        w, h = image.size
    elif isinstance(image, np.ndarray):
        w, h = image.shape[:2]
    else:
        raise ValueError("Image needs to be a numpy array or PIL image format")

    transform = PerspectiveTransformer(image)
    async with aiofiles.tempfile.NamedTemporaryFile("w+b") as tmp:
        for phi in range(360):
            rotated_image = transform.rotate_along_axis(phi=phi, dx=5)
            raw_frame = cv2_to_pil(rotated_image).tobytes()
            await tmp.write(raw_frame)

        process = (
            FFmpeg()
            .option("y")
            .input(
                tmp.name,
                options={
                    "f": "rawvideo",
                    "pix_fmt": "rgb24",
                    "s": f"{w}x{h}",
                },
            )
            .output(
                output_video_path,
                options={
                    "c:v": "libx264",
                    "pix_fmt": "yuv420p",
                    "movflags": "+faststart",
                },
                preset="fast",
            )
        )
        await process.execute()


class PerspectiveTransformer:
    """
    Perspective transformation class for images

    Parameters
    ----------
    image: np.ndarray | PIL.Image.Image
        Image to be transformed
    """

    def __init__(self, image: Union[Image.Image, np.ndarray]) -> None:
        if isinstance(image, Image.Image):
            self.image = pil_to_cv2(image)
        elif isinstance(image, np.ndarray):
            self.image = image
        else:
            raise ValueError("Image needs to be a numpy array or PIL image format")

        if not len(self.image.shape) == 3:
            raise ValueError(
                f"Image needs to be a 3-dim array, got {len(self.image.shape)}-dim"
            )

        self.height, self.width, self.num_channels = self.image.shape

    def rotate_along_axis(
        self,
        theta: Numeric = 0,
        phi: Numeric = 0,
        gamma: Numeric = 0,
        dx: Numeric = 0,
        dy: Numeric = 0,
        dz: Numeric = 0,
    ) -> np.ndarray:
        """
        Wrapper of Rotating a Image
        """
        # Get radius of rotation along 3 axes
        rtheta, rphi, rgamma = get_rad(theta, phi, gamma)

        # Get ideal focal length on z axis
        # NOTE: Change this section to other axis if needed
        d = np.sqrt(self.height**2 + self.width**2)
        self.focal = d / (2 * np.sin(rgamma) if np.sin(rgamma) != 0 else 1)
        dz = self.focal

        # Get projection matrix
        mat = self.get_M(rtheta, rphi, rgamma, dx, dy, dz)

        return cv2.warpPerspective(self.image, mat, (self.width, self.height))

    def get_M(
        self,
        theta: Numeric,
        phi: Numeric,
        gamma: Numeric,
        dx: Numeric,
        dy: Numeric,
        dz: Numeric,
    ) -> np.ndarray:
        """
        Get Perspective Projection Matrix
        """
        w = self.width
        h = self.height
        f = self.focal

        # Projection 2D -> 3D matrix
        A1 = np.array([[1, 0, -w / 2], [0, 1, -h / 2], [0, 0, 1], [0, 0, 1]])

        # Rotation matrices around the X, Y, and Z axis
        RX = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), -np.sin(theta), 0],
                [0, np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        RY = np.array(
            [
                [np.cos(phi), 0, -np.sin(phi), 0],
                [0, 1, 0, 0],
                [np.sin(phi), 0, np.cos(phi), 0],
                [0, 0, 0, 1],
            ]
        )

        RZ = np.array(
            [
                [np.cos(gamma), -np.sin(gamma), 0, 0],
                [np.sin(gamma), np.cos(gamma), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        # Composed rotation matrix with (RX, RY, RZ)
        R = np.dot(np.dot(RX, RY), RZ)

        # Translation matrix
        T = np.array([[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]])

        # Projection 3D -> 2D matrix
        A2 = np.array([[f, 0, w / 2, 0], [0, f, h / 2, 0], [0, 0, 1, 0]])

        # Final transformation matrix
        return np.dot(A2, np.dot(T, np.dot(R, A1)))
