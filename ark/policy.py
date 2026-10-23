from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

_ALLOWED_KEYS = {
    "allowed_events",
    "required_events",
    "forbidden_events",
    "min_events",
    "max_events",
    "max_total_duration_ms",
    "max_total_tokens",
    "max_calls_per_event",
    "max_duration_ms_per_event",
    "max_tokens_per_event",
}


def _is_non_negative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def _validate_event_names(policy: dict[str, Any], key: str) -> None:
    value = policy.get(key, [])
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{key} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{key} must not contain duplicate event names")


def _validate_named_limits(
    policy: dict[str, Any],
    key: str,
    value_check,
    expected_type: str,
) -> None:
    value = policy.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object mapping event names to {expected_type}")
    for name, limit in value.items():
        if not isinstance(name, str) or not name.strip() or not value_check(limit):
            raise ValueError(f"{key} keys must be non-empty names and values must be {expected_type}")


def load_policy(path: str | Path) -> dict[str, Any]:
    """Load and validate a declarative JSON policy contract."""
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

    for key in ("allowed_events", "required_events", "forbidden_events"):
        _validate_event_names(policy, key)

    for key in ("min_events", "max_events", "max_total_tokens"):
        if key in policy and (
            not isinstance(policy[key], int)
            or isinstance(policy[key], bool)
            or policy[key] < 0
        ):
            raise ValueError(f"{key} must be a non-negative integer")

    if "max_total_duration_ms" in policy and not _is_non_negative_number(
        policy["max_total_duration_ms"]
    ):
        raise ValueError("max_total_duration_ms must be a finite non-negative number")

    _validate_named_limits(
        policy,
        "max_calls_per_event",
        lambda value: isinstance(value, int) and not isinstance(value, bool) and value >= 0,
        "non-negative integers",
    )
    _validate_named_limits(
        policy,
        "max_duration_ms_per_event",
        _is_non_negative_number,
        "finite non-negative numbers",
    )
    _validate_named_limits(
        policy,
        "max_tokens_per_event",
        lambda value: isinstance(value, int) and not isinstance(value, bool) and value >= 0,
        "non-negative integers",
    )

    if "min_events" in policy and "max_events" in policy and policy["min_events"] > policy["max_events"]:
        raise ValueError("min_events cannot be greater than max_events")

    if "allowed_events" in policy:
        allowed = set(policy["allowed_events"])
        required = set(policy.get("required_events", []))
        forbidden = set(policy.get("forbidden_events", []))
        impossible_required = sorted(required - allowed)
        if impossible_required:
            raise ValueError(f"required_events contains names excluded by allowed_events: {impossible_required}")
        contradictory = sorted(allowed & forbidden)
        if contradictory:
            raise ValueError(f"forbidden_events conflicts with allowed_events: {contradictory}")

    return policy


def _recorded_token_count(event: dict[str, Any], index: int) -> int | None:
    """Return token usage, preferring a provider aggregate over its subtotals."""
    usage = event.get("token_usage")
    if usage is None or usage == {}:
        return None
    if not isinstance(usage, dict):
        raise ValueError(f"event {index} token_usage must be an object")
    for counter_name, value in usage.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"event {index} has invalid token counter {counter_name!r}")
    # Many APIs report total_tokens alongside input/output subtotals.
    # Prefer the aggregate so the same tokens are not counted twice.
    if "total_tokens" in usage:
        return usage["total_tokens"]
    return sum(usage.values())


def evaluate_policy(events: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate recorded events against deterministic, declarative policy rules."""
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"event {index} must be an object")
        if not isinstance(event.get("name"), str) or not event["name"].strip():
            raise ValueError(f"event {index} name must be a non-empty string")

    names = [event["name"] for event in events]
    name_counts = Counter(names)
    results: list[dict[str, Any]] = []

    def add(name: str, passed: bool, message: str) -> None:
        results.append({"name": name, "passed": bool(passed), "message": message})

    if "allowed_events" in policy:
        allowed = set(policy["allowed_events"])
        unexpected = Counter(name for name in names if name not in allowed)
        message = (
            "unexpected event names: " + ", ".join(
                f"{name} ({count} occurrence(s))" for name, count in sorted(unexpected.items())
            )
            if unexpected
            else "all recorded event names are allowed"
        )
        add("allowed_events", not unexpected, message)

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
        total = 0.0
        missing = []
        for index, event in enumerate(events):
            value = event.get("duration_ms")
            if value is None:
                missing.append(index)
                continue
            if not _is_non_negative_number(value):
                raise ValueError(f"event {index} has an invalid duration_ms value")
            total += value
        add(
            "duration_coverage",
            not missing,
            "duration recorded for every event" if not missing
            else f"duration_ms missing from event index/indices: {', '.join(map(str, missing))}",
        )
        limit = policy["max_total_duration_ms"]
        add(
            "max_total_duration_ms",
            not missing and total <= limit,
            f"recorded duration {total:g} ms; limit {limit:g} ms"
            + (" (budget fails closed because duration data is missing)" if missing else ""),
        )

    if "max_total_tokens" in policy:
        total_tokens = 0
        tracked_events = 0
        for index, event in enumerate(events):
            token_count = _recorded_token_count(event, index)
            if token_count is not None:
                tracked_events += 1
                total_tokens += token_count
        limit = policy["max_total_tokens"]
        add(
            "max_total_tokens",
            tracked_events > 0 and total_tokens <= limit,
            f"recorded token count {total_tokens}; limit {limit}"
            + (" (no token usage was recorded)" if tracked_events == 0 else ""),
        )

    for event_name, limit in policy.get("max_calls_per_event", {}).items():
        count = name_counts[event_name]
        add(f"max_calls:{event_name}", count <= limit, f"event {event_name!r} occurred {count} time(s); limit {limit}")

    for event_name, limit in policy.get("max_duration_ms_per_event", {}).items():
        matches = [(index, event) for index, event in enumerate(events) if event["name"] == event_name]
        for occurrence, (index, event) in enumerate(matches, start=1):
            value = event.get("duration_ms")
            check_name = f"max_duration:{event_name}#{occurrence}"
            if value is None:
                add(check_name, False, f"event index {index} has no duration_ms; cannot verify the {limit:g} ms limit")
                continue
            if not _is_non_negative_number(value):
                raise ValueError(f"event {index} has an invalid duration_ms value")
            add(check_name, value <= limit, f"event index {index} duration {value:g} ms; limit {limit:g} ms")

    for event_name, limit in policy.get("max_tokens_per_event", {}).items():
        matches = [(index, event) for index, event in enumerate(events) if event["name"] == event_name]
        for occurrence, (index, event) in enumerate(matches, start=1):
            token_count = _recorded_token_count(event, index)
            check_name = f"max_tokens:{event_name}#{occurrence}"
            if token_count is None:
                add(check_name, False, f"event index {index} has no token_usage counters; cannot verify the {limit}-token limit")
                continue
            add(check_name, token_count <= limit, f"event index {index} recorded {token_count} tokens; limit {limit}")

    if not results:
        add("policy_has_rules", False, "policy contains no checks")
    return results
