from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from common.broker import Connection
from common.config import Config
from common.publisher import Producer, Publisher
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

connection = Connection(Config.BROKER_URL)
store = Store(Config.DATABASE_URL)

publisher = Publisher(connection)
publisher.register_producers([Producer(queue_name=Config.QUEUE_SEARCH_ARTISTS)])


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "artists": store.list_artists()},
    )


@app.post("/search-artist")
async def search_artists(request: Request):
    form_data = await request.form()
    artist_name = form_data.get("artist-name")
    if not artist_name:
        return templates.TemplateResponse(
            "search-artist-result.html",
            {"request": request, "found_artists": []},
        )

    publisher.send_message(Config.QUEUE_SEARCH_ARTISTS, {"artist_name": artist_name})
    return templates.TemplateResponse(
        "search-artist-result.html",
        {"request": request, "found_artists": store.search_artists(artist_name)},
    )
