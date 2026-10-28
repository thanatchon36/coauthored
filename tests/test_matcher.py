import pytest
from conftest import FIXTURES

from coauthored.signatures import catalogue as cat_mod
from coauthored.signatures.matcher import Identity, match_commit, trailer_block

CAT = cat_mod.load(FIXTURES / "catalogue.yaml")
H = Identity("Ada", "ada@example.org")


def test_precedence_trailer_over_marker() -> None:
    msg = "x\n\nGenerated with [Claude Code](u)\n\nCo-authored-by: Cursor <cursoragent@cursor.com>"
    m = match_commit(CAT, H, H, msg)
    assert m.tool == "Cursor"
    assert m.tools == ["Claude Code", "Cursor"]


def test_identity_beats_marker() -> None:
    bot = Identity("Copilot", "198982749+Copilot@users.noreply.github.com")
    m = match_commit(CAT, bot, H, "x\n\nGenerated with [Claude Code](u)")
    assert m.tool == "GitHub Copilot"


def test_case_insensitive_key_and_email() -> None:
    assert match_commit(CAT, H, H, "x\n\nCO-AUTHORED-BY: Claude <NoReply@Anthropic.com>").attributed


def test_marker_alone_counts() -> None:
    m = match_commit(CAT, H, H, "x\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)")
    assert m.attributed and m.strict


@pytest.mark.parametrize(
    "msg,expected",
    [
        ("subject only", 0),
        ("subject\n\nbody\n\nSigned-off-by: a <b>\nCo-authored-by: c <d>", 2),
        ("subject\n\nCo-authored-by: c <d>\nnot a trailer", 0),
        ("subject\n\nKey: v\n  continued", 2),
    ],
)
def test_trailer_block(msg: str, expected: int) -> None:
    assert len(trailer_block(msg)) == expected


def test_bad_signature_rejected() -> None:
    with pytest.raises(ValueError):
        cat_mod.Signature(id="x", tool="t", kind="marker", email="a")
    with pytest.raises(ValueError):
        cat_mod.Signature(id="x", tool="t", kind="coauthor")


def test_unqualified_lists_missing_evidence() -> None:
    assert {s.id for s in CAT.unqualified()} == {s.id for s in CAT.signatures}


@pytest.mark.parametrize("key", ["Co-authored-by", "Assisted-by", "Co-developed-by", "* Co-Authored-By"])
def test_attribution_keys(key: str) -> None:
    assert match_commit(CAT, H, H, f"x\n\n{key}: Cursor <cursoragent@cursor.com>").attributed


def test_signed_off_by_is_not_attribution() -> None:
    assert not match_commit(CAT, H, H, "x\n\nSigned-off-by: Cursor <cursoragent@cursor.com>").attributed


@pytest.mark.parametrize(
    "line,bare",
    [
        ("Assisted-by: Claude:claude-opus-4 coccinelle sparse", True),
        ("Assisted-by: GPT:gpt-5", True),
        ("Assisted-by: Claude <noreply@anthropic.com>", False),
        ("Assisted-by: a colleague", False),
    ],
)
def test_bare_assisted_is_flagged_not_counted(line: str, bare: bool) -> None:
    m = match_commit(CAT, H, H, f"Fix a bug\n\n{line}\n")
    assert m.bare_assisted is bare
    assert m.attributed is (not bare and "anthropic" in line)
