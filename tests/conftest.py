"""A fixture git repository with known attributions (MISSION §6: no-network smoke test)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
HUMAN = ("Ada Human", "ada@example.org")

# (label, author, message, expected lenient, expected strict, expected tool)
COMMITS = [
    ("plain", HUMAN, "Add parser\n\nPlain human commit.", False, False, None),
    (
        "claude-trailer",
        HUMAN,
        "Fix tokenizer\n\nBody.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n"
        "Co-Authored-By: Claude <noreply@anthropic.com>",
        True,
        True,
        "Claude Code",
    ),
    (
        "claude-model-named",
        HUMAN,
        "Speed up loader\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nSigned-off-by: Ada <ada@example.org>",
        True,
        True,
        "Claude Code",
    ),
    (
        "squash-bullet",
        HUMAN,
        "Refactor (#12)\n\n* step one\n\n* Co-authored-by: Cursor <cursoragent@cursor.com>\n\nmore notes here",
        True,
        False,
        "Cursor",
    ),
    (
        "copilot-agent",
        ("Copilot", "198982749+Copilot@users.noreply.github.com"),
        "Add retries (#13)",
        True,
        True,
        "GitHub Copilot",
    ),
    (
        "dependabot",
        ("dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com"),
        "Bump x from 1 to 2",
        False,
        False,
        None,
    ),
    ("human-coauthor", HUMAN, "Pair work\n\nCo-authored-by: Bob <bob@example.org>", False, False, None),
    ("free-text", HUMAN, "Docs\n\nClaude helped me write this, and so did ChatGPT.", False, False, None),
    ("impostor-email", HUMAN, "Thing\n\nCo-authored-by: Claude <claude@example.org>", False, False, None),
]


def _git(repo: Path, *args: str, author: tuple[str, str] = HUMAN, date: str = "2025-06-01T12:00:00Z") -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": author[0],
        "GIT_AUTHOR_EMAIL": author[1],
        "GIT_COMMITTER_NAME": author[0],
        "GIT_COMMITTER_EMAIL": author[1],
        "GIT_AUTHOR_DATE": date,
        "GIT_COMMITTER_DATE": date,
    }
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture(scope="session")
def fixture_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    repo = tmp_path_factory.mktemp("src")
    _git(repo, "init", "-q", "-b", "main")
    for i, (label, author, msg, *_rest) in enumerate(COMMITS):
        (repo / f"{label}.txt").write_text(label)
        _git(repo, "add", ".")
        _git(repo, "commit", "-q", "-m", msg, author=author, date=f"2025-{1 + i % 12:02d}-15T12:00:00Z")
    target = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "revert", "--no-edit", target, date="2025-11-01T00:00:00Z")
    _git(repo, "checkout", "-q", "-b", "side", "HEAD~2")
    (repo / "side.txt").write_text("side")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Side work", date="2025-11-02T00:00:00Z")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--no-ff", "-m", "Merge side", "side", date="2025-11-03T00:00:00Z")
    return repo
