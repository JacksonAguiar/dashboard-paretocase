from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
_EVENT_DETAILS_PATH = _BASE_DIR / "EVENT-DETAILS.md"

_event_context: str | None = None


def get_event_context() -> str:
    global _event_context
    if _event_context is None:
        _event_context = _EVENT_DETAILS_PATH.read_text(encoding="utf-8")
    return _event_context