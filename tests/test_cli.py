import contextlib
import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from ark import TraceRecorder
from ark.cli import main


class PolicyCliTests(unittest.TestCase):
    def _make_trace(self, folder: str, event_name: str) -> Path:
        trace = TraceRecorder("cli-test")
        trace.record("tool", event_name, inputs={}, outputs={"ok": True}, duration_ms=2)
        path = Path(folder) / "trace.jsonl"
        trace.save(path)
        return path

    def _make_policy(self, folder: str, policy: dict) -> Path:
        path = Path(folder) / "policy.json"
        path.write_text(json.dumps(policy), encoding="utf-8")
        return path

    def test_diff_cli_ignores_requested_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = TraceRecorder("left")
            left.record("tool", "lookup", inputs={"request_id": "req-a"}, outputs={"ok": True})
            right = TraceRecorder("right")
            right.record("tool", "lookup", inputs={"request_id": "req-b"}, outputs={"ok": True})
            expected = left.save(Path(tmp) / "expected.jsonl")
            actual = right.save(Path(tmp) / "actual.jsonl")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([
                    "diff", str(expected), str(actual),
                    "--ignore-path", "inputs.request_id",
                ])
            self.assertEqual(code, 0)
            self.assertIn("Differences: 0", output.getvalue())

    def test_diff_cli_reports_invalid_ignore_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "lookup")
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                code = main(["diff", str(trace), str(trace), "--ignore-path", "inputs..id"])
            self.assertEqual(code, 2)
            self.assertIn("empty path segment", output.getvalue())

    def test_policy_command_writes_junit_failure_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "unexpected_action")
            policy = self._make_policy(tmp, {"allowed_events": ["lookup"]})
            report = Path(tmp) / "reports" / "policy.xml"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([
                    "policy", str(trace), "--policy", str(policy),
                    "--junit-xml", str(report),
                ])
            self.assertEqual(code, 1)
            self.assertTrue(report.is_file())
            root = ET.parse(report).getroot()
            self.assertEqual(root.tag, "testsuite")
            self.assertEqual(root.attrib["tests"], "1")
            self.assertEqual(root.attrib["failures"], "1")
            failure = root.find("./testcase/failure")
            self.assertIsNotNone(failure)
            self.assertIn("unexpected_action", failure.attrib["message"])
            self.assertIn("unexpected_action", failure.text or "")

    def test_evaluate_command_writes_junit_success_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "lookup")
            report = Path(tmp) / "evaluate.xml"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([
                    "evaluate", str(trace), "--min-steps", "1",
                    "--require", "lookup", "--junit-xml", str(report),
                ])
            self.assertEqual(code, 0)
            root = ET.parse(report).getroot()
            self.assertEqual(root.attrib["failures"], "0")
            self.assertEqual(root.attrib["tests"], "2")

    def test_inspect_does_not_double_count_aggregate_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = TraceRecorder("inspect-test")
            trace.record(
                "llm",
                "completion",
                inputs={},
                outputs={"ok": True},
                token_usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
            )
            path = trace.save(Path(tmp) / "trace.jsonl")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(["inspect", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("Recorded tokens: 15", output.getvalue())

    def test_policy_command_returns_zero_for_allowed_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "lookup")
            policy = self._make_policy(tmp, {"allowed_events": ["lookup"]})
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["policy", str(trace), "--policy", str(policy)])
            self.assertEqual(code, 0)

    def test_policy_command_returns_one_for_allowlist_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "unexpected_action")
            policy = self._make_policy(tmp, {"allowed_events": ["lookup"]})
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(["policy", str(trace), "--policy", str(policy)])
            self.assertEqual(code, 1)
            self.assertIn("unexpected_action", output.getvalue())

    def test_policy_command_returns_two_for_invalid_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = self._make_trace(tmp, "lookup")
            policy = self._make_policy(tmp, {"unknown_rule": True})
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["policy", str(trace), "--policy", str(policy)])
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
