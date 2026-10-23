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
