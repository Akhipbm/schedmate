from app.ollama_client import normalize_analysis


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
