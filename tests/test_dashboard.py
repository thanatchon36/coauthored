from datetime import date
from pathlib import Path

import polars as pl
import pytest
from test_scan import _scan

from coauthored import dashboard

pytest.importorskip("matplotlib")


def test_last_complete_month() -> None:
    assert dashboard.last_complete_month(date(2026, 11, 2)) == "2026-10"
    assert dashboard.last_complete_month(date(2027, 1, 2)) == "2026-12"


def test_write_from_scanned_fixture(fixture_repo: Path, tmp_path: Path) -> None:
    _scan(fixture_repo, tmp_path)
    page = dashboard.write({"S1": ["fixture/repo"]}, tmp_path / "raw", tmp_path / "site", date(2026, 1, 5))
    s = pl.read_csv(tmp_path / "site" / "monthly.csv")
    assert s["month"].max() <= "2025-12" and set(s["stratum"]) == {"S1"}
    text = page.read_text()
    assert "Post-registration, not part of the paper" in text and "<svg" in text
    assert "S1 model infrastructure" in text and "lower bound" in text


def test_window_marker_only_past_the_window() -> None:
    rows = [
        {"stratum": "S1", "month": m, "n": 10, "n_attr": 1, "share": 0.1}
        for m in ("2026-08", "2026-09", "2026-10")
    ]
    assert "end of pre-registered window" in dashboard.chart(pl.DataFrame(rows))
    assert "end of pre-registered window" not in dashboard.chart(pl.DataFrame(rows[:2]))
