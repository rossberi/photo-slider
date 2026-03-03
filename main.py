from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps
from pathlib import Path
import os
import random
import shutil
import asyncio

interval = int(os.getenv("SLIDESHOW_INTERVAL", 10)) * 1000
use_thumbs = os.getenv("USE_THUMBS", "false").lower() == "true"
thumb_dir = Path("static/thumbs")


def create_thumbnail(src: Path) -> None:
    dest = thumb_dir / src.with_suffix(".jpg").name
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.thumbnail((2560, 1440))
        img.save(dest, "JPEG", quality=75, optimize=True, progressive=True)


async def process_images():
    loop = asyncio.get_event_loop()
    images = [
        f
        for f in Path("static/images").iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    for img in images:
        await loop.run_in_executor(None, create_thumbnail, img)
        await asyncio.sleep(0)  # anderen Tasks Luft lassen


@asynccontextmanager
async def lifespan(app: FastAPI):
    if use_thumbs:
        shutil.rmtree(thumb_dir, ignore_errors=True)
        thumb_dir.mkdir()
        asyncio.create_task(process_images())
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

if use_thumbs:
    image_path = thumb_dir
else:
    image_path = Path("static/images")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    images = [
        f"{image_path}/{f.name}"
        for f in image_path.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    random.shuffle(images)
    return templates.TemplateResponse(
        "index.html", {"request": request, "images": images, "interval": interval}
    )
