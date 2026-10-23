import json
import tempfile
import unittest
from pathlib import Path

from ark.policy import evaluate_policy, load_policy


def event(name, duration_ms=5, token_usage=None):
    return {
        "event_id": name,
        "run_id": "test-run",
        "timestamp": "2026-01-01T00:00:00+00:00",
        "kind": "tool",
        "name": name,
        "inputs": {},
        "outputs": {},
        "duration_ms": duration_ms,
        "token_usage": token_usage or {},
        "metadata": {},
    }


class PolicyTests(unittest.TestCase):
    def test_policy_passes_required_forbidden_and_budgets(self):
        events = [
            event("order_lookup", 10, {"input_tokens": 20, "output_tokens": 5}),
            event("refund_eligibility", 2, {"total_tokens": 10}),
            event("customer_reply", 3),
        ]
        policy = {
            "min_events": 3,
            "max_events": 5,
            "required_events": ["order_lookup", "customer_reply"],
            "forbidden_events": ["refund_execution"],
            "max_total_duration_ms": 20,
            "max_total_tokens": 40,
            "max_calls_per_event": {"order_lookup": 1},
        }
        results = evaluate_policy(events, policy)
        self.assertTrue(all(item["passed"] for item in results), results)

    def test_policy_fails_forbidden_event_and_budget_overrun(self):
        events = [event("refund_execution", 30, {"total_tokens": 50})]
        policy = {
            "forbidden_events": ["refund_execution"],
            "max_total_duration_ms": 10,
            "max_total_tokens": 20,
        }
        results = evaluate_policy(events, policy)
        self.assertEqual([item["name"] for item in results], [
            "forbidden_event:refund_execution", "max_total_duration_ms", "max_total_tokens"
        ])
        self.assertFalse(any(item["passed"] for item in results))

    def test_policy_caps_number_of_calls(self):
        results = evaluate_policy(
            [event("search"), event("search")],
            {"max_calls_per_event": {"search": 1}},
        )
        self.assertFalse(results[0]["passed"])

    def test_aggregate_total_tokens_is_not_double_counted(self):
        events = [event("llm_call", token_usage={
            "input_tokens": 40,
            "output_tokens": 10,
            "total_tokens": 50,
        })]
        results = evaluate_policy(events, {"max_total_tokens": 55})
        self.assertTrue(results[0]["passed"], results)
        self.assertIn("recorded token count 50", results[0]["message"])

    def test_component_tokens_are_summed_when_no_aggregate_exists(self):
        events = [event("llm_call", token_usage={
            "input_tokens": 40,
            "output_tokens": 10,
        })]
        results = evaluate_policy(events, {"max_total_tokens": 55})
        self.assertTrue(results[0]["passed"], results)
        self.assertIn("recorded token count 50", results[0]["message"])

    def test_policy_loader_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps({"surprise": True}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported policy keys"):
                load_policy(path)

    def test_policy_loader_checks_min_max_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps({"min_events": 4, "max_events": 2}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "min_events cannot"):
                load_policy(path)

    def test_policy_rejects_invalid_recorded_token_counts(self):
        events = [event("tool", token_usage={"total_tokens": -1})]
        with self.assertRaisesRegex(ValueError, "invalid token counter"):
            evaluate_policy(events, {"max_total_tokens": 10})


if __name__ == "__main__":
    unittest.main()
