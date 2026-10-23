"""Agent Reliability Kit: local-first tracing and regression checks."""
from .recorder import TraceRecorder
from .io import load_trace
from .diff import diff_traces
from .evaluate import evaluate_trace
from .redact import redact
from .policy import evaluate_policy, load_policy

__version__ = "0.1.0"
__all__ = [
    "TraceRecorder",
    "load_trace",
    "diff_traces",
    "evaluate_trace",
    "redact",
    "load_policy",
    "evaluate_policy",
]
