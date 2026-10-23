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
            "forbidden_event:refund_execution",
            "duration_coverage",
            "max_total_duration_ms",
            "max_total_tokens",
        ])
        self.assertFalse(results[0]["passed"])  # forbidden event\n        self.assertTrue(results[1]["passed"])   # all events recorded duration\n        self.assertFalse(results[2]["passed"])  # total duration over budget\n        self.assertFalse(results[3]["passed"])  # total tokens over budget

    def test_policy_caps_number_of_calls(self):
        results = evaluate_policy(
            [event("search"), event("search")],
            {"max_calls_per_event": {"search": 1}},
        )
        self.assertFalse(results[0]["passed"])

    def test_allowed_events_rejects_unexpected_action(self):
        results = evaluate_policy(
            [event("order_lookup"), event("send_external_email")],
            {"allowed_events": ["order_lookup"]},
        )
        self.assertFalse(results[0]["passed"])
        self.assertIn("send_external_email", results[0]["message"])

    def test_per_event_duration_budget_passes_and_fails(self):
        events = [event("llm_call", duration_ms=12), event("lookup", duration_ms=3)]
        passed = evaluate_policy(events, {"max_duration_ms_per_event": {"llm_call": 12}})
        failed = evaluate_policy(events, {"max_duration_ms_per_event": {"llm_call": 10}})
        self.assertTrue(passed[0]["passed"])
        self.assertFalse(failed[0]["passed"])

    def test_per_event_duration_budget_fails_when_metric_missing(self):
        events = [event("llm_call", duration_ms=None)]
        results = evaluate_policy(events, {"max_duration_ms_per_event": {"llm_call": 100}})
        self.assertFalse(results[0]["passed"])
        self.assertIn("cannot verify", results[0]["message"])

    def test_total_duration_budget_fails_closed_on_missing_measurement(self):
        results = evaluate_policy(
            [event("first", duration_ms=3), event("second", duration_ms=None)],
            {"max_total_duration_ms": 100},
        )
        self.assertFalse(results[0]["passed"])
        self.assertFalse(results[1]["passed"])
        self.assertIn("missing", results[0]["message"])

    def test_per_event_token_budget_and_aggregate_precedence(self):
        events = [event("llm_call", token_usage={
            "input_tokens": 40, "output_tokens": 10, "total_tokens": 50,
        })]
        results = evaluate_policy(events, {
            "max_total_tokens": 50,
            "max_tokens_per_event": {"llm_call": 50},
        })
        self.assertTrue(all(item["passed"] for item in results), results)
        self.assertIn("recorded 50 tokens", results[1]["message"])

    def test_per_event_token_budget_fails_when_usage_missing(self):
        results = evaluate_policy(
            [event("llm_call", token_usage={})],
            {"max_tokens_per_event": {"llm_call": 50}},
        )
        self.assertFalse(results[0]["passed"])
        self.assertIn("cannot verify", results[0]["message"])

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

    def test_policy_loader_rejects_impossible_allowlist_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps({
                "allowed_events": ["lookup"],
                "required_events": ["refund"],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "excluded by allowed_events"):
                load_policy(path)

    def test_policy_rejects_invalid_recorded_token_counts(self):
        events = [event("tool", token_usage={"total_tokens": -1})]
        with self.assertRaisesRegex(ValueError, "invalid token counter"):
            evaluate_policy(events, {"max_total_tokens": 10})


if __name__ == "__main__":
    unittest.main()
