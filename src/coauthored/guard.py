"""Refuse to run when a pay-per-token API key is present (MISSION §1.9).

The study needs no paid model API. A key in the environment is treated as a configuration
error, not an opportunity.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

PAID_KEYS = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY")


class PaidKeyError(RuntimeError):
    pass


def present_paid_keys(env: Mapping[str, str] | None = None) -> list[str]:
    env = os.environ if env is None else env
    return [k for k in PAID_KEYS if env.get(k)]


def check(env: Mapping[str, str] | None = None) -> None:
    found = present_paid_keys(env)
    if found:
        raise PaidKeyError(
            f"refusing to run: {', '.join(found)} set. coauthored uses no paid API; unset the key(s)."
        )
