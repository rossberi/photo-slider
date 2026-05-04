import os, random, time
from pathlib import Path
from PIL import Image, ImageOps
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

IMG_DIR = Path("static/images")
THUMB_DIR = Path("static/thumbs")
THUMB_DIR.mkdir(parents=True, exist_ok=True)
INTERVAL = int(os.getenv("SLIDESHOW_INTERVAL", 10)) * 1000


def get_or_create_thumb(img_path: Path) -> str:
    thumb_path = THUMB_DIR / f"thumb_{img_path.name}"

    # Nur komprimieren, wenn das Thumbnail noch nicht existiert
    if not thumb_path.exists():
        with Image.open(img_path) as img:
            img = ImageOps.exif_transpose(img)  # Korrigiert Rotation
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((2560, 1440))
            img.save(thumb_path, "JPEG", quality=80, optimize=True)

    return f"/static/thumbs/{thumb_path.name}"


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "interval": INTERVAL}
    )


@app.get("/random-image")
async def get_random_image():
    images = [
        f for f in IMG_DIR.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    if not images:
        return RedirectResponse(url="/static/placeholder.jpg")

    selected_img = random.choice(images)
    thumb_url = get_or_create_thumb(selected_img)

    return RedirectResponse(url=f"{thumb_url}?t={time.time()}")
