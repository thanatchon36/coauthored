"""Apply the inclusion rule (DECISIONS D6) to cache/candidates_meta.json and write the S1/S2 part of
configs/repos.yaml. S3 is appended by `coauthored match`. Judgment exclusions are listed here with reasons.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

MIN_STARS = 2000
MIN_COMMITS_12M = 200  # 2025-10-01 .. 2026-10-01, default branch, API count
MIN_COMMITS_2024 = 100  # S1 and S3 only: active before the trend window's second half

JUDGMENT_EXCLUDE = {
    "huggingface/huggingface_hub": (
        "S1 scope: a Hub client for distributing models and datasets, not training, fine-tuning, "
        "evaluating or serving"
    ),
    "zed-industries/zed": (
        "S2 scope: describes itself as a code editor; the agent is a feature, not the product"
    ),
    "anthropics/claude-code": (
        "S2 scope: harness source is not in the repository (plugins, examples, changelog)"
    ),
    "github/copilot-cli": "S2 scope: harness source is not in the repository (issues and releases only)",
}
LAYER = {"extra": None}  # S1 'extra' candidates are assigned a layer below
EXTRA_LAYER = {
    "pytorch/ao": "kernels_compilers",
    "pytorch/executorch": "inference_serving",
    "NVIDIA/TransformerEngine": "kernels_compilers",
    "flashinfer-ai/flashinfer": "kernels_compilers",
    "InternLM/lmdeploy": "inference_serving",
    "microsoft/onnxruntime": "inference_serving",
    "openxla/xla": "kernels_compilers",
    "tensorflow/tensorflow": "training_frameworks",
    "modular/modular": "inference_serving",
    "stanford-crfm/helm": "evaluation_data",
}


def main() -> None:
    meta = json.loads(Path("cache/candidates_meta.json").read_text())
    out: dict[str, list[dict]] = {"s1": [], "s2": []}
    excluded: list[dict] = []
    seen: set[str] = set()
    for rec in meta.values():
        if "error" in rec:
            excluded.append({"repo": rec["query"], "stratum": rec["stratum"], "reason": "not found"})
            continue
        full = rec["full_name"]
        if full in seen:
            continue
        seen.add(full)
        s = rec["stratum"]
        reasons = []
        if rec["stars"] < MIN_STARS:
            reasons.append(f"stars {rec['stars']} < {MIN_STARS}")
        if rec["commits_12m"] < MIN_COMMITS_12M:
            reasons.append(f"commits_12m {rec['commits_12m']} < {MIN_COMMITS_12M}")
        if s == "s1" and rec["commits_2024"] < MIN_COMMITS_2024:
            reasons.append(f"commits_2024 {rec['commits_2024']} < {MIN_COMMITS_2024}")
        if rec["archived"] or rec["fork"]:
            reasons.append("archived or fork")
        if full in JUDGMENT_EXCLUDE:
            reasons.append(JUDGMENT_EXCLUDE[full])
        if reasons:
            excluded.append({"repo": full, "stratum": s, "reason": "; ".join(reasons)})
            continue
        layer = EXTRA_LAYER.get(full, rec["layer"]) if s == "s1" else "harness"
        out[s].append(
            {
                "repo": full,
                "layer": layer,
                "language": rec["language"],
                "stars": rec["stars"],
                "commits_2024": rec["commits_2024"],
                "commits_12m": rec["commits_12m"],
                "created_at": rec["created_at"][:10],
                "rationale": (rec["description"] or "").strip()[:160],
            }
        )
    doc = {
        "rule": {
            "min_stars": MIN_STARS,
            "min_commits_12m": MIN_COMMITS_12M,
            "min_commits_2024_s1_s3": MIN_COMMITS_2024,
            "window_12m": "2025-10-01..2026-10-01",
            "counted_via": "GitHub REST commits API, default branch",
        },
        "s1": out["s1"],
        "s2": out["s2"],
        "excluded": excluded,
    }
    Path("configs/repos.yaml").write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120))
    print(f"S1={len(out['s1'])} S2={len(out['s2'])} excluded={len(excluded)}")


if __name__ == "__main__":
    main()
