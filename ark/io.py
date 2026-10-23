from __future__ import annotations

import json
import math
from pathlib import Path

REQUIRED_FIELDS = {"event_id", "run_id", "timestamp", "kind", "name"}
STRING_FIELDS = ("event_id", "run_id", "timestamp", "kind", "name")


def _validate_event(event: dict, source: Path, line_number: int) -> None:
    missing = REQUIRED_FIELDS - event.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")

    for field in STRING_FIELDS:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    if "inputs" in event and not isinstance(event["inputs"], dict):
        raise ValueError("inputs must be a JSON object")
    if "metadata" in event and not isinstance(event["metadata"], dict):
        raise ValueError("metadata must be a JSON object")

    if "duration_ms" in event and event["duration_ms"] is not None:
        value = event["duration_ms"]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError("duration_ms must be a finite non-negative number or null")

    if "token_usage" in event and event["token_usage"] is not None:
        usage = event["token_usage"]
        if not isinstance(usage, dict):
            raise ValueError("token_usage must be a JSON object or null")
        for counter_name, value in usage.items():
            if (
                not isinstance(counter_name, str)
                or not counter_name.strip()
                or not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError("token_usage counters must have non-empty names and non-negative integer values")


def load_trace(path: str | Path) -> list[dict]:
    """Load a JSONL trace and validate its schema with line-specific errors."""
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
                _validate_event(event, source, line_number)
                events.append(event)
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(f"invalid trace at {source}:{line_number}: {exc}") from exc
    return events
