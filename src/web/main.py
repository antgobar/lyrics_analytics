from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from common.config import Config
from common.store import Store

CURRENT_DIRECTORY = Path.cwd()
templates = Jinja2Templates(directory=CURRENT_DIRECTORY / "src" / "templates")
static_files = StaticFiles(directory=CURRENT_DIRECTORY / "src" / "static")


app = FastAPI()
app.mount("/static", static_files, name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = Store(Config.DATABASE_URL)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "artists": store.list_artists()},
    )


@app.post("/search-artists")
async def search_artists(request: Request):
    await request.form()
