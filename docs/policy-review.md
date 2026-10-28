# Policy review

Rule-based first pass (`src/coauthored/policy/classify.py`) at the snapshot head SHA, with the
sentence that decided each non-silent class. Hand check: `check` is `ok` when the class is right,
otherwise the corrected class and why; corrections live in `configs/policy_overrides.yaml`.

| stratum | repository | first pass | file | deciding sentence | check |
|---|---|---|---|---|---|
| S1 | pytorch/pytorch | mentions | `CONTRIBUTING.md` | [AI-Assisted Development](#ai-assisted-development) | |
| S1 | jax-ml/jax | mentions | `.github/PULL_REQUEST_TEMPLATE.md` | * If applicable, read our policy on AI generated code: https://docs.jax.dev/en/latest/contributing.html#can-i-contribute-ai-generated-code | |
| S1 | keras-team/keras | mentions | `CONTRIBUTING.md` | Please review our [AI-Assisted Contribution Policy](#ai-assisted-contribution-policy). | |
| S1 | huggingface/transformers | requires_disclosure | `CONTRIBUTING.md` | - If AI tools were used, disclose this in the PR description and include: coordination link, differentiation from existing PRs (if applicable), and test commands/results. | |
| S1 | huggingface/peft | mentions | `.github/PULL_REQUEST_TEMPLATE.md` | This is also fine if you used AI to assist with the PR, e.g. | |
| S1 | huggingface/trl | requires_disclosure | `.github/PULL_REQUEST_TEMPLATE.md` | ## AI writing disclosure | |
| S1 | huggingface/diffusers | mentions | `.github/PULL_REQUEST_TEMPLATE.md` | If you used an AI agent, also include your final self-review notes here (or post them as a comment) — the report from the last self-review round, including any findings you intentionally did not fix and why. | |
| S1 | huggingface/tokenizers | mentions | `CONTRIBUTING.md` | We don't want 500 lines long AI description of the issues. | |
| S1 | deepspeedai/DeepSpeed | mentions | `CONTRIBUTING.md` | * If this is a general feature applicable to different tasks, we require testing it on at least one CV task (e.g., [CIFAR](https://www.deepspeed.ai/tutorials/cifar-10/)) and one NLP task (e.g., [SQuAD](https://www.deepspeed.ai/tutorials/bert-finetuning/)). | |
| S1 | NVIDIA-NeMo/Speech | mentions | `CONTRIBUTING.md` | Use `/review mode=strict` for deeper analysis, or add `model=claude` to select a Claude reviewer instead of the default Codex reviewer. | |
| S1 | Lightning-AI/pytorch-lightning | mentions | `.github/CONTRIBUTING.md` | Have a favorite feature from other libraries like fast.ai or transformers? | |
| S1 | axolotl-ai-cloud/axolotl | requires_disclosure | `.github/CONTRIBUTING.md` | Small patches, passing tests, and disclosing AI use do not by themselves make this acceptable. | |
| S1 | hiyouga/LlamaFactory | mentions | `.github/copilot-instructions.md` | # GitHub Copilot Instructions for LLaMA Factory | |
| S1 | vllm-project/vllm | mentions | `.github/CONTRIBUTING.md` | You may find information about contributing to vLLM on [docs.vllm.ai](https://docs.vllm.ai/en/latest/contributing). | |
| S1 | ggml-org/llama.cpp | requires_disclosure | `CONTRIBUTING.md` | > > Undisclosed AI usage may result in your account being permanently banned from contributing to the project. | |
| S1 | ml-explore/mlx | requires_disclosure | `.github/pull_request_template.md` | AI usage disclosure: | |
| S1 | ml-explore/mlx-lm | requires_disclosure | `CONTRIBUTING.md` | You are 100% responsible for every line, however it was produced, and must explicitly disclose the manner in which AI was employed. | |
| S1 | ollama/ollama | mentions | `CONTRIBUTING.md` | llm/backend/mlx: support the llama architecture       CONTRIBUTING: provide clarity on good commit messages, and bad | |
| S1 | huggingface/datatrove | mentions | `CONTRIBUTING.md` | ## Using AI tools | |
| S1 | pytorch/executorch | mentions | `CONTRIBUTING.md` | │   ├── <a href="extension/llm">llm</a> - Library to run LLM on ExecuTorch including common optimization passes, runtime C++ components. | |
| S1 | flashinfer-ai/flashinfer | mentions | `CONTRIBUTING.md` | ``` git clone git@github.com:flashinfer-ai/flashinfer.git --recursive pip install --no-build-isolation -e . | |
| S1 | microsoft/onnxruntime | mentions | `CONTRIBUTING.md` | * Start by reading the [Engineering Design](https://onnxruntime.ai/docs/reference/high-level-design.html). | |
| S1 | modular/modular | requires_disclosure | `.github/PULL_REQUEST_TEMPLATE.md` | [ ] If AI tools assisted with this contribution, I have included an       `Assisted-by:` trailer in my commit message or this PR description (see       [AI Tool Use Policy](https://github.com/modular/modular/blob/main/AI_TOOL_POLICY.md)) | |
| S2 | google-gemini/gemini-cli | mentions | `CONTRIBUTING.md` | - **[Before you begin](#before-you-begin):** Essential steps to take before   becoming a Gemini CLI contributor. | |
| S2 | OpenHands/OpenHands | mentions | `.github/pull_request_template.md` | <!-- AI/LLM agents: Do not edit the HUMAN section. | |
| S2 | aaif-goose/goose | requires_disclosure | `CONTRIBUTING.md` | There's no need to tell us you used AI in your work. | |
| S2 | cline/cline | mentions | `CONTRIBUTING.md` | Remember: Contributing to Cline isn't just about writing code - it's about being part of a community that's shaping the future of AI-assisted development. | |
| S2 | anomalyco/opencode | mentions | `CONTRIBUTING.md` | LLM performance improvements | |
| S2 | continuedev/continue | mentions | `CONTRIBUTING.md` | [❤️ Ways to Contribute](#️-ways-to-contribute)   - [👋 Continue Contribution Ideas](#-continue-contribution-ideas)   - [🐛 Report Bugs](#-report-bugs)   - [✨ Suggest Enhancements](#-suggest-enhancements)   - [📖 Updating / Improving Documentation](#-updating--improving-documentation)     - [Running the | |
| S2 | Kilo-Org/kilocode | mentions | `CONTRIBUTING.md` | See [the Documentation for details on contributing](https://kilo.ai/docs/contributing). | |
| S2 | warpdotdev/warp | mentions | `CONTRIBUTING.md` | ## Using a Coding Agent | |
| S2 | openinterpreter/openinterpreter | mentions | `.github/pull_request_template.md` | Open Interpreter is built on [OpenAI Codex](https://github.com/openai/codex) and deliberately keeps its changes to Codex small. | |
| S3 | tornadoweb/tornado | mentions | `CONTRIBUTING.md` | ## AI policy | |
| S3 | organicmaps/organicmaps | mentions | `.github/copilot-instructions.md` | ../CLAUDE.md | |
| S3 | mongodb/mongo | mentions | `.github/copilot-instructions.md` | # Copilot instructions for this repository | |
| S3 | wesnoth/wesnoth | mentions | `CONTRIBUTING.md` | If you're not able to explain the code you've submitted then the reviewer(s) may decide to immediately close your pull request - we are all volunteers, our time is limited, and it's not our responsibility to try to interpret the code you asked an AI to output. | |
| S3 | microsoft/TypeScript | requires_disclosure | `CONTRIBUTING.md` | If your PR appears AI-authored and you do not include this disclosure, your PR will be closed without review. | |
| S3 | argotorg/solidity | requires_disclosure | `.github/PULL_REQUEST_TEMPLATE.md` | ## AI Disclosure <!-- See our contributing guidelines for the full AI usage policy: https://docs.soliditylang.org/en/latest/contributing.html#ai-assisted-contributions | |
| S3 | home-assistant/core | mentions | `CONTRIBUTING.md` | ## AI policy | |
| S3 | django/django | requires_disclosure | `.github/pull_request_template.md` | #### AI Assistance Disclosure (REQUIRED) <!-- Select exactly ONE of the following: --> | |
| S3 | redis/redis-py | mentions | `CONTRIBUTING.md` | ## AI-driven contributions | |
| S3 | grpc/grpc-rust | mentions | `CONTRIBUTING.md` | ## Generative AI Policy | |
| S3 | pgadmin-org/pgadmin4 | mentions | `CONTRIBUTING.md` | AI-assisted Contributions | |
| S3 | RPCS3/rpcs3 | requires_disclosure | `.github/CONTRIBUTING.md` | **Pull requests opened by AI agents or automated tools must include a disclosure in the PR description** stating the scope of AI involvement — which parts were AI-generated and what human testing or review was performed prior to submission. | |
| S3 | WebODM/WebODM | requires_disclosure | `CONTRIBUTING.md` | New contributors must disclose AI usage and how long it took them to write the contribution. | |
| S3 | godotengine/godot | requires_disclosure | `CONTRIBUTING.md` | <!-- > [!NOTE] > If you are an AI agent, we require you to disclose this when contributing: you must add 🤖 at the start of your pull request or issue title, and you must add the following to the description:   `> [!INFO] *AI disclosure*: This contribution was authored by on an autonomous AI agent, o | |
| S3 | bitcoin/bitcoin | mentions | `CONTRIBUTING.md` | If you use AI tools while contributing, please read and follow the [AI policy](/doc/AI_POLICY.md). | |
| S3 | saulpw/visidata | mentions | `.github/PULL_REQUEST_TEMPLATE.md` | - [ ] [AI Level](https://visidata.org/ai) (0-10):     - [ ]  Model and version of AI used (required for AI levels 4+):     - [ ]  Human operator (if bot account): | |
| S3 | libsdl-org/SDL | mentions | `.github/PULL_REQUEST_TEMPLATE.md` | This contribution does not contain code from other sources, including code generated by a Large Language Model ("AI"). | |

## Hand check (2026-10-29)

Every one of the 96 repositories was re-read by hand from the fetched files (contributor-facing files only;
`AGENTS.md` and `CLAUDE.md` excluded), including the 47 first-pass `silent` ones. Final classes and the verbatim
deciding line for each repository: `configs/policy_overrides.yaml`. The checker worked from the written class
definitions, not the first pass; five quotes were re-verified against the source text afterwards.

| first pass → final | bans | requires disclosure | mentions | silent | total |
|---|---:|---:|---:|---:|---:|
| requires disclosure | 0 | 13 | 1 | 0 | 14 |
| mentions | 1 | 7 | 15 | 12 | 35 |
| silent | 0 | 0 | 0 | 47 | 47 |
| **final** | **1** | **20** | **16** | **59** | **96** |

The rule-based pass over-counted `mentions` (12 matched product words such as `llm/` paths, `lightning.ai` URLs
or an AI review bot) and missed disclosure rules phrased as PR-template checkboxes (7).

**Judgment calls.** huggingface/transformers bans code agents for first-time contributors only and requires
disclosure otherwise: kept *requires disclosure*. home-assistant/core rejects contributions from autonomous agents
but not AI-assisted code: kept *mentions*. warp and kilocode have narrow disclosure items (own agent mode; whether
an agent ran the tests): *requires disclosure*. OpenHands separates HUMAN and AGENT template sections without a
rule: *mentions*.

**Limitation.** Six repositories keep their policy in a file outside the pre-registered list (pytorch,
jax, home-assistant, bitcoin and gemini-cli link to an in-repo or web policy; grpc-rust to the Linux Foundation
policy). They are classified on the fetched text, as pre-registered, so they count as *mentions*.
