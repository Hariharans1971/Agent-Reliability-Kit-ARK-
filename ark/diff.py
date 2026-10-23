from __future__ import annotations

COMPARE_FIELDS = ("kind", "name", "inputs", "outputs", "token_usage")


def diff_traces(expected: list[dict], actual: list[dict]) -> list[dict]:
    """Compare behavior fields, deliberately ignoring timestamps and generated IDs."""
    result: list[dict] = []
    for index in range(max(len(expected), len(actual))):
        left = expected[index] if index < len(expected) else None
        right = actual[index] if index < len(actual) else None
        left_view = {key: left.get(key) for key in COMPARE_FIELDS} if left is not None else None
        right_view = {key: right.get(key) for key in COMPARE_FIELDS} if right is not None else None
        if left is None:
            status = "added"
        elif right is None:
            status = "removed"
        elif left_view == right_view:
            status = "same"
        else:
            status = "changed"
        result.append({"index": index, "status": status, "expected": left_view, "actual": right_view})
    return result
