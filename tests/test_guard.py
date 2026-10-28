import pytest

from coauthored import guard


def test_no_keys_passes() -> None:
    guard.check({})


def test_empty_key_passes() -> None:
    guard.check({"ANTHROPIC_API_KEY": ""})


@pytest.mark.parametrize("key", guard.PAID_KEYS)
def test_each_key_refused(key: str) -> None:
    with pytest.raises(guard.PaidKeyError, match=key):
        guard.check({key: "sk-x"})
