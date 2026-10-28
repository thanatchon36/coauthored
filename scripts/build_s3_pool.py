"""Build the S3 candidate pool and run the seeded match (MISSION §3.5, DECISIONS D6).

1. GitHub repository search per language and star band (pushed since 2026-09-01, not archived, not a fork).
2. Static eligibility (non-AI topics/description, software project, language group) before any count.
3. Commit counts (REST commits API) only for statically eligible repos whose stars are within the caliper of
   some S1 repo in the same language group.
4. `coauthored.match.match` with the frozen seed; append S3 to configs/repos.yaml; write data/s3_match.json.
Caches in cache/s3_*.json; resumable.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from resolve_candidates import WINDOWS, commit_count  # noqa: E402

from coauthored.match import group, is_eligible_control, match  # noqa: E402

SEED = 20261028
LANGS = ["Python", "C++", "C", "Go", "Rust", "TypeScript", "JavaScript"]
BANDS = ["2000..5000", "5001..15000", "15001..50000", ">50000"]
PAGES = 3


def search_repos(q: str, page: int) -> list[dict] | None:
    for wait in (60, 120, 240, 480):
        out = subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "GET",
                "search/repositories",
                "-f",
                f"q={q}",
                "-f",
                "sort=stars",
                "-f",
                "per_page=100",
                "-f",
                f"page={page}",
            ],
            capture_output=True,
            text=True,
        )
        if out.returncode == 0:
            return json.loads(out.stdout).get("items", [])
        print(f"! {q} p{page}: {out.stderr.strip()[:80]} (sleep {wait}s)", file=sys.stderr)
        time.sleep(wait)
    return None


def main() -> None:
    repos_cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    rule = repos_cfg["rule"]
    s1 = repos_cfg["s1"]
    exclude = {r["repo"] for k in ("s1", "s2") for r in repos_cfg[k]}
    exclude |= {r["repo"] for r in repos_cfg["excluded"]}
    exclude |= set(yaml.safe_load(Path("configs/pilot.yaml").read_text())["pilots"])
    screen = Path("configs/s3_screen.yaml")
    if screen.exists():
        exclude |= {r["repo"] for r in yaml.safe_load(screen.read_text())["screened_out"]}

    raw_path = Path("cache/s3_search.json")
    raw: dict[str, dict] = json.loads(raw_path.read_text()) if raw_path.exists() else {}
    done_path = Path("cache/s3_queries_done.json")
    done: list[str] = json.loads(done_path.read_text()) if done_path.exists() else []
    for lang in LANGS:
        for band in BANDS:
            for page in range(1, PAGES + 1):
                key = f"{lang}|{band}|{page}"
                if key in done:
                    continue
                q = f"language:{json.dumps(lang)} stars:{band} pushed:>=2026-09-01 archived:false fork:false"
                items = search_repos(q, page)
                if items is None:
                    continue
                for it in items:
                    raw[it["full_name"]] = {
                        "full_name": it["full_name"],
                        "stars": it["stargazers_count"],
                        "language": it["language"],
                        "topics": it.get("topics", []),
                        "description": it.get("description") or "",
                        "archived": it["archived"],
                        "fork": it["fork"],
                        "default_branch": it["default_branch"],
                        "created_at": it["created_at"],
                    }
                done.append(key)
                raw_path.write_text(json.dumps(raw))
                done_path.write_text(json.dumps(done))
                print(f"{key}: {len(items)} (pool {len(raw)})", file=sys.stderr)
                time.sleep(7)
                if len(items) < 100:
                    break

    def near_some_s1(r: dict) -> bool:
        return any(
            group(t["language"]) == group(r["language"])
            and 0.5 * t["stars"] <= r["stars"] <= 1.5 * t["stars"]
            for t in s1
        )

    static = []
    for r in raw.values():
        if r["full_name"] in exclude:
            continue
        ok, _ = is_eligible_control(
            {**r, "commits_12m": 10**9, "commits_2024": 10**9}, rule["min_stars"], 0, 0
        )
        if ok and near_some_s1(r):
            static.append(r)
    print(f"statically eligible and near some S1 repo: {len(static)}", file=sys.stderr)

    counts_path = Path("cache/s3_counts.json")
    counts: dict[str, dict] = json.loads(counts_path.read_text()) if counts_path.exists() else {}
    for r in static:
        if r["full_name"] in counts:
            continue
        counts[r["full_name"]] = {
            k: commit_count(r["full_name"], r["default_branch"], *w) for k, w in WINDOWS.items()
        }
        counts_path.write_text(json.dumps(counts))
    pool = []
    for r in static:
        rec = {**r, **counts[r["full_name"]]}
        ok, _ = is_eligible_control(
            rec, rule["min_stars"], rule["min_commits_12m"], rule["min_commits_2024_s1_s3"]
        )
        if ok:
            pool.append(rec)
    print(f"eligible pool: {len(pool)}", file=sys.stderr)

    matched = match(s1, pool, seed=SEED)
    Path("data").mkdir(exist_ok=True)
    Path("data/s3_match.json").write_text(
        json.dumps({"seed": SEED, "caliper": 0.5, "pool_size": len(pool), "matches": matched}, indent=1)
    )
    by_name = {p["full_name"]: p for p in pool}
    repos_cfg["s3"] = [
        {
            "repo": m["control"],
            "matched_to": m["treated"],
            "language": by_name[m["control"]]["language"],
            "stars": by_name[m["control"]]["stars"],
            "commits_2024": by_name[m["control"]]["commits_2024"],
            "commits_12m": by_name[m["control"]]["commits_12m"],
            "caliper_violated": m["caliper_violated"],
            "rationale": by_name[m["control"]]["description"][:160],
        }
        for m in matched
        if m["control"]
    ]
    Path("configs/repos.yaml").write_text(
        yaml.safe_dump(repos_cfg, sort_keys=False, allow_unicode=True, width=120)
    )
    viol = sum(m["caliper_violated"] for m in matched)
    print(f"matched {len(repos_cfg['s3'])}/{len(s1)}; caliper violated {viol}", file=sys.stderr)


if __name__ == "__main__":
    main()
