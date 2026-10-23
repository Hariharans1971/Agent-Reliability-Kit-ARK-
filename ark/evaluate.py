from __future__ import annotations


def evaluate_trace(
    events: list[dict],
    min_steps: int = 1,
    required_names: list[str] | None = None,
) -> list[dict]:
    """Run small deterministic checks; these checks do not guarantee correctness."""
    results = [{
        "name": "minimum_steps",
        "passed": len(events) >= min_steps,
        "message": f"expected at least {min_steps} events; found {len(events)}",
    }]
    names = [event.get("name") for event in events]
    for required in required_names or []:
        results.append({
            "name": f"required_event:{required}",
            "passed": required in names,
            "message": f"{'found' if required in names else 'missing'} event named {required!r}",
        })
    return results
