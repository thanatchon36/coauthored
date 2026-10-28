"""Fetch AI-contribution policy files at the snapshot head SHA and classify them (PREREGISTRATION §6).

One GraphQL query per repository. Writes data/policy.csv (no file text) and docs/policy-review.md (the
deciding sentence for every non-silent repository, for the hand check). File texts are cached in
cache/policy/.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from _graphql import graphql  # noqa: E402

from coauthored.policy.classify import POLICY_FILES, classify  # noqa: E402

CACHE = Path("cache/policy")


def fetch(repo: str, sha: str) -> dict[str, str]:
    path = CACHE / (repo.replace("/", "__") + ".json")
    if path.exists():
        return json.loads(path.read_text())
    owner, name = repo.split("/")
    fields = "\n".join(
        f'f{i}: object(expression: "{sha}:{p}") {{ ... on Blob {{ text }} }}'
        for i, p in enumerate(POLICY_FILES)
    )
    q = f'query {{ repository(owner: "{owner}", name: "{name}") {{ {fields} }} }}'
    data = graphql(q)["repository"]
    files = {p: data[f"f{i}"]["text"] for i, p in enumerate(POLICY_FILES) if data.get(f"f{i}")}
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(files))
    return files


def main() -> None:
    cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    manifest: dict[str, dict] = {}
    for k in ("s1", "s2", "s3"):
        manifest |= json.loads(Path(f"data/manifest_{k}.json").read_text())["repos"]
    rows, review = [], []
    for stratum in ("s1", "s2", "s3"):
        for r in cfg[stratum]:
            repo = r["repo"]
            res = classify(fetch(repo, manifest[repo]["head_sha"]))
            rows.append(
                {
                    "repo": repo,
                    "stratum": stratum.upper(),
                    "policy": res.cls,
                    "source": res.source,
                    "agent_config": int(res.agent_config),
                }
            )
            if res.cls != "silent":
                review.append((stratum.upper(), repo, res))
            print(f"{repo:45s} {res.cls:20s} {res.source}", file=sys.stderr)
    with open("data/policy.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = [
        "# Policy review",
        "",
        "Rule-based first pass (`src/coauthored/policy/classify.py`) at the snapshot head SHA, with the",
        "sentence that decided each non-silent class. Hand check: `check` is `ok` when the class is right,",
        "otherwise the corrected class and why; corrections live in `configs/policy_overrides.yaml`.",
        "",
        "| stratum | repository | first pass | file | deciding sentence | check |",
        "|---|---|---|---|---|---|",
    ]
    for stratum, repo, res in review:
        quote = res.quote.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {stratum} | {repo} | {res.cls} | `{res.source}` | {quote} | |")
    Path("docs/policy-review.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
