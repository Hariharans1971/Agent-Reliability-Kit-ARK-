from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

_ALLOWED_KEYS = {
    "required_events",
    "forbidden_events",
    "min_events",
    "max_events",
    "max_total_duration_ms",
    "max_total_tokens",
    "max_calls_per_event",
}


def load_policy(path: str | Path) -> dict[str, Any]:
    """Load and validate a small JSON policy contract."""
    source = Path(path)
    try:
        policy = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid policy JSON in {source}: {exc}") from exc

    if not isinstance(policy, dict):
        raise ValueError("policy must be a JSON object")

    unknown = policy.keys() - _ALLOWED_KEYS
    if unknown:
        raise ValueError(f"unsupported policy keys: {sorted(unknown)}")

    for key in ("required_events", "forbidden_events"):
        value = policy.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            raise ValueError(f"{key} must be a list of non-empty strings")

    for key in ("min_events", "max_events", "max_total_tokens"):
        if key in policy and (not isinstance(policy[key], int) or isinstance(policy[key], bool) or policy[key] < 0):
            raise ValueError(f"{key} must be a non-negative integer")

    if "max_total_duration_ms" in policy:
        value = policy["max_total_duration_ms"]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ValueError("max_total_duration_ms must be a finite non-negative number")

    if "max_calls_per_event" in policy:
        value = policy["max_calls_per_event"]
        if not isinstance(value, dict):
            raise ValueError("max_calls_per_event must be an object mapping event names to integer limits")
        for name, limit in value.items():
            if not isinstance(name, str) or not name.strip() or not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
                raise ValueError("max_calls_per_event keys must be non-empty names and values non-negative integers")

    if "min_events" in policy and "max_events" in policy and policy["min_events"] > policy["max_events"]:
        raise ValueError("min_events cannot be greater than max_events")

    return policy


def evaluate_policy(events: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate trace events against declarative, deterministic rules."""
    names = [event.get("name") for event in events]
    name_counts = Counter(names)
    results: list[dict[str, Any]] = []

    def add(name: str, passed: bool, message: str) -> None:
        results.append({"name": name, "passed": bool(passed), "message": message})

    if "min_events" in policy:
        limit = policy["min_events"]
        add("min_events", len(events) >= limit, f"expected at least {limit} events; found {len(events)}")
    if "max_events" in policy:
        limit = policy["max_events"]
        add("max_events", len(events) <= limit, f"expected at most {limit} events; found {len(events)}")

    for name in policy.get("required_events", []):
        add(f"required_event:{name}", name in name_counts, f"{'found' if name in name_counts else 'missing'} required event {name!r}")
    for name in policy.get("forbidden_events", []):
        add(f"forbidden_event:{name}", name not in name_counts, f"{'forbidden event found' if name in name_counts else 'forbidden event absent'}: {name!r}")

    if "max_total_duration_ms" in policy:
        durations = []
        for index, event in enumerate(events):
            value = event.get("duration_ms")
            if value is None:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                raise ValueError(f"event {index} has an invalid duration_ms value")
            durations.append(value)
        total = sum(durations)
        limit = policy["max_total_duration_ms"]
        add("max_total_duration_ms", total <= limit, f"recorded duration {total:g} ms; limit {limit:g} ms")

    if "max_total_tokens" in policy:
        total_tokens = 0
        for index, event in enumerate(events):
            usage = event.get("token_usage") or {}
            if not isinstance(usage, dict):
                raise ValueError(f"event {index} token_usage must be an object")
            for counter_name, value in usage.items():
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"event {index} has invalid token counter {counter_name!r}")
            # Many providers include total_tokens alongside input/output breakdowns.
            # Prefer the aggregate to avoid counting those components twice.
            if "total_tokens" in usage:
                total_tokens += usage["total_tokens"]
            else:
                total_tokens += sum(usage.values())
        limit = policy["max_total_tokens"]
        add("max_total_tokens", total_tokens <= limit, f"recorded token count {total_tokens}; limit {limit}")

    for event_name, limit in policy.get("max_calls_per_event", {}).items():
        count = name_counts[event_name]
        add(f"max_calls:{event_name}", count <= limit, f"event {event_name!r} occurred {count} time(s); limit {limit}")

    if not results:
        add("policy_has_rules", False, "policy contains no checks")
    return results
