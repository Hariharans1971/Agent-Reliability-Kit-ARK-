from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class TraceRecorder:
    """Collect events for one agent run and persist them as JSON Lines."""

    def __init__(self, name: str, tags: dict[str, str] | None = None):
        if not name.strip():
            raise ValueError("run name cannot be empty")
        self.name = name
        self.run_id = str(uuid4())
        self.tags = tags or {}
        self.events: list[dict[str, Any]] = []

    def record(
        self,
        kind: str,
        name: str,
        inputs: dict[str, Any] | None = None,
        outputs: Any = None,
        duration_ms: float | None = None,
        token_usage: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not kind.strip() or not name.strip():
            raise ValueError("kind and name cannot be empty")
        if duration_ms is not None and duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
        if token_usage and any(not isinstance(v, int) or v < 0 for v in token_usage.values()):
            raise ValueError("token usage counters must be non-negative integers")
        event = {
            "event_id": str(uuid4()),
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "name": name,
            "inputs": inputs or {},
            "outputs": outputs,
            "duration_ms": duration_ms,
            "token_usage": token_usage or {},
            "metadata": {"run_name": self.name, "tags": self.tags, **(metadata or {})},
        }
        # Fail early for values that cannot be encoded as JSON.
        json.dumps(event, ensure_ascii=False)
        self.events.append(event)
        return event

    def save(self, path: str | Path) -> Path:
        """Write one JSON event per line and return the destination path."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as stream:
            for event in self.events:
                stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return target
