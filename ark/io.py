from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS = {"event_id", "run_id", "timestamp", "kind", "name"}


def load_trace(path: str | Path) -> list[dict]:
    """Load a JSONL trace and report the exact line on malformed input."""
    source = Path(path)
    events: list[dict] = []
    with source.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("each JSONL record must be an object")
                missing = REQUIRED_FIELDS - event.keys()
                if missing:
                    raise ValueError(f"missing fields: {sorted(missing)}")
                events.append(event)
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(f"invalid trace at {source}:{line_number}: {exc}") from exc
    return events
