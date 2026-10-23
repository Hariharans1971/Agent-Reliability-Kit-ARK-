from __future__ import annotations

from typing import Any

DEFAULT_SENSITIVE_KEYS = {
    "api_key", "authorization", "access_token", "refresh_token",
    "password", "secret", "email", "phone", "ssn",
}


def redact(value: Any, sensitive_keys: set[str] | None = None) -> Any:
    """Return a recursively redacted copy of JSON-like data.

    Best-effort only: secrets embedded in arbitrary strings are not detected.
    """
    keys = {key.lower() for key in (sensitive_keys or DEFAULT_SENSITIVE_KEYS)}
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if str(key).lower() in keys else redact(item, keys)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item, keys) for item in value]
    if isinstance(value, tuple):
        return [redact(item, keys) for item in value]
    return value
