from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps
from pathlib import Path
import os
import random
import asyncio
import shutil

interval = int(os.getenv("SLIDESHOW_INTERVAL", 10)) * 1000
THUMB_DIR = Path("static/thumbs")


def create_thumbnail(src: Path) -> None:
    dest = THUMB_DIR / src.with_suffix(".jpg").name
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.thumbnail((2560 , 1440))
        img.save(dest, "JPEG", quality=75, optimize=True, progressive=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    shutil.rmtree(THUMB_DIR, ignore_errors=True)
    THUMB_DIR.mkdir()

    loop = asyncio.get_event_loop()
    images = [
        f
        for f in Path("static/images").iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    for img in images:
        await loop.run_in_executor(None, create_thumbnail, img)
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    images = [
        f"/static/thumbs/{f.name}"
        for f in THUMB_DIR.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    random.shuffle(images)
    return templates.TemplateResponse(
        "index.html", {"request": request, "images": images, "interval": interval}
    )
