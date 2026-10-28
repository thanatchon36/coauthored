"""Total default-branch commit count per S1/S2 repository (one REST call each: per_page=1, last page number).

Metadata only (DECISIONS D2): used for the Phase 3 time and disk estimate. Writes cache/history_counts.json.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
out: dict[str, int | None] = {}
for key in ("s1", "s2", "s3"):
    for r in cfg.get(key) or []:
        repo = r if isinstance(r, str) else r["repo"]
        head = subprocess.run(
            ["gh", "api", "-i", f"repos/{repo}/commits?per_page=1"], capture_output=True, text=True
        ).stdout
        m = re.search(r'[?&]page=(\d+)>; rel="last"', head)
        out[repo] = int(m.group(1)) if m else None
        print(f"{repo:45s} {out[repo]}")
Path("cache/history_counts.json").write_text(json.dumps(out, indent=1))
