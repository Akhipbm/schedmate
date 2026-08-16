from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .ollama_client import OllamaError, analyze_with_ollama

app = FastAPI(title="SchedMate", description="Turn messy notes into a practical action plan.")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, messy_text: str = Form(...)) -> HTMLResponse:
    cleaned_text = messy_text.strip()
    context = {"request": request, "messy_text": messy_text}

    if not cleaned_text:
        context["error"] = "Paste a few notes first so SchedMate has something to organize."
        return templates.TemplateResponse("index.html", context, status_code=400)

    try:
        context["analysis"] = await analyze_with_ollama(cleaned_text)
    except OllamaError as exc:
        context["error"] = str(exc)
        context["hint"] = "Make sure Ollama is running and the configured model is available."

    return templates.TemplateResponse("index.html", context)
