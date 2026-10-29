"""Survival of attribution through the merge (PREREGISTRATION §5, DECISIONS D12).

1. List merged PRs of every S1 ∪ S2 repository (GraphQL, newest first) and keep those merged
   2025-06-01..2026-09-30. Cached per repository in cache/survival/prs/.
2. Shuffle each repository's list with the frozen seed; visit repositories round-robin, one PR per visit.
3. For each PR fetch its head commits (first 100) and its landed commit, classify with
   `coauthored.survival.classify`, and stop at 200 PRs with an attributed head commit or 4,000 inspected.
Writes data/survival.csv (repository, method, flags, tools; no messages or identities).
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from _graphql import graphql  # noqa: E402

from coauthored.signatures import catalogue  # noqa: E402
from coauthored.signatures.matcher import Identity  # noqa: E402
from coauthored.survival.classify import ApiCommit, classify  # noqa: E402

SEED = 20261028
WINDOW = ("2025-06-01", "2026-09-30T23:59:59Z")
CREATED_FLOOR = "2024-06-01"  # stop paging once PRs were created this long before the window
TARGET_ATTRIBUTED, MAX_INSPECTED, BATCH = 200, 4000, 10
CACHE = Path("cache/survival")

LIST_Q = """query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: MERGED, first: 100, after: $after, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes { number createdAt mergedAt }
    }
  }
}"""
COMMIT = "oid message parents { totalCount } author { name email } committer { name email }"


def list_merged(repo: str) -> list[int]:
    path = CACHE / "prs" / (repo.replace("/", "__") + ".json")
    if path.exists():
        return json.loads(path.read_text())
    owner, name = repo.split("/")
    out: list[int] = []
    after: str | None = None
    while True:
        args: dict[str, Any] = {"owner": owner, "name": name}
        if after:
            args["after"] = after
        page = graphql(LIST_Q, **args)["repository"]["pullRequests"]
        nodes = page["nodes"]
        out += [n["number"] for n in nodes if n["mergedAt"] and WINDOW[0] <= n["mergedAt"] <= WINDOW[1]]
        if not page["pageInfo"]["hasNextPage"] or (nodes and nodes[-1]["createdAt"] < CREATED_FLOOR):
            break
        after = page["pageInfo"]["endCursor"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(out)))
    return sorted(out)


def _commit(c: dict[str, Any]) -> ApiCommit:
    return ApiCommit(
        c["oid"],
        c["message"],
        Identity(c["author"]["name"] or "", c["author"]["email"] or ""),
        Identity(c["committer"]["name"] or "", c["committer"]["email"] or ""),
        c["parents"]["totalCount"],
    )


def fetch_details(batch: list[tuple[str, int]]) -> dict[tuple[str, int], dict[str, Any] | None]:
    parts = []
    for i, (repo, number) in enumerate(batch):
        owner, name = repo.split("/")
        parts.append(
            f'r{i}: repository(owner: "{owner}", name: "{name}") {{ pullRequest(number: {number}) {{ '
            f"mergeCommit {{ {COMMIT} }} "
            f"commits(first: 100) {{ totalCount nodes {{ commit {{ {COMMIT} }} }} }} }} }}"
        )
    data = graphql("query { " + "\n".join(parts) + " }")
    return {key: (data.get(f"r{i}") or {}).get("pullRequest") for i, key in enumerate(batch)}


def main() -> None:
    cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    cat = catalogue.load(Path("configs/signatures.yaml"))
    repos = [(k.upper(), r["repo"]) for k in ("s1", "s2") for r in cfg[k]]
    rng = random.Random(SEED)
    queues: dict[str, list[int]] = {}
    for _stratum, repo in repos:
        prs = list_merged(repo)
        rng.shuffle(prs)
        queues[repo] = prs
        print(f"{repo:45s} merged in window: {len(prs)}", file=sys.stderr)
    order: list[tuple[str, int]] = []
    depth = 0
    while any(depth < len(q) for q in queues.values()):
        order += [(repo, queues[repo][depth]) for _s, repo in repos if depth < len(queues[repo])]
        depth += 1
    stratum_of = {repo: s for s, repo in repos}

    done_path = CACHE / "results.jsonl"
    done = [json.loads(ln) for ln in done_path.read_text().splitlines()] if done_path.exists() else []
    seen = {(d["repo"], d["number"]) for d in done}
    n_attr = sum(d["head_attributed"] for d in done)
    i = len(done)
    with done_path.open("a") as fh:
        while i < min(len(order), MAX_INSPECTED) and n_attr < TARGET_ATTRIBUTED:
            batch = [k for k in order[i : i + BATCH] if k not in seen]
            details = fetch_details(batch) if batch else {}
            for key in order[i : i + BATCH]:
                if key in seen or n_attr >= TARGET_ATTRIBUTED:
                    continue
                pr = details.get(key)
                row: dict[str, Any] = {"repo": key[0], "number": key[1], "stratum": stratum_of[key[0]]}
                if not pr or not pr.get("mergeCommit"):
                    row |= {
                        "method": "unavailable",
                        "head_attributed": False,
                        "landed_attributed": False,
                        "survived": None,
                        "head_tools": "",
                        "n_head": 0,
                        "head_truncated": False,
                    }
                else:
                    head = [_commit(n["commit"]) for n in pr["commits"]["nodes"]]
                    s = classify(cat, head, _commit(pr["mergeCommit"]))
                    row |= {
                        "method": s.method,
                        "head_attributed": s.head_attributed,
                        "landed_attributed": s.landed_attributed,
                        "survived": s.survived,
                        "head_tools": ";".join(s.head_tools),
                        "n_head": pr["commits"]["totalCount"],
                        "head_truncated": pr["commits"]["totalCount"] > 100,
                    }
                n_attr += row["head_attributed"]
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                done.append(row)
                seen.add(key)
            i += BATCH
            print(f"inspected {len(done)}  attributed-head {n_attr}", file=sys.stderr)
    with open("data/survival.csv", "w", newline="") as out:
        # the published file carries no PR number (PREREGISTRATION §11); cache/ keeps the identified rows
        w = csv.DictWriter(out, fieldnames=[k for k in done[0] if k != "number"], extrasaction="ignore")
        w.writeheader()
        w.writerows(done)
    print(f"done: inspected {len(done)}, attributed head {n_attr}", file=sys.stderr)


if __name__ == "__main__":
    main()
