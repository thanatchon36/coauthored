<p align="center"><img src="docs/assets/logo.svg" alt="coauthored logo" width="120"></p>

<h1 align="center">coauthored</h1>

[![CI](https://github.com/thanatchon36/coauthored/actions/workflows/ci.yml/badge.svg)](https://github.com/thanatchon36/coauthored/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Data](https://img.shields.io/badge/data-CC--BY--4.0-blue)](LICENSE-DATA)
[![Status](https://img.shields.io/badge/status-in%20progress-orange)](STATUS.md)

📄 Paper: *in preparation* · 📋 [Status](STATUS.md)

**Who writes the code that trains the models?** `coauthored` counts the commits in a git history that carry
an explicit AI attribution — a `Co-authored-by:` trailer naming an AI tool, an AI-agent bot account, or a
generated-with marker — and the accompanying pre-registered study measures that share month by month,
2023–2026, in the open-source repositories that train, fine-tune, evaluate and serve AI models, against
matched non-AI repositories and against the coding-agent harnesses themselves.

An attributed commit is a **lower bound**: tools can be configured not to attribute, attributions can be
lost at merge, and some tools never attribute. The study measures how much each of those leaks hides. It
reports *attributed* commits, never "AI-written" ones, and publishes repository-month aggregates only.

> **Status: in progress.** No results yet. The design will be frozen in `PREREGISTRATION.md` before any
> study repository is scanned.

> Independent personal research. Public data only. Does not represent the views of any employer or institution.

## License

Code: [Apache-2.0](LICENSE). Aggregated data: [CC-BY-4.0](LICENSE-DATA).
