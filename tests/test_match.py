from coauthored.match import is_eligible_control, match


def rec(name: str, lang: str, stars: int, c12: int, **kw: object) -> dict:
    return {
        "full_name": name,
        "repo": name,
        "language": lang,
        "stars": stars,
        "commits_12m": c12,
        "commits_2024": 500,
        "topics": [],
        "description": "",
        **kw,
    }


def test_eligibility_rules() -> None:
    ok, _ = is_eligible_control(rec("a/web", "Go", 5000, 400), 2000, 200, 100)
    assert ok
    for bad in (
        rec("a/b", "Go", 5000, 400, topics=["machine-learning"]),
        rec("a/b", "Go", 5000, 400, description="An AI-powered terminal"),
        rec("a/b", "Go", 5000, 400, description="Awesome list of Go things"),
        rec("a/b", "Haskell", 5000, 400),
        rec("a/b", "Go", 1000, 400),
        rec("a/b", "Go", 5000, 100),
        rec("a/b", "Go", 5000, 400, archived=True),
    ):
        assert not is_eligible_control(bad, 2000, 200, 100)[0], bad


def test_match_prefers_inside_caliper_and_same_group() -> None:
    treated = [rec("t/py", "Python", 10000, 1000), rec("t/go", "Go", 10000, 1000)]
    pool = [
        rec("c/py-near", "Jupyter Notebook", 11000, 900),
        rec("c/py-far", "Python", 100000, 50),
        rec("c/go", "Go", 30000, 3000),  # outside caliper, but the only Go candidate
    ]
    out = {m["treated"]: m for m in match(treated, pool, seed=1)}
    assert out["t/py"]["control"] == "c/py-near" and not out["t/py"]["caliper_violated"]
    assert out["t/go"]["control"] == "c/go" and out["t/go"]["caliper_violated"]


def test_match_is_deterministic_and_without_replacement() -> None:
    treated = [rec(f"t/{i}", "Rust", 5000 + i, 300 + i) for i in range(5)]
    pool = [rec(f"c/{i}", "Rust", 5000 + 10 * i, 300 + 10 * i) for i in range(8)]
    a, b = match(treated, pool, seed=7), match(treated, pool, seed=7)
    assert a == b
    controls = [m["control"] for m in a]
    assert len(set(controls)) == len(controls)
