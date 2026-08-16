import asyncio
import json
import sys
from types import SimpleNamespace

from app.ollama_client import analyze_with_ollama, normalize_analysis


def test_normalize_analysis_fills_missing_fields():
    analysis = normalize_analysis({"tasks": [{"title": "Call dentist", "priority": "urgent"}]})

    assert analysis["summary"] == "Here is what SchedMate found."
    assert analysis["tasks"] == [
        {
            "title": "Call dentist",
            "deadline": "unknown",
            "priority": "medium",
            "reason": "No reason provided.",
        }
    ]
    assert analysis["next_actions"] == []


def test_normalize_analysis_keeps_valid_priorities_and_actions():
    analysis = normalize_analysis(
        {
            "summary": "Two tasks need attention.",
            "tasks": [{"title": "Pay rent", "deadline": "tomorrow", "priority": "high", "reason": "Due soon"}],
            "next_actions": ["Pay rent first", ""],
        }
    )

    assert analysis["tasks"][0]["priority"] == "high"
    assert analysis["next_actions"] == ["Pay rent first"]


def test_analyze_with_ollama_uses_confirmed_default_model(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": json.dumps(
                    {
                        "summary": "One task found.",
                        "tasks": [{"title": "Call Sam", "deadline": "today", "priority": "medium", "reason": "Requested"}],
                        "next_actions": ["Call Sam today"],
                    }
                )
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return FakeResponse()

    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setitem(sys.modules, "httpx", SimpleNamespace(AsyncClient=FakeAsyncClient, HTTPError=Exception))

    analysis = asyncio.run(analyze_with_ollama("call Sam today"))

    assert captured["url"] == "http://localhost:11434/api/generate"
    assert captured["json"]["model"] == "gemma3:4b"
    assert captured["json"]["stream"] is False
    assert analysis["next_actions"] == ["Call Sam today"]
