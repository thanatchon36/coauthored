"""Write paper/repositories.md, the appendix list of study repositories, from the frozen configs/repos.yaml.

Repositories excluded by the inclusion rule, with the failing criterion, are listed under `excluded` in the
same file; S3 screening decisions are in configs/s3_screen.yaml.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

LAYER = {
    "training_frameworks": "Training frameworks",
    "model_libraries": "Model libraries",
    "distributed_training": "Distributed training",
    "finetuning_rl": "Fine-tuning and RL",
    "inference_serving": "Inference and serving",
    "kernels_compilers": "Kernels and compilers",
    "evaluation_data": "Evaluation and data",
}


def main() -> None:
    cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    by_layer: dict[str, list[str]] = defaultdict(list)
    for r in cfg["s1"]:
        by_layer[r["layer"]].append(r["repo"])
    rows = ["| Group | Repositories |", "|---|---|"]
    rows += [f"| S1 · {LAYER[k]} | {', '.join(sorted(by_layer[k]))} |" for k in LAYER if k in by_layer]
    rows.append(f"| S2 · Coding-agent harnesses | {', '.join(sorted(r['repo'] for r in cfg['s2']))} |")
    # one S3 row per S1 layer, so that no table cell runs past a page
    layer_of = {r["repo"]: r["layer"] for r in cfg["s1"]}
    controls: dict[str, list[str]] = defaultdict(list)
    for r in cfg["s3"]:
        controls[layer_of[r["matched_to"]]].append(r["repo"])
    rows += [
        f"| S3 · controls for {LAYER[k][0].lower() + LAYER[k][1:]} | {', '.join(sorted(controls[k]))} |"
        for k in LAYER
        if k in controls
    ]
    Path("paper/repositories.md").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
