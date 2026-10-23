"""Synthetic customer-support workflow demo; no model or API key is needed."""
from pathlib import Path
from ark import TraceRecorder


def main() -> None:
    trace = TraceRecorder("customer-support-demo", tags={"domain": "support", "model": "mock"})
    trace.record(
        "tool", "order_lookup", {"order_id": "ORD-1042"},
        {"status": "delivered", "days_since_delivery": 3, "amount": 49.99},
        duration_ms=18, metadata={"source": "synthetic-demo-data"},
    )
    trace.record(
        "decision", "refund_eligibility",
        {"days_since_delivery": 3, "policy_window_days": 14},
        {"eligible": True, "reason": "within_policy_window"}, duration_ms=1,
    )
    trace.record(
        "tool", "refund_quote", {"order_id": "ORD-1042"},
        {"currency": "USD", "amount": 49.99}, duration_ms=7,
    )
    trace.record(
        "response", "customer_reply", {"intent": "refund_status"},
        {"message": "The order is eligible; a support agent will confirm the next step."},
        duration_ms=2,
    )
    output = trace.save(Path("artifacts") / "customer-support.jsonl")
    print(f"Saved {len(trace.events)} events to {output}")


if __name__ == "__main__":
    main()
