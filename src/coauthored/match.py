"""Matched non-AI controls for S1 (MISSION §3.5 S3, DECISIONS D6).

For each S1 repository, in a seeded order, pick the unused pool candidate in the same language group whose
stars and last-12-month commit count are both within the caliper (±50%), minimising
``|log(stars ratio)| + |log(commits ratio)|``. When no candidate is inside the caliper, the nearest candidate
in the language group is taken and flagged ``caliper_violated``. Run once; the output is frozen.
"""

from __future__ import annotations

import math
import random
import re
from typing import Any

LANGUAGE_GROUP = {
    "Python": "python",
    "Jupyter Notebook": "python",
    "C++": "c-family",
    "C": "c-family",
    "Cuda": "c-family",
    "MLIR": "c-family",
    "Mojo": "c-family",
    "Go": "go",
    "Rust": "rust",
    "TypeScript": "js",
    "JavaScript": "js",
}

AI_TOPICS = {
    "ai",
    "artificial-intelligence",
    "machine-learning",
    "deep-learning",
    "llm",
    "llms",
    "nlp",
    "gpt",
    "chatgpt",
    "openai",
    "agent",
    "agents",
    "ai-agent",
    "ai-agents",
    "agentic-ai",
    "mcp",
    "rag",
    "pytorch",
    "tensorflow",
    "transformers",
    "generative-ai",
    "genai",
    "computer-vision",
    "neural-network",
    "neural-networks",
    "ml",
    "data-science",
    "large-language-models",
    "claude",
    "anthropic",
    "gemini",
    "copilot",
    "ollama",
    "langchain",
    "stable-diffusion",
    "diffusion",
    "inference",
    "embeddings",
    "vector-database",
    "chatbot",
    "speech-recognition",
}
AI_TEXT = re.compile(
    r"\b(ai|a\.i\.|llms?|gpt|machine[- ]learning|deep[- ]learning|neural|agents?|agentic|copilot|"
    r"chatgpt|openai|anthropic|claude|gemini|transformers?|inference|model context protocol|mcp|rag|"
    r"embeddings?|diffusion|ml|artificial intelligence|language models?|chatbot|vector)\b",
    re.I,
)
NOT_SOFTWARE = re.compile(
    r"\b(awesome|curated|list of|interview|tutorials?|roadmap|cheat ?sheet|books?)\b", re.I
)


def group(language: str | None) -> str | None:
    return LANGUAGE_GROUP.get(language or "")


def is_eligible_control(rec: dict[str, Any], min_stars: int, min_12m: int, min_2024: int) -> tuple[bool, str]:
    """Pool rule for S3: same activity rule as S1 (D6), non-AI, a software project."""
    if rec.get("archived") or rec.get("fork"):
        return False, "archived or fork"
    if group(rec.get("language")) is None:
        return False, f"language {rec.get('language')} outside the S1 language groups"
    if AI_TOPICS & set(rec.get("topics", [])):
        return False, "AI/ML topic"
    text = f"{rec.get('full_name', '')} {rec.get('description', '')}"
    if AI_TEXT.search(text):
        return False, "AI/ML term in name or description"
    if NOT_SOFTWARE.search(text):
        return False, "not a software project"
    if rec.get("stars", 0) < min_stars:
        return False, "stars"
    if rec.get("commits_12m", 0) < min_12m or rec.get("commits_2024", 0) < min_2024:
        return False, "activity"
    return True, ""


def _distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    return abs(math.log(b["stars"] / a["stars"])) + abs(math.log(b["commits_12m"] / a["commits_12m"]))


def _inside(a: dict[str, Any], b: dict[str, Any], caliper: float) -> bool:
    return all((1 - caliper) * a[k] <= b[k] <= (1 + caliper) * a[k] for k in ("stars", "commits_12m"))


def match(
    treated: list[dict[str, Any]], pool: list[dict[str, Any]], seed: int, caliper: float = 0.5
) -> list[dict[str, Any]]:
    order = sorted(treated, key=lambda r: r["repo"])
    random.Random(seed).shuffle(order)
    used: set[str] = set()
    out = []
    for t in order:
        g = group(t["language"])
        cands = [p for p in pool if group(p["language"]) == g and p["full_name"] not in used]
        if not cands:
            out.append({"treated": t["repo"], "control": None, "caliper_violated": True, "distance": None})
            continue
        inside = [p for p in cands if _inside(t, p, caliper)]
        best = min(inside or cands, key=lambda p: (_distance(t, p), p["full_name"]))
        used.add(best["full_name"])
        out.append(
            {
                "treated": t["repo"],
                "control": best["full_name"],
                "language_group": g,
                "caliper_violated": not inside,
                "distance": round(_distance(t, best), 4),
                "treated_stars": t["stars"],
                "control_stars": best["stars"],
                "treated_commits_12m": t["commits_12m"],
                "control_commits_12m": best["commits_12m"],
            }
        )
    return out
