from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes.generate import router as generate_router

app = FastAPI(title="AI Android Generator App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory (optional for future assets)
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

templates = Jinja2Templates(directory="backend/app/web/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})

app.include_router(generate_router)