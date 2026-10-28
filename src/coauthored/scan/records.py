"""Turn a raw commit into the stored record: flags and hashes, no names, no emails, no message."""

from __future__ import annotations

import re
from typing import Any

from coauthored.bots import BotList
from coauthored.scan.gitlog import RawCommit
from coauthored.scan.identity import hash_identity
from coauthored.signatures.catalogue import Catalogue
from coauthored.signatures.matcher import Identity, match_commit

_REVERT_RE = re.compile(r'^Revert "', re.M)
_REVERTED_SHA_RE = re.compile(r"This reverts commit ([0-9a-f]{7,40})")
# commits exported from a private monorepo; attribution on the private side cannot survive (DECISIONS D8)
MIRROR_RE = re.compile(
    r"^(PiperOrigin-RevId|fbshipit-source-id|GitOrigin-RevId|MODULAR_ORIG_COMMIT_REV_ID):", re.M | re.I
)


def _is_agent(catalogue: Catalogue, who: Identity) -> bool:
    return any(s.matches_identity(who.name, who.email) for s in catalogue.of_kind("identity"))


def build(
    raw: RawCommit, catalogue: Catalogue, bots: BotList, salt: str, first_parent: set[str]
) -> dict[str, Any]:
    author = Identity(raw.author_name, raw.author_email)
    committer = Identity(raw.committer_name, raw.committer_email)
    m = match_commit(catalogue, author, committer, raw.message)
    reverted = _REVERTED_SHA_RE.search(raw.message)
    return {
        "sha": raw.sha,
        "n_parents": len(raw.parents),
        "first_parent": raw.sha in first_parent,
        "author_date": raw.author_date,
        "committer_date": raw.committer_date,
        "author_h": hash_identity(author.name, author.email, salt),
        "committer_h": hash_identity(committer.name, committer.email, salt),
        # an AI-agent account is never a maintenance bot, even with a [bot] suffix (DECISIONS D7)
        "author_maint_bot": bots.is_bot(author.name, author.email) and not _is_agent(catalogue, author),
        "committer_maint_bot": bots.is_bot(committer.name, committer.email)
        and not _is_agent(catalogue, committer),
        "attributed": m.attributed,
        "attributed_strict": m.attributed and m.strict,
        "signature_ids": m.signature_ids,
        "tool": m.tool,
        "n_coauthor_lines": len(m.coauthors),
        "bare_assisted": m.bare_assisted,
        "is_revert": bool(_REVERT_RE.match(raw.message)),
        "mirror_export": bool(MIRROR_RE.search(raw.message)),
        "reverted_sha": reverted.group(1) if reverted else None,
    }
