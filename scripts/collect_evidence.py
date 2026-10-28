"""Collect >= 3 public evidence URLs per catalogue entry (MISSION §1.6) and write them back to the YAML.

Sources, in order: the pilot clones (work/*.git), then GitHub commit search with the entry's `query`. Every
candidate is re-checked with the real matcher (or bot rule) before its URL is accepted. Prefers distinct
repositories.
Usage: uv run python scripts/collect_evidence.py configs/signatures.yaml | --bots configs/bots.yaml
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

from coauthored import bots as bots_mod
from coauthored.scan.gitlog import iter_commits
from coauthored.signatures.catalogue import Catalogue, Signature
from coauthored.signatures.matcher import Identity, match_commit

PILOTS = {p.name.removesuffix(".git").replace("__", "/"): p for p in Path("work").glob("*__*.git")}
WANT = 3


def search(q: str) -> list[dict]:
    for wait in (60, 120, 240):
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/commits", "-f", f"q={q}", "-f", "per_page=50"],
            capture_output=True,
            text=True,
        )
        if out.returncode == 0:
            return json.loads(out.stdout).get("items", [])
        print(f"! {q}: {out.stderr.strip()[:70]} (sleep {wait})", file=sys.stderr)
        time.sleep(wait)
    return []


def hits_signature(sig: Signature, author: Identity, committer: Identity, message: str) -> bool:
    one = Catalogue(version="x", signatures=[sig])
    return sig.id in match_commit(one, author, committer, message).signature_ids


def pick(urls: list[tuple[str, str]]) -> list[str]:
    """Up to WANT URLs, one per repository first."""
    out, seen = [], set()
    for repo, url in urls:
        if repo not in seen:
            out.append(url)
            seen.add(repo)
    for _repo, url in urls:
        if len(out) >= WANT:
            break
        if url not in out:
            out.append(url)
    return out[:WANT]


def main(cat_path: Path) -> None:
    doc = yaml.safe_load(cat_path.read_text())
    sigs = [Signature.model_validate(s) for s in doc["signatures"]]
    found: dict[str, list[tuple[str, str]]] = {s.id: [] for s in sigs}
    for repo, path in PILOTS.items():
        for c in iter_commits(path):
            a, k = Identity(c.author_name, c.author_email), Identity(c.committer_name, c.committer_email)
            for s in sigs:
                if len(found[s.id]) < 10 and hits_signature(s, a, k, c.message):
                    found[s.id].append((repo, f"https://github.com/{repo}/commit/{c.sha}"))
    for s in sigs:
        if len({r for r, _ in found[s.id]}) >= WANT or not s.query:
            continue
        for it in search(s.query):
            c = it["commit"]
            a = Identity(c["author"]["name"], c["author"]["email"])
            k = Identity(c["committer"]["name"], c["committer"]["email"])
            if hits_signature(s, a, k, c["message"]):
                found[s.id].append((it["repository"]["full_name"], it["html_url"]))
        time.sleep(7)
    for raw in doc["signatures"]:
        raw["evidence"] = pick(found[raw["id"]])
        print(f"{raw['id']:34s} {len(raw['evidence'])}", file=sys.stderr)
    cat_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))


# Second pass for entries the first pass left short: identity entries searched by account (commit search's
# author-email/committer-email qualifiers), co-author entries by an alternative literal.
SUPPLEMENT = {
    "codex-connector-identity": [
        "author-email:199175422+chatgpt-codex-connector[bot]@users.noreply.github.com"
    ],
    "openhands-identity": ["author-email:openhands@all-hands.dev", "committer-email:openhands@all-hands.dev"],
    "jules-identity": ["author-email:161369871+google-labs-jules[bot]@users.noreply.github.com"],
    "amazon-q-identity": ["author-email:208079219+amazon-q-developer[bot]@users.noreply.github.com"],
    "factory-droid-identity": ["author-email:138933559+factory-droid[bot]@users.noreply.github.com"],
    "replit-agent-identity": ["author-email:agent@replit.com", "committer-email:agent@replit.com"],
    "lovable-identity": ["author-email:159125892+lovable-dev[bot]@users.noreply.github.com"],
    "coderabbit-identity": ["author-email:136622811+coderabbitai[bot]@users.noreply.github.com"],
    "aider-author-suffix": ["author-name:aider", "committer-name:aider"],
    "kiro-coauthor": ['"kiro-agent[bot]"', '"245459735+kiro-agent"'],
    "lovable-coauthor": ['"lovable-dev[bot]"', '"159125892+lovable-dev"'],
    "sweep-coauthor": ['"sweep-ai@users.noreply.github.com"', '"236279702+sweep-ai"'],
}


def main_supplement(cat_path: Path) -> None:
    doc = yaml.safe_load(cat_path.read_text())
    for raw in doc["signatures"]:
        if raw["id"] not in SUPPLEMENT or len(raw.get("evidence", [])) >= WANT:
            continue
        sig = Signature.model_validate(raw)
        urls = [(u.split("/")[3] + "/" + u.split("/")[4], u) for u in raw.get("evidence", [])]
        for q in SUPPLEMENT[raw["id"]]:
            for it in search(q):
                c = it["commit"]
                a = Identity(c["author"]["name"], c["author"]["email"])
                k = Identity(c["committer"]["name"], c["committer"]["email"])
                if hits_signature(sig, a, k, c["message"]) and it["html_url"] not in {u for _, u in urls}:
                    urls.append((it["repository"]["full_name"], it["html_url"]))
            time.sleep(10)
        raw["evidence"] = pick(urls)
        print(f"{raw['id']:34s} {len(raw['evidence'])}", file=sys.stderr)
        cat_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))


def main_bots(path: Path) -> None:
    doc = yaml.safe_load(path.read_text())
    for raw in doc["bots"]:
        b = bots_mod.Bot.model_validate(raw)
        urls: list[tuple[str, str]] = []
        if b.query:
            for it in search(b.query):
                c = it["commit"]["author"]
                if b.matches(c["name"], c["email"]):
                    urls.append((it["repository"]["full_name"], it["html_url"]))
            time.sleep(7)
        raw["evidence"] = pick(urls)
        print(f"{raw['id']:34s} {len(raw['evidence'])}", file=sys.stderr)
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))


if __name__ == "__main__":
    if sys.argv[1] == "--bots":
        main_bots(Path(sys.argv[2]))
    elif sys.argv[1] == "--supplement":
        main_supplement(Path(sys.argv[2]))
    else:
        main(Path(sys.argv[1]))
