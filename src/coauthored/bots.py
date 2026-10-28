"""Maintenance bots excluded from the denominator (MISSION §3.2, DECISIONS D7).

Rule: a commit is a maintenance-bot commit when its *author* is (a) any account whose name ends in ``[bot]``
and that is not an AI-agent account in the signature catalogue, or (b) a listed automation identity without
the suffix. Committers are ignored: merge and export bots commit human work.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

_BOT_SUFFIX = re.compile(r".*\[bot\]")


class Bot(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    query: str | None = None
    evidence: list[str] = Field(default_factory=list)

    def matches(self, name: str, email: str) -> bool:
        if self.email and not re.fullmatch(self.email, email.strip().lower()):
            return False
        if self.name and not re.fullmatch(self.name, name.strip().lower()):
            return False
        return bool(self.email or self.name)


class BotList(BaseModel):
    version: str
    bot_suffix_rule: bool = True
    bots: list[Bot] = Field(default_factory=list)

    def is_bot(self, name: str, email: str) -> bool:
        if self.bot_suffix_rule and _BOT_SUFFIX.fullmatch(name.strip().lower()):
            return True
        return any(b.matches(name, email) for b in self.bots)


def load(path: Path) -> BotList:
    return BotList.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
