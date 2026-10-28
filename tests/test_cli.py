import json
from pathlib import Path

import polars as pl
import pytest
import yaml
from conftest import FIXTURES
from typer.testing import CliRunner

from coauthored.cli import app
from coauthored.scan import identity

runner = CliRunner()


def test_version() -> None:
    r = runner.invoke(app, ["version"])
    assert r.exit_code == 0 and r.stdout.strip()


def test_paid_key_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert runner.invoke(app, ["version"]).exit_code != 0


def test_signatures_verify_flags_missing_evidence() -> None:
    r = runner.invoke(app, ["signatures", "--catalogue", str(FIXTURES / "catalogue.yaml"), "--verify"])
    assert r.exit_code == 1
    assert "claude" in r.stdout.lower()


def test_scan_then_aggregate(fixture_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(identity.SALT_VAR, "salt")
    cfg = tmp_path / "repos.yaml"
    cfg.write_text(yaml.safe_dump({"s1": [{"repo": "fixture/repo"}]}))
    manifest = tmp_path / "manifest.json"
    common = ["--config", str(cfg)]
    r = runner.invoke(
        app,
        [
            "scan",
            *common,
            "--catalogue",
            str(FIXTURES / "catalogue.yaml"),
            "--bots",
            str(FIXTURES / "bots.yaml"),
            "--manifest",
            str(manifest),
            "--workdir",
            str(tmp_path / "work"),
            "--rawdir",
            str(tmp_path / "raw"),
            "--url-template",
            str(fixture_repo),
        ],
    )
    assert r.exit_code == 0, r.output
    assert "fixture/repo" in json.loads(manifest.read_text())["repos"]
    out = tmp_path / "agg"
    r = runner.invoke(app, ["aggregate", *common, "--rawdir", str(tmp_path / "raw"), "--out", str(out)])
    assert r.exit_code == 0, r.output
    rm = pl.read_parquet(out / "repo_month.parquet")
    assert set(rm["spec"].unique()) >= {"primary", "strict_trailers"}


def test_salt_from_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(identity.SALT_VAR, raising=False)
    env = tmp_path / ".env"
    with pytest.raises(RuntimeError):
        identity.load_salt(env, create=False)
    created = identity.load_salt(env)
    assert len(created) == 64 and identity.load_salt(env) == created
    env.write_text("OTHER=1\nHASH_SALT=abc\n")
    assert identity.load_salt(env) == "abc"


def test_hash_identity_uses_email_then_name() -> None:
    a = identity.hash_identity("Ada", "ADA@example.org ", "s")
    assert a == identity.hash_identity("Someone", "ada@example.org", "s")
    assert identity.hash_identity("Ada", "", "s") != identity.hash_identity("Bob", "", "s")
