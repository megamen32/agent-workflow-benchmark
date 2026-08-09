"""Conservative secret redaction for published benchmark dialogs."""

from __future__ import annotations

import re
from typing import Any


PATTERNS = (
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1[REDACTED]"),
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{12,})\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)(api[_ -]?key\s*[:=]\s*)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(cookie\s*[:=]\s*)[^\n]+"), r"\1[REDACTED]"),
)


def redact_text(value: str) -> str:
    for pattern, replacement in PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        return {str(key): redact(item) for key, item in value.items()}
    return value
