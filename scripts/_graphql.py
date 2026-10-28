"""Minimal GitHub GraphQL client over `gh api graphql`, with backoff on rate limits."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from typing import Any


def graphql(query: str, **variables: Any) -> dict[str, Any]:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    for wait in (30, 60, 120, 240, 480, 600):
        out = subprocess.run(args, capture_output=True, text=True)
        if out.returncode == 0:
            body = json.loads(out.stdout)
            if body.get("data") is not None:
                return body["data"]  # partial errors (e.g. one missing file) are fine
        print(f"! graphql: {(out.stderr or out.stdout).strip()[:100]} (sleep {wait}s)", file=sys.stderr)
        time.sleep(wait)
    raise RuntimeError("GraphQL kept failing")
