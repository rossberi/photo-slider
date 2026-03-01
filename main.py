from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import random

token = os.environ.get("TOKEN")
if not token:
    raise Exception("TOKEN not set")

hostname = os.environ.get("HOSTNAME")
if not hostname:
    raise Exception("HOSTNAME not set")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def restrict_access(request: Request, call_next):
    allowed_path = f"/{token}"

    request_host = request.headers.get("host", "")
    if request_host != hostname:
        return Response(status_code=404)

    path = request.url.path
    if path != allowed_path and not path.startswith("/static/"):
        return Response(status_code=404)

    return await call_next(request)

@app.get(f"/{token}", response_class=HTMLResponse)
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
        {"request": request, "images": images}
    )