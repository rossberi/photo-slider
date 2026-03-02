from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import random

interval = (int(os.getenv("SLIDESHOW_INTERVAL", 10)) * 1000)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    image_folder = "static/images"
    images = [
        f"/static/images/{img}"
        for img in os.listdir(image_folder)
        if img.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    random.shuffle(images)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "images": images, "interval": interval},
    )