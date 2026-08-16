from __future__ import annotations

import json
import os
from typing import Any


DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1"


class OllamaError(RuntimeError):
    """Raised when Ollama cannot return a usable schedule analysis."""


async def analyze_with_ollama(text: str) -> dict[str, Any]:
    """Ask Ollama to extract tasks, deadlines, priorities, and next actions."""
    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL).rstrip("/")
    model = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    timeout = float(os.getenv("OLLAMA_TIMEOUT", "30"))

    prompt = f"""
You are SchedMate, a practical scheduling assistant.
Read the messy everyday text below and return ONLY valid JSON with this shape:
{{
  "summary": "one sentence overview",
  "tasks": [
    {{"title": "task name", "deadline": "date/time or unknown", "priority": "high|medium|low", "reason": "short reason"}}
  ],
  "next_actions": ["concrete recommended action in order"]
}}
Infer priorities from urgency, consequences, and explicit wording. Use "unknown" when a deadline is absent.

Text:
{text}
""".strip()

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }

    import httpx

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{base_url}/api/generate", json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise OllamaError(f"Could not reach Ollama at {base_url}: {exc}") from exc

    raw_response = response.json().get("response", "")
    try:
        analysis = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise OllamaError("Ollama returned a response that was not valid JSON.") from exc

    return normalize_analysis(analysis)


def normalize_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    """Keep template rendering predictable even when the model omits fields."""
    tasks = analysis.get("tasks") if isinstance(analysis.get("tasks"), list) else []
    normalized_tasks: list[dict[str, str]] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        normalized_tasks.append(
            {
                "title": str(task.get("title") or "Untitled task"),
                "deadline": str(task.get("deadline") or "unknown"),
                "priority": normalize_priority(str(task.get("priority") or "medium")),
                "reason": str(task.get("reason") or "No reason provided."),
            }
        )

    next_actions = analysis.get("next_actions") if isinstance(analysis.get("next_actions"), list) else []
    normalized_actions = [str(action) for action in next_actions if str(action).strip()]

    return {
        "summary": str(analysis.get("summary") or "Here is what SchedMate found."),
        "tasks": normalized_tasks,
        "next_actions": normalized_actions,
    }


def normalize_priority(priority: str) -> str:
    priority = priority.strip().lower()
    if priority in {"high", "medium", "low"}:
        return priority
    return "medium"
