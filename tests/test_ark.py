import tempfile
import unittest
from pathlib import Path

from ark import TraceRecorder, load_trace, diff_traces, evaluate_trace, redact


class ARKTests(unittest.TestCase):
    def test_record_save_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = TraceRecorder("unit-test", tags={"env": "test"})
            trace.record("tool", "lookup", {"id": 7}, {"ok": True}, duration_ms=4)
            target = trace.save(Path(tmp) / "nested" / "trace.jsonl")
            loaded = load_trace(target)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["name"], "lookup")
            self.assertEqual(loaded[0]["outputs"], {"ok": True})

    def test_empty_names_and_negative_duration_rejected(self):
        trace = TraceRecorder("unit-test")
        with self.assertRaises(ValueError):
            trace.record("", "lookup")
        with self.assertRaises(ValueError):
            trace.record("tool", "lookup", duration_ms=-1)

    def test_diff_ignores_ids_and_timestamps(self):
        a = [{"event_id": "1", "run_id": "a", "timestamp": "t1", "kind": "tool", "name": "lookup", "inputs": {"id": 1}, "outputs": {"ok": True}, "token_usage": {}}]
        b = [{"event_id": "2", "run_id": "b", "timestamp": "t2", "kind": "tool", "name": "lookup", "inputs": {"id": 1}, "outputs": {"ok": True}, "token_usage": {}}]
        self.assertEqual(diff_traces(a, b)[0]["status"], "same")

    def test_diff_detects_output_change_and_extra_event(self):
        a = [{"kind": "tool", "name": "lookup", "inputs": {}, "outputs": {"ok": True}}]
        b = [{"kind": "tool", "name": "lookup", "inputs": {}, "outputs": {"ok": False}}, {"kind": "response", "name": "reply"}]
        self.assertEqual([item["status"] for item in diff_traces(a, b)], ["changed", "added"])

    def test_diff_ignores_nested_request_id_without_mutating_input(self):
        expected = [{
            "kind": "tool", "name": "lookup",
            "inputs": {"request_id": "req-a", "customer": {"id": 7}},
            "outputs": {"ok": True},
        }]
        actual = [{
            "kind": "tool", "name": "lookup",
            "inputs": {"request_id": "req-b", "customer": {"id": 7}},
            "outputs": {"ok": True},
        }]
        result = diff_traces(expected, actual, ignore_paths=["inputs.request_id"])
        self.assertEqual(result[0]["status"], "same")
        self.assertEqual(expected[0]["inputs"]["request_id"], "req-a")
        self.assertEqual(actual[0]["inputs"]["request_id"], "req-b")

    def test_diff_ignores_list_index_path(self):
        expected = [{
            "kind": "llm", "name": "completion", "inputs": {},
            "outputs": {"messages": [{"trace_id": "a", "text": "hello"}]},
        }]
        actual = [{
            "kind": "llm", "name": "completion", "inputs": {},
            "outputs": {"messages": [{"trace_id": "b", "text": "hello"}]},
        }]
        result = diff_traces(expected, actual, ignore_paths=["outputs.messages.0.trace_id"])
        self.assertEqual(result[0]["status"], "same")

    def test_diff_rejects_empty_ignore_path(self):
        with self.assertRaisesRegex(ValueError, "non-empty dotted paths"):
            diff_traces([], [], ignore_paths=[""])

    def test_evaluation_required_event(self):
        results = evaluate_trace([{"name": "lookup"}], min_steps=1, required_names=["lookup", "refund"])
        self.assertTrue(results[0]["passed"])
        self.assertTrue(results[1]["passed"])
        self.assertFalse(results[2]["passed"])

    def test_nested_redaction(self):
        value = {"api_key": "secret", "user": {"email": "x@example.com", "name": "Ada"}}
        self.assertEqual(redact(value), {"api_key": "[REDACTED]", "user": {"email": "[REDACTED]", "name": "Ada"}})

    def test_invalid_jsonl_has_line_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "bad.jsonl"
            target.write_text('not-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, ":1:"):
                load_trace(target)


if __name__ == "__main__":
    unittest.main()
