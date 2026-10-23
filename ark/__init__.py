"""Agent Reliability Kit: local-first tracing and regression checks."""
from .diff import diff_traces
from .evaluate import evaluate_trace
from .io import load_trace
from .policy import evaluate_policy, load_policy
from .recorder import TraceRecorder
from .redact import redact

__version__ = "0.1.0"
__all__ = [
    "TraceRecorder",
    "diff_traces",
    "evaluate_policy",
    "evaluate_trace",
    "load_policy",
    "load_trace",
    "redact",
]
