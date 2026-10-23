from __future__ import annotations

from copy import deepcopy
from typing import Any

COMPARE_FIELDS = ("kind", "name", "inputs", "outputs", "token_usage")
_IGNORED_LIST_ITEM = "[ARK:IGNORED]"


def _parse_ignore_paths(ignore_paths: list[str] | None) -> list[list[str]]:
    parsed = []
    for path in ignore_paths or []:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("ignore paths must be non-empty dotted paths")
        parts = path.split(".")
        if any(not part for part in parts):
            raise ValueError(f"invalid ignore path {path!r}: empty path segment")
        parsed.append(parts)
    return parsed


def _remove_path(value: Any, parts: list[str]) -> None:
    """Remove a dict key or replace an indexed list item without shifting indexes."""
    if not parts:
        return
    head, tail = parts[0], parts[1:]
    if isinstance(value, dict):
        if head not in value:
            return
        if not tail:
            value.pop(head, None)
        else:
            _remove_path(value[head], tail)
    elif isinstance(value, list):
        if not head.isdigit():
            return
        index = int(head)
        if index >= len(value):
            return
        if not tail:
            value[index] = _IGNORED_LIST_ITEM
        else:
            _remove_path(value[index], tail)


def _comparison_view(event: dict, ignore_paths: list[list[str]]) -> dict[str, Any]:
    # Copy nested values so ignored paths never mutate caller-owned events.
    view = {key: deepcopy(event.get(key)) for key in COMPARE_FIELDS}
    for path in ignore_paths:
        _remove_path(view, path)
    return view


def _changed_paths(expected: Any, actual: Any, path: str = "") -> list[dict[str, Any]]:
    """Return deterministic leaf-level changes between two JSON-compatible values."""
    changes: list[dict[str, Any]] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(expected) | set(actual), key=str)
        for key in keys:
            child_path = f"{path}.{key}" if path else str(key)
            if key not in actual:
                changes.append({"path": child_path, "status": "removed", "expected": expected[key], "actual": None})
            elif key not in expected:
                changes.append({"path": child_path, "status": "added", "expected": None, "actual": actual[key]})
            else:
                changes.extend(_changed_paths(expected[key], actual[key], child_path))
        return changes

    if isinstance(expected, list) and isinstance(actual, list):
        for index in range(max(len(expected), len(actual))):
            child_path = f"{path}[{index}]" if path else f"[{index}]"
            if index >= len(actual):
                changes.append({"path": child_path, "status": "removed", "expected": expected[index], "actual": None})
            elif index >= len(expected):
                changes.append({"path": child_path, "status": "added", "expected": None, "actual": actual[index]})
            else:
                changes.extend(_changed_paths(expected[index], actual[index], child_path))
        return changes

    if expected != actual:
        changes.append({"path": path or "$", "status": "changed", "expected": expected, "actual": actual})
    return changes


def diff_traces(
    expected: list[dict],
    actual: list[dict],
    ignore_paths: list[str] | None = None,
    include_paths: bool = False,
) -> list[dict]:
    """Compare trace behavior and optionally include nested, path-focused changes.

    Ignore paths are relative to the compared event fields (kind/name/inputs/outputs/token_usage).
    Dict fields are removed; indexed list items are replaced with a stable sentinel to preserve
    positions. Missing paths have no effect. Input events are never mutated.

    Set include_paths=True to add changed_paths entries describing added, removed, or changed
    nested values on non-identical events. The default response shape is unchanged.
    """
    parsed_ignore_paths = _parse_ignore_paths(ignore_paths)
    result: list[dict] = []
    for index in range(max(len(expected), len(actual))):
        left = expected[index] if index < len(expected) else None
        right = actual[index] if index < len(actual) else None
        left_view = _comparison_view(left, parsed_ignore_paths) if left is not None else None
        right_view = _comparison_view(right, parsed_ignore_paths) if right is not None else None
        if left is None:
            status = "added"
        elif right is None:
            status = "removed"
        elif left_view == right_view:
            status = "same"
        else:
            status = "changed"

        item = {"index": index, "status": status, "expected": left_view, "actual": right_view}
        if include_paths and status != "same":
            if status == "changed":
                item["changed_paths"] = _changed_paths(left_view, right_view)
            else:
                item["changed_paths"] = [{
                    "path": "$",
                    "status": status,
                    "expected": left_view,
                    "actual": right_view,
                }]
        result.append(item)
    return result
