"""Signature catalogue: the exact identities and verbatim markers that make a commit AI-attributed.

Three kinds (MISSION §3.3):

- ``coauthor``: a ``Co-authored-by:`` line whose identity matches.
- ``identity``: the commit's author or committer identity matches (AI-agent accounts).
- ``marker``: a verbatim substring of the commit message.

Identity patterns are full-match regular expressions on the lower-cased email and/or name. They stand for
one exact identity or a closed family (for example model-named ``Claude <noreply@anthropic.com>`` variants);
free-text words such as "AI" or "Claude" alone are never a signature.
"""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

Kind = Literal["coauthor", "identity", "marker"]


class Signature(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    tool: str
    kind: Kind
    email: str | None = None
    name: str | None = None
    text: str | None = None
    query: str | None = None  # GitHub commit-search query used to collect evidence
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def _check_fields(self) -> Signature:
        if self.kind == "marker":
            if not self.text or self.email or self.name:
                raise ValueError(f"{self.id}: a marker needs `text` only")
        elif not (self.email or self.name) or self.text:
            raise ValueError(f"{self.id}: a {self.kind} signature needs `email` and/or `name`")
        for pattern in (self.email, self.name):
            if pattern is not None:
                re.compile(pattern)
        return self

    @cached_property
    def _email_re(self) -> re.Pattern[str] | None:
        return re.compile(self.email) if self.email else None

    @cached_property
    def _name_re(self) -> re.Pattern[str] | None:
        return re.compile(self.name) if self.name else None

    def matches_identity(self, name: str, email: str) -> bool:
        """Full-match on lower-cased name and email; every pattern given must match."""
        if self.kind == "marker":
            return False
        if self._email_re is not None and not self._email_re.fullmatch(email.strip().lower()):
            return False
        return self._name_re is None or bool(self._name_re.fullmatch(name.strip().lower()))


class Catalogue(BaseModel):
    version: str
    signatures: list[Signature]

    @model_validator(mode="after")
    def _unique_ids(self) -> Catalogue:
        ids = [s.id for s in self.signatures]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"duplicate signature ids: {sorted(dupes)}")
        return self

    def of_kind(self, kind: Kind) -> list[Signature]:
        return [s for s in self.signatures if s.kind == kind]

    def unqualified(self, min_evidence: int = 3) -> list[Signature]:
        """Signatures that lack the evidence MISSION §1.6 requires."""
        return [s for s in self.signatures if len(set(s.evidence)) < min_evidence]


def load(path: Path) -> Catalogue:
    return Catalogue.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
