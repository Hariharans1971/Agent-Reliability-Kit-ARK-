import contextlib
import io
import json
import tempfile
import unittest
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
