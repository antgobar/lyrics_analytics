import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

CURRENT_DIRECTORY = os.getcwd()
templates = Jinja2Templates(directory=os.path.join(CURRENT_DIRECTORY, "src", "templates"))
static_files = StaticFiles(directory=os.path.join(CURRENT_DIRECTORY, "src", "static"))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", static_files, name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/")
def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})
