import tempfile
import unittest
from pathlib import Path

from ark import TraceRecorder, diff_traces, evaluate_trace, load_trace, redact


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

    def test_diff_reports_nested_changed_added_removed_and_list_paths(self):
        expected = [{
            "kind": "llm",
            "name": "answer",
            "inputs": {},
            "outputs": {
                "answer": {"text": "old", "source": "docs"},
                "messages": [{"id": "a"}, {"id": "b"}],
            },
        }]
        actual = [{
            "kind": "llm",
            "name": "answer",
            "inputs": {},
            "outputs": {
                "answer": {"text": "new", "confidence": 0.9},
                "messages": [{"id": "a"}, {"id": "c"}, {"id": "d"}],
            },
        }]
        result = diff_traces(expected, actual, include_paths=True)[0]
        self.assertEqual(result["status"], "changed")
        changes = {item["path"]: item["status"] for item in result["changed_paths"]}
        self.assertEqual(changes["outputs.answer.text"], "changed")
        self.assertEqual(changes["outputs.answer.source"], "removed")
        self.assertEqual(changes["outputs.answer.confidence"], "added")
        self.assertEqual(changes["outputs.messages[1].id"], "changed")
        self.assertEqual(changes["outputs.messages[2]"], "added")

    def test_diff_changed_paths_respect_ignore_paths(self):
        expected = [{
            "kind": "tool", "name": "lookup",
            "inputs": {"request_id": "a"},
            "outputs": {"answer": "old"},
        }]
        actual = [{
            "kind": "tool", "name": "lookup",
            "inputs": {"request_id": "b"},
            "outputs": {"answer": "new"},
        }]
        result = diff_traces(
            expected, actual,
            ignore_paths=["inputs.request_id"],
            include_paths=True,
        )[0]
        paths = [item["path"] for item in result["changed_paths"]]
        self.assertEqual(paths, ["outputs.answer"])

    def test_diff_does_not_add_changed_paths_by_default(self):
        result = diff_traces(
            [{"kind": "tool", "name": "x", "outputs": {"ok": True}}],
            [{"kind": "tool", "name": "x", "outputs": {"ok": False}}],
        )[0]
        self.assertNotIn("changed_paths", result)

    def test_diff_rejects_empty_ignore_path(self):
        with self.assertRaisesRegex(ValueError, "non-empty dotted paths"):
            diff_traces([], [], ignore_paths=[""])

    def test_trace_loader_rejects_invalid_optional_field_types(self):
        valid = {
            "event_id": "evt-1",
            "run_id": "run-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "kind": "tool",
            "name": "lookup",
            "inputs": {},
            "outputs": {},
            "duration_ms": 2,
            "token_usage": {"total_tokens": 3},
            "metadata": {},
        }
        invalid_updates = [
            ({"name": ""}, "name must be a non-empty string"),
            ({"inputs": []}, "inputs must be a JSON object"),
            ({"metadata": []}, "metadata must be a JSON object"),
            ({"duration_ms": -1}, "duration_ms must be a finite non-negative number"),
            ({"duration_ms": True}, "duration_ms must be a finite non-negative number"),
            ({"token_usage": "many"}, "token_usage must be a JSON object"),
            ({"token_usage": {"total_tokens": -1}}, "token_usage counters"),
            ({"token_usage": {"total_tokens": 1.5}}, "token_usage counters"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "invalid-events.jsonl"
            for changes, expected_message in invalid_updates:
                event = {**valid, **changes}
                target.write_text(__import__("json").dumps(event) + "\n", encoding="utf-8")
                with self.subTest(changes=changes), self.assertRaisesRegex(
                    ValueError, expected_message
                ):
                    load_trace(target)

    def test_trace_loader_validates_second_line_with_line_number(self):
        valid = {
            "event_id": "evt-1",
            "run_id": "run-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "kind": "tool",
            "name": "lookup",
        }
        invalid = {**valid, "duration_ms": float("inf")}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "trace.jsonl"
            target.write_text(
                __import__("json").dumps(valid) + "\n" + __import__("json").dumps(invalid) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, ":2:"):
                load_trace(target)

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
