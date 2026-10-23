from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from .diff import diff_traces
from .evaluate import evaluate_trace
from .io import load_trace
from .policy import evaluate_policy, load_policy


def _print_results(results: list[dict], as_json: bool = False) -> bool:
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for item in results:
            print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['message']}")
    return all(item["passed"] for item in results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ark",
        description="Inspect and regression-test AI-agent JSONL traces.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect", help="summarize a trace")
    inspect_parser.add_argument("trace")

    diff_parser = sub.add_parser("diff", help="compare two traces")
    diff_parser.add_argument("expected")
    diff_parser.add_argument("actual")

    eval_parser = sub.add_parser("evaluate", help="run basic deterministic checks")
    eval_parser.add_argument("trace")
    eval_parser.add_argument("--min-steps", type=int, default=1)
    eval_parser.add_argument("--require", action="append", default=[])
    eval_parser.add_argument("--json", action="store_true", help="output JSON results")

    policy_parser = sub.add_parser("policy", help="enforce a JSON policy contract against a trace")
    policy_parser.add_argument("trace")
    policy_parser.add_argument("--policy", dest="policy_file", required=True)
    policy_parser.add_argument("--json", action="store_true", help="output JSON results")

    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            events = load_trace(args.trace)
            kinds = Counter(event.get("kind", "unknown") for event in events)
            duration = sum(event.get("duration_ms") or 0 for event in events)
            tokens = sum(sum((event.get("token_usage") or {}).values()) for event in events)
            print(f"Trace: {args.trace}\nEvents: {len(events)}\nKinds: {dict(kinds)}")
            print(f"Recorded duration: {duration:.2f} ms\nRecorded tokens: {tokens}")
            return 0

        if args.command == "diff":
            differences = [
                item for item in diff_traces(load_trace(args.expected), load_trace(args.actual))
                if item["status"] != "same"
            ]
            print(f"Differences: {len(differences)}")
            for item in differences:
                print(f"\n[{item['status'].upper()}] event index {item['index']}")
                print("expected:", json.dumps(item["expected"], sort_keys=True))
                print("actual:  ", json.dumps(item["actual"], sort_keys=True))
            return 1 if differences else 0

        if args.command == "evaluate":
            if args.min_steps < 0:
                print("--min-steps must be >= 0", file=sys.stderr)
                return 2
            results = evaluate_trace(load_trace(args.trace), args.min_steps, args.require)
            return 0 if _print_results(results, args.json) else 1

        results = evaluate_policy(load_trace(args.trace), load_policy(args.policy_file))
        return 0 if _print_results(results, args.json) else 1
    except (OSError, ValueError) as exc:
        print(f"ark: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
