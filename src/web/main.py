from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import Config
from services.broker import RabbitMQBroker
from services.broker.publisher import Producer, Publisher
from services.cache import ValkeyCache
from services.models import GetArtistSongsRequest
from services.search import SearchService
from services.store import Store

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

connection = RabbitMQBroker(Config.BROKER_URL)
store = Store(Config.DATABASE_URL)
cache = ValkeyCache(Config.CACHE_URL)
publisher = Publisher(connection)
publisher.register_producer(Producer(queue_name=Config.QUEUE_SEARCH_ARTISTS))
publisher.register_producer(Producer(queue_name=Config.QUEUE_GET_ARTIST_SONGS))

search_service = SearchService(cache=cache, publisher=publisher, store=store)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search-artist")
async def search_artists(request: Request):
    form_data = await request.form()
    artist_name = form_data.get("artist-name").strip()
    if not artist_name:
        return templates.TemplateResponse(
            "search-artist-result.html",
            {"request": request, "found_artists": []},
        )

    return templates.TemplateResponse(
        "search-artist-result.html",
        {
            "request": request,
            "found_artists": search_service.search_artist_by_name(artist_name),
        },
    )


@app.post("/search-lyrics/{artist_id}")
async def search_lyrics(request: Request, artist_id: str):
    publisher.get_artist_songs(GetArtistSongsRequest(artist_id=artist_id))
    return "In progress"
