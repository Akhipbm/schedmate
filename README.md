# SchedMate

SchedMate is a tiny FastAPI web app that turns messy everyday notes into a prioritized action plan with Ollama.

## Features

- Paste free-form notes into a simple web form.
- Uses Ollama's `/api/generate` endpoint to extract tasks, deadlines, and priorities.
- Displays a summary, task cards, and recommended next actions.
- No database, accounts, or background workers.

## Setup

1. Install Python dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Start Ollama and make sure a model is available:

   ```bash
   ollama pull gemma3:4b
   ollama serve
   ```

3. Run SchedMate:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Open <http://127.0.0.1:8000>.

## Configuration

Environment variables:

- `OLLAMA_BASE_URL` defaults to `http://localhost:11434`.
- `OLLAMA_MODEL` defaults to `gemma3:4b`.
- `OLLAMA_TIMEOUT` defaults to `30` seconds.
