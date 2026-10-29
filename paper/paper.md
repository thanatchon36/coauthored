---
title: "Who Writes the Code That Trains the Models? AI Co-Authorship Trailers in AI Infrastructure Repositories, 2023–2026"
author: "Thanatchon Chongmankhong"
date: "October 2026"
bibliography: paper/refs.bib
csl: paper/csl/ieee.csl
link-citations: true
numbersections: true
section-numbering: "1.1"
mainfont: "Libertinus Serif"
fontsize: 10pt
papersize: a4
margin:
  x: 2.2cm
  y: 2.4cm
abstract: |
  Coding agents now sign their work: Claude Code, Copilot's cloud agent, Codex, Cursor, Jules and others leave
  co-author trailers, agent author accounts or verbatim markers in commit metadata. We use these signatures to
  measure, month by month from 2023 to 2026, the share of commits to the open-source repositories that train,
  fine-tune, evaluate and serve AI models that carry an explicit AI attribution, and compare it with matched
  popular non-AI repositories and with the coding-agent harnesses themselves. The design was pre-registered
  before any study repository was scanned. Every repository's full default-branch history was read on one day
  ({{summary.snapshot.repositories}} repositories, {{summary.snapshot.commits_all|,}} commits), and matched
  against a published catalogue of {{summary.catalogue.entries}} signatures for {{summary.catalogue.tools}}
  tools, each backed by three public example commits. In July–September 2026,
  {{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}} of commits to AI-infrastructure repositories were
  AI-attributed (95% CI {{summary.quarterly[stratum=S1,q=2026-Q3].lo|pct1}}–{{summary.quarterly[stratum=S1,q=2026-Q3].hi|pct1}}),
  up from {{summary.year[stratum=S1,year=2025].share|pct1}} over 2025 and almost none in 2024. Matched non-AI
  repositories reached {{summary.quarterly[stratum=S3,q=2026-Q3].share|pct1}} and the coding-agent harnesses
  {{summary.quarterly[stratum=S2,q=2026-Q3].share|pct1}}, with intervals too wide to tell the three groups apart:
  we find no evidence that AI infrastructure is ahead, but cannot rule out a sizeable lead either. Of the
  pre-registered hypotheses about level, difference, growth, recursion and tools, only the level hypothesis meets
  its decision rule, and only on its point estimate; its interval reaches below the threshold. Attribution is a
  lower bound: it can be switched off, lost at merge, dropped when code is exported from a private monorepo, or
  never added. We measure the merge path directly: {{hypotheses[hypothesis=H6].estimate|pct}} of sampled
  attributed pull requests keep an attribution on the default branch. We release the scanner so that any
  organisation can draw the same curve for its own repositories.
---

<!-- Independent personal research. Every number below is filled from results/numbers.json by `coauthored paper`. -->

# Introduction

Frontier laboratories now say that most of their own code is written with their models. Anthropic reports that
more than eighty percent of the lines of code merged into its codebase in May 2026 could be attributed to Claude
[@favaro2026]. <!-- numbers-ok: quoted from the cited source --> Such figures come from inside one laboratory, count lines rather than commits, and cannot be checked from outside. The question
behind them can be asked in public, though: *how much of the open-source code that trains and serves AI models
is already produced with AI tools?* We answer a narrower and checkable version of it: what share of commits to
that code *declare* AI involvement in their metadata?

We find that the answer in mid-2026 is about one commit in {{summary.quarterly[stratum=S1,q=2026-Q3].share|inv}}
({{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}} in July–September 2026), and almost nothing before 2025
(Figure @fig:f1). The comparison is the part we expected to be different. Popular repositories with nothing to
do with AI, matched on stars, language and activity, carry AI attribution at a similar rate
({{summary.quarterly[stratum=S3,q=2026-Q3].share|pct1}}), and in {{robustness.s1_below_s3_2026.count}} of the
{{robustness.s1_below_s3_2026.of}} months of 2026 the controls were *above* the AI-infrastructure repositories.
The open-source coding-agent harnesses, the tools that produce these attributions, started earlier but are not
clearly ahead in 2026. We read this as inconclusive rather than as equality: the intervals are wide, one control
repository supplies {{robustness.s3_top_repo.fraction_of_attributed|pct}} of the controls' attributed commits in
the quarter, and some AI-infrastructure repositories are exported from internal monorepos, so their public
commits cannot show attribution. What the data do not show is the clear lead of "AI building AI" that we pre-registered.

The instrument is simple, and the simplicity is deliberate. Many coding agents add a signature to the commits
they help write: Claude Code adds a `Co-Authored-By` trailer by default [@anthropic2026claudecode], GitHub's
cloud agent authors commits under its own account [@github2026copilotagent], and Cursor, Jules, Aider and Codex
have their own conventions [@cursor2026docs; @jules2026; @aider2026; @openai2026codex]. Counting these
signatures is not new [@robbes2026; @horikawa2026; @kinlan2026]. What this study adds is
(i) a pre-registered monthly series for a defined population of AI-infrastructure repositories, with matched
controls and the agent harnesses as a third group; (ii) a catalogue in which every signature is backed by three
public example commits; (iii) a direct measurement of how often attribution on a pull request's commits survives
the merge to the default branch; and (iv) a link between the measured share and each repository's stated
AI-contribution policy. The scanner, `coauthored`, is a small open-source command-line tool; it reproduces every
number in this paper from a recorded snapshot and draws the same curve for any organisation's repositories.

Throughout, the unit is the **AI-attributed commit**, and every share is a **lower bound** on AI involvement.
An attributed commit is not a commit "written by AI": the trailer says a tool took part, not how much of the
change it produced. Attribution is also not adoption. It measures which tools sign and which repositories keep
the signature, not who uses AI: the repository of OpenAI's Codex harness had
{{per_repo_2026q3[repo=openai/codex].n_attr}} attributed commit of
{{per_repo_2026q3[repo=openai/codex].n|,}} in 2026-Q3. Section @sec:leaks explains how attribution goes missing.

# Related work

**Measuring AI's share of code.** Daniotti et al. train a classifier to detect AI-written Python functions in
GitHub commits and estimate national shares and productivity effects [@daniotti2026]. Their detector measures
code style; we count declarations. The two quantities have different errors and should not be compared
one-to-one. Horikawa et al. find that once signatures are masked, detectors of agent commits lose much of their
precision at realistic base rates, which suggests that signature-based studies like ours report a lower bound
[@horikawa2026].

**Counting signatures.** Robbes et al. estimate project-level coding-agent adoption across a large GitHub sample
from several signals, among them co-author trailers, agent accounts, configuration files, branch names and
labels [@robbes2026]; their unit is the project, ours the commit. AIDev
collects agent-authored pull requests from five agents [@li2026aidev]. Blog-scale and dashboard counts of
`Co-Authored-By: Claude` commits across public GitHub [@kinlan2026; @semianalysis2026; @amplifying2026] and
GitHub's own telemetry on agent-started pull requests [@github2026octoverse] report fast growth; several
describe their counts as incomplete, and none fixes a population, compares it with controls, or measures loss
at merge. Our
contribution is a narrow, pre-registered and reproducible series rather than a new signal.

**Bots, trailers and merges.** Separating automation from people in commit history has a long history in mining
software repositories [@dey2020]. Our denominator removes maintenance bots (dependency updates, releases) but
keeps AI-agent accounts, which do commit code on someone's behalf. The `Co-authored-by` convention
[@githubdocs2026coauthors] interacts with squash merging: a repository chooses whether the squash message holds
the pull request's title, its description or a list of its commits [@githubdocs2026squash], and GitHub credits
every commit author as a co-author of the squash commit [@github2019squash].

**Policies.** Open-source projects have adopted AI-contribution policies ranging from outright bans
[@gentoo2024; @netbsd2024; @qemu2025] to disclosure requirements [@curl2025; @ghostty2026] and the Linux
kernel's `Assisted-by:` tag [@kerneldocs2026]. Hora and Robbes classify the policies of popular repositories
[@hora2026policy]; we relate a similar classification to measured attribution.

**Productivity and usage.** Experiments find that AI assistance changes the speed and volume of programming
work, in both directions [@peng2023; @cui2026; @becker2025], that it raises open-source contributions
[@yeverechyahu2024], and that agentic tools are used mostly to delegate whole tasks [@anthropic2025eisoftware].
Task-length benchmarks show fast capability growth [@kwa2025]. None of these measures what share of a real
repository's history declares AI involvement.

# What an attribution is, and how it goes missing {#sec:leaks}

A commit is **AI-attributed** if (a) a `Co-authored-by:`, `Assisted-by:` or `Co-developed-by:` line in its
message names an identity in the signature catalogue, (b) its author or committer is an AI-agent account in the
catalogue, or (c) it carries a tool's verbatim marker such as `Generated with Claude Code`. Identities are
matched in full on e-mail address and/or name; no free-text keyword ("AI", "GPT", "Claude") counts. A
`Signed-off-by:` line never counts, because it is a human's certification of origin. The Linux kernel's
`Assisted-by: AGENT:MODEL` format carries no e-mail address and cannot be tied to a catalogue identity; we report
it as a separate indicator ({{bare_assisted_in_window.S1|,}} commits in S1 and
{{bare_assisted_in_window.S2|,}} in S2 over the window, none in S3).

The signal is a lower bound for four reasons.

1. **The trailer is switched off.** Every major tool lets the user disable or change attribution
   [@anthropic2026claudecode; @cursor2026docs; @jules2026; @openai2026codex]. Since February 2026 Jules can
   commit as the user alone [@jules2026], which leaves no trace at all.
2. **The trailer is stripped at merge.** A trailer on a pull request's commits reaches the default branch only if
   the merge keeps it: a merge commit and a rebase keep the original commits, but a squash commit carries
   whatever message the repository's squash setting and the person merging produce [@githubdocs2026squash]. We
   measure this loss in Section @sec:undercount.
3. **The commit is exported from elsewhere.** Some projects are developed in a company's internal repository and
   exported to GitHub by a tool that writes its own commit (in S1, for example, `openxla/xla`, `jax-ml/jax` and
   `tensorflow/tensorflow`). Whatever attribution the internal change had is not visible. Removing the
   repositories with mirror-export trailers raises the S1 share in 2026-Q3 to
   {{sensitivity.mirror_removed[hypothesis=H1].estimate|pct1}}
   ({{sensitivity.mirror_removed[hypothesis=H1].ci[0]|pct1}}–{{sensitivity.mirror_removed[hypothesis=H1].ci[1]|pct1}}).
4. **The tool never attributes.** Autocomplete, chat assistants and copy-paste leave nothing in git, and some
   agents add no signature by default. Some policies also exempt maintainers from disclosure [@ghostty2026].

The tool mix in the data is therefore partly a property of the instrument: tools that sign by default are
over-represented relative to their use. Pre-registered hypothesis H5 tests the instrument as much as the market.

# Pre-registered design

The design, the repository lists, the bot list and the signature catalogue were frozen in a pre-registration
tagged `prereg-v1` (commit `27a6847`) before any study repository was scanned; three pilot repositories, excluded
from every analysis, were used to debug the scanner and discover signatures. Every later clarification is logged
with its effect (`DEVIATIONS.md`).

**Strata.** Inclusion rules were applied to GitHub metadata before scanning. All repositories are public, not
archived and not forks, with at least two thousand stars and at least two hundred default-branch commits in the
twelve months to October 2026; S1 and S3 repositories also had at least a hundred commits in 2024, so that the
series has a pre-agent baseline. <!-- numbers-ok: pre-registered inclusion thresholds -->
**S1** ({{summary.strata.S1}} repositories) contains model-building infrastructure across seven layers: training
frameworks (PyTorch, JAX, Keras), model libraries (Transformers, PEFT, TRL, Diffusers), distributed training
(DeepSpeed, Megatron-LM), fine-tuning and reinforcement learning, inference and serving (vLLM, SGLang,
llama.cpp, Ollama), kernels and compilers (Triton, FlashAttention), and evaluation and data. **S2**
({{summary.strata.S2}}) contains open-source coding-agent harnesses whose primary product is a coding agent
(e.g. OpenHands, Cline, Gemini CLI, Codex, Qwen Code). **S3** ({{summary.strata.S3}}) contains one matched
control per S1 repository, drawn from popular non-AI repositories by a seeded nearest-neighbour match on stars
and recent commit activity within the same language group (caliper ±50%), <!-- numbers-ok: pre-registered caliper -->
then screened so that no control has model training or inference at its core. The lists are in the appendix
(Table @tbl:repos); every exclusion and its reason is in `configs/repos.yaml` and `configs/s3_screen.yaml`.

**Snapshot.** All {{summary.snapshot.repositories}} repositories were cloned on one UTC calendar day,
2026-10-28, with commit objects only, and their full default-branch history was scanned
({{summary.snapshot.commits_all|,}} commits, {{summary.snapshot.seconds|,.0f}} seconds of clone and scan time,
{{summary.snapshot.clone_gb|.2f}} GB). Head SHAs are recorded, and all counting is from those SHAs. Author and
committer identities are replaced by a salted hash at ingest; no names, e-mail addresses or messages are stored.

**Counting.** The primary unit is a non-merge commit reachable from the default branch, dated by its committer
date in UTC, in the window January 2023 to September 2026. Commits authored by maintenance bots are removed from
the denominator; AI-agent accounts stay. Shared history (a fork or a vendored copy) is counted once per stratum,
in the earliest-created repository. The catalogue has {{summary.catalogue.entries}} entries for
{{summary.catalogue.tools}} tools ({{summary.catalogue.kind_coauthor}} co-author identities,
{{summary.catalogue.kind_identity}} agent accounts, {{summary.catalogue.kind_marker}} markers), each with three
public commits as evidence and a passing and a failing test case. On a labelled sample of
{{summary.validation.n}} pilot commits ({{summary.validation.positives}} attributed), the scanner's precision and
recall were {{summary.validation.precision|.2f}} and {{summary.validation.recall|.2f}} (Wilson lower bounds at 95% confidence:
{{summary.validation.precision_lo|pct1}} and {{summary.validation.recall_lo|pct1}}). This validation is weaker
than it looks. The labels were assigned by an AI assistant (a Claude subagent) that saw the catalogue's
definitions but not the scanner, not by an independent human; and the pilot repositories also served to
discover signatures, so the sample checks that the scanner implements the catalogue, not that the catalogue
covers every tool.

**Hypotheses.** All shares are pooled over commits, so large repositories weigh more; repository-weighted shares
(the mean of repository shares) are reported alongside.
Confidence intervals are percentile intervals from {{bootstrap_draws|,}} cluster-bootstrap resamples of
repositories within stratum (seed {{seed}}).

- **H1 (level):** the pooled S1 share in 2026-Q3 is at least 5%. <!-- numbers-ok: pre-registered threshold -->
- **H2 (difference):** S1 exceeds S3 in every month from April to September 2026, and the 2026-Q3 odds ratio is at least two with a CI above one. <!-- numbers-ok: pre-registered threshold -->
- **H3 (growth):** the monthly logit slope of a binomial model is positive in S1 and in S2, and steeper in S1 than in S3 (CIs exclude zero).
- **H4 (recursion):** the 2026-Q3 share in S2 exceeds that in S1 (CI of the difference excludes zero).
- **H5 (tools):** Claude Code has the plurality of attributed commits in S1 ∪ S2 in every quarter from 2025-Q2 to 2026-Q3.
- **H6 (survival):** at least 80% of sampled merged pull requests with an attributed head commit keep the attribution on the default branch. <!-- numbers-ok: pre-registered threshold -->
- **H7 (policy, exploratory):** repositories that require disclosure have a higher share than those that ban AI or are silent.

Holm's correction is applied across H1–H6 for a family-wise claim; each hypothesis is also decided on its own
rule, as pre-registered. Analyses not in the pre-registration are labelled *post hoc* (`DEVIATIONS.md`). Pre-registered sensitivity analyses use author dates, include merges, keep only first-parent commits,
require trailers in the final trailer block, include maintenance bots, remove the three largest repositories of
each stratum, remove mirror-exported repositories, remove outside-caliper matches, and replace the model in H3
with a mixed model with a random intercept and slope per repository.

# Results

## The curve (RQ1–RQ3)

Figure @fig:f1 shows the monthly attributed share. Before 2025 it is close to zero everywhere: in 2024,
{{summary.year[stratum=S1,year=2024].n_attr|,}} of {{summary.year[stratum=S1,year=2024].n|,}} S1 commits were
attributed, {{summary.year[stratum=S2,year=2024].n_attr|,}} of {{summary.year[stratum=S2,year=2024].n|,}} in S2
and {{summary.year[stratum=S3,year=2024].n_attr|,}} of {{summary.year[stratum=S3,year=2024].n|,}} in S3. The harnesses move first, from late 2024, driven by
one project whose agent commits under its own account. S1 and S3 start rising together in mid-2025 and stay
close afterwards: over the 2025 calendar year the pooled share was
{{summary.year[stratum=S1,year=2025].share|pct2}} in S1 and {{summary.year[stratum=S3,year=2025].share|pct2}}
in S3, and over January–September 2026 {{summary.year[stratum=S1,year=2026].share|pct1}} and
{{summary.year[stratum=S3,year=2026].share|pct1}}.

![Monthly AI-attributed share of commits by stratum, January 2023 – September 2026, pooled over repositories,
with 95% cluster-bootstrap bands. AI-attributed commits are a lower bound on AI
involvement.](results/figures/f1_monthly_share.svg){#fig:f1 width=100%}

In 2026-Q3 the pooled share was {{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}} in S1
({{summary.quarterly[stratum=S1,q=2026-Q3].n_attr|,}} of {{summary.quarterly[stratum=S1,q=2026-Q3].n|,}}
commits; 95% CI {{summary.quarterly[stratum=S1,q=2026-Q3].lo|pct1}}–{{summary.quarterly[stratum=S1,q=2026-Q3].hi|pct1}};
repository-weighted {{robustness.repo_weighted_q3.S1|pct1}}),
{{summary.quarterly[stratum=S2,q=2026-Q3].share|pct1}} in S2
({{summary.quarterly[stratum=S2,q=2026-Q3].lo|pct1}}–{{summary.quarterly[stratum=S2,q=2026-Q3].hi|pct1}};
repository-weighted {{robustness.repo_weighted_q3.S2|pct1}}) and
{{summary.quarterly[stratum=S3,q=2026-Q3].share|pct1}} in S3
({{summary.quarterly[stratum=S3,q=2026-Q3].lo|pct1}}–{{summary.quarterly[stratum=S3,q=2026-Q3].hi|pct1}};
repository-weighted {{robustness.repo_weighted_q3.S3|pct1}}). The
wide intervals reflect how unevenly attribution is spread across repositories (Figure @fig:f4):
{{summary.repos[stratum=S1].with_attributed_q3}} of the {{summary.repos[stratum=S1].active_q3}} S1 repositories
active in the quarter had at least one attributed commit, {{summary.repos[stratum=S1].share_ge_10pct_q3}} had a
share of ten percent or more, and the median repository share was {{summary.repos[stratum=S1].median_share_q3|pct1}}.
In S3, {{summary.repos[stratum=S3].with_attributed_q3}} of {{summary.repos[stratum=S3].active_q3}} had any
attributed commit, and the two largest contributors account for
{{summary.repos[stratum=S3].top2_attr_fraction_q3|pct}} of the stratum's attributed commits; the largest,
`{{robustness.s3_top_repo.repo}}`, alone for {{robustness.s3_top_repo.fraction_of_attributed|pct}}. Without it
the S3 share is {{robustness.s3_top_repo.s3_share_without|pct1}} (post hoc). Figure @fig:f3 in the appendix shows
every repository month by month.

Table @tbl:hyp gives the decisions. **H1 is {{hypotheses[hypothesis=H1].supported|verdict}}** on its pre-registered rule, which looks at the point
estimate: the S1 share in 2026-Q3 is above the 5% floor, but its interval reaches below it, and the one-sided <!-- numbers-ok: threshold -->
p-value against the threshold is {{hypotheses[hypothesis=H1].p_one_sided|.2f}} ({{hypotheses[hypothesis=H1].p_holm|.2f}}
after Holm's correction). Of H1–H6, only H6 survives the family-wise correction. **H2 is {{hypotheses[hypothesis=H2].supported|verdict}}**: S1 was below S3 in {{robustness.s1_below_s3_h2_window}} of the six pre-registered months (April–September 2026), and the 2026-Q3 odds ratio is
{{hypotheses[hypothesis=H2].estimate|.2f}} (95% CI {{hypotheses[hypothesis=H2].ci[0]|.2f}}–{{hypotheses[hypothesis=H2].ci[1]|.2f}}).
The interval runs from S1 having about half the odds of S3 to almost five times them, so the data neither
support the pre-registered doubling nor exclude it.
**H3 is {{hypotheses[hypothesis=H3].supported|verdict}}**: the monthly logit slope is clearly positive in S1
({{hypotheses[hypothesis=H3].detail.slopes.S1|.3f}}) but just as steep in S3
({{hypotheses[hypothesis=H3].detail.slopes.S3|.3f}}); the S2 slope
({{hypotheses[hypothesis=H3].detail.slopes.S2|.3f}}; CI {{hypotheses[hypothesis=H3].detail.slope_ci.S2[0]|.3f}} to
{{hypotheses[hypothesis=H3].detail.slope_ci.S2[1]|.3f}}) includes zero, because the harnesses were
already attributing in 2025. **H4 is {{hypotheses[hypothesis=H4].supported|verdict}}**: S2 is
{{hypotheses[hypothesis=H4].estimate|pp1}} percentage points above S1 in 2026-Q3, with a CI from
{{hypotheses[hypothesis=H4].ci[0]|pp1}} to {{hypotheses[hypothesis=H4].ci[1]|pp1}} points. Among the harnesses,
attribution says more about the tool than about its use: OpenHands' own agent signs most of that repository's
commits, while the Codex repository carries almost none.

: Pre-registered hypotheses. Estimates and 95% CIs from the cluster bootstrap (H6: Wilson interval). p: one-sided p-values against each hypothesis's null: share at or below the threshold (H1), odds ratio at most one (H2), difference at most zero (H3–H5), from the bootstrap; survival share at or below the threshold (H6), exact binomial test. Holm-adjusted across H1–H6. H7 is exploratory. {#tbl:hyp}

| | Estimate | 95% CI | p | p (Holm) | Decision |
|----------------------------------|---------:|-----------------:|-------:|---------:|------------------|
| H1 S1 share, 2026-Q3 | {{hypotheses[hypothesis=H1].estimate\|pct1}} | {{hypotheses[hypothesis=H1].ci[0]\|pct1}}–{{hypotheses[hypothesis=H1].ci[1]\|pct1}} | {{hypotheses[hypothesis=H1].p_one_sided\|p}} | {{hypotheses[hypothesis=H1].p_holm\|p}} | {{hypotheses[hypothesis=H1].supported\|verdict}} |
| H2 odds ratio S1 : S3 | {{hypotheses[hypothesis=H2].estimate\|.2f}} | {{hypotheses[hypothesis=H2].ci[0]\|.2f}}–{{hypotheses[hypothesis=H2].ci[1]\|.2f}} | {{hypotheses[hypothesis=H2].p_one_sided\|p}} | {{hypotheses[hypothesis=H2].p_holm\|p}} | {{hypotheses[hypothesis=H2].supported\|verdict}} |
| H3 slope S1 − S3 (logit/month) | {{hypotheses[hypothesis=H3].estimate\|.3f}} | {{hypotheses[hypothesis=H3].ci[0]\|.3f}} to {{hypotheses[hypothesis=H3].ci[1]\|.3f}} | {{hypotheses[hypothesis=H3].p_one_sided\|p}} | {{hypotheses[hypothesis=H3].p_holm\|p}} | {{hypotheses[hypothesis=H3].supported\|verdict}} |
| H4 share S2 − S1 (points) | {{hypotheses[hypothesis=H4].estimate\|pp1}} | {{hypotheses[hypothesis=H4].ci[0]\|pp1}} to {{hypotheses[hypothesis=H4].ci[1]\|pp1}} | {{hypotheses[hypothesis=H4].p_one_sided\|p}} | {{hypotheses[hypothesis=H4].p_holm\|p}} | {{hypotheses[hypothesis=H4].supported\|verdict}} |
| H5 Claude Code lead, min. (points) | {{hypotheses[hypothesis=H5].estimate\|pp1}} | {{hypotheses[hypothesis=H5].ci[0]\|pp1}} to {{hypotheses[hypothesis=H5].ci[1]\|pp1}} | {{hypotheses[hypothesis=H5].p_one_sided\|p}} | {{hypotheses[hypothesis=H5].p_holm\|p}} | {{hypotheses[hypothesis=H5].supported\|verdict}} |
| H6 attribution survives merge | {{hypotheses[hypothesis=H6].estimate\|pct1}} | {{hypotheses[hypothesis=H6].ci[0]\|pct1}}–{{hypotheses[hypothesis=H6].ci[1]\|pct1}} | {{hypotheses[hypothesis=H6].p_one_sided\|p}} | {{hypotheses[hypothesis=H6].p_holm\|p}} | {{hypotheses[hypothesis=H6].supported\|verdict}} |
| H7 disclosure − (ban ∪ silent) (points) | {{hypotheses[hypothesis=H7].estimate\|pp1}} | – | – | – | exploratory |

The decisions are the same under every pre-registered sensitivity analysis (Appendix, Table @tbl:sens): H1 holds
and H2–H4 fail under author dates, with merges, on the first-parent chain, with strict trailer positions, with
maintenance bots, without the three largest repositories of each stratum, without mirror-exported repositories
and without the outside-caliper matches. The estimates, however, move a good deal, which is itself a measure of
how fragile they are: the S1 share ranges from
{{sensitivity.strict_trailers[hypothesis=H1].estimate|pct1}} with strict trailer positions to
{{sensitivity.mirror_removed[hypothesis=H1].estimate|pct1}} without mirror exports, and the H2 odds ratio from
{{sensitivity.strict_trailers[hypothesis=H2].estimate|.2f}} to
{{sensitivity.largest_3_removed[hypothesis=H2].estimate|.2f}} without the three largest repositories of each
stratum. The mixed model with a random intercept and slope per repository gives the same decision for H3 but a
different picture: the S1 − S3 slope difference changes sign, to {{sensitivity.glmm[0].estimate|.3f}} logit per
month (Wald CI {{sensitivity.glmm[0].ci[0]|.3f}} to {{sensitivity.glmm[0].ci[1]|.3f}}), and the S2 slope,
{{sensitivity.glmm[0].detail.slopes.S2|.3f}} ({{sensitivity.glmm[0].detail.ci.S2[0]|.3f}} to
{{sensitivity.glmm[0].detail.ci.S2[1]|.3f}}), has an interval that excludes zero once each repository has its
own trend.

## Which tools (RQ4)

The tool mix changed quickly (Figure @fig:f2). In S1 ∪ S2, OpenHands had the plurality of attributed commits
through 2025-Q3 (a majority until 2025-Q2), almost all of them in its own repository. Gemini Code Assist led in
2025-Q4 ({{summary.tool_leaders[q=2025-Q4].share|pct}}); it is a code-review bot, and its trailer marks a
reviewer's suggested change that a contributor applied, as does Copilot's for applied review suggestions.
Dropping those two signatures (post hoc) changes the S1 share in 2026-Q3 to
{{sensitivity.no_review_suggestions[hypothesis=H1].estimate|pct1}}. Claude Code has led since
2026-Q1, with {{summary.tool_leaders[q=2026-Q1].claude_code|pct}},
{{summary.tool_leaders[q=2026-Q2].claude_code|pct}} and {{summary.tool_leaders[q=2026-Q3].claude_code|pct}} of
attributed commits in the three quarters of 2026. **H5 is {{hypotheses[hypothesis=H5].supported|verdict}}** because the plurality did not hold in
2025; the minimum margin of Claude Code over the next tool is
{{hypotheses[hypothesis=H5].estimate|pp1}} percentage points. Because Claude Code signs by default and many tools do not,
its share of *attributed* commits probably overstates its share of AI-assisted commits, by an unknown factor.

![Attributed commits by tool, as a share of all commits in each stratum, by quarter, 2025-Q1 to 2026-Q3. The nine
tools with the most attributed commits over 2025–2026 are shown; all others are grouped as Other. AI-attributed
commits are a lower bound.](results/figures/f2_tools.svg){#fig:f2 width=100%}

# How much does the signal miss? (RQ5) {#sec:undercount}

**Survival through the merge.** The estimand is the share of merged pull requests with at least one attributed
commit whose commit on the default branch still carries an attribution, among pull requests merged June 2025 to
September 2026 in S1 and S2, each sampled pull request counting once. We sampled them uniformly at random within
repository, visiting repositories in turn, and compared the attribution on each pull request's commits with the
attribution on what landed. Of {{hypotheses[hypothesis=H6].detail.inspected|,}} pull requests inspected,
{{hypotheses[hypothesis=H6].detail.n|,}} had at least one attributed commit, and in
{{hypotheses[hypothesis=H6].detail.k|,}} of them an attribution reached the default branch
({{hypotheses[hypothesis=H6].estimate|pct1}}, 95% CI {{hypotheses[hypothesis=H6].ci[0]|pct1}}–{{hypotheses[hypothesis=H6].ci[1]|pct1}};
H6 {{hypotheses[hypothesis=H6].supported|verdict}}). Figure @fig:f5 splits the result by merge method. Only squash
merges are an observed test: a merge commit keeps the pull request's commits by construction, and a rebase is
scored as kept unless its rewritten last commit lost an attribution that the original had (`DEVIATIONS.md`).
Almost all sampled pull requests were squash-merged, and
{{hypotheses[hypothesis=H6].detail.by_method.squash[0]}} of {{hypotheses[hypothesis=H6].detail.by_method.squash[1]}}
squash merges kept an attribution, which also clears the pre-registered threshold. The {{hypotheses[hypothesis=H6].detail.n}}
pull requests come from {{hypotheses[hypothesis=H6].detail.repos}} repositories, a few of which contribute many;
resampling repositories instead of pull requests gives an interval of
{{hypotheses[hypothesis=H6].detail.ci_cluster_repo[0]|pct1}}–{{hypotheses[hypothesis=H6].detail.ci_cluster_repo[1]|pct1}}
(post hoc), and the losses are spread over {{hypotheses[hypothesis=H6].detail.repos_with_loss}} repositories
rather than concentrated in one. By tool named on the commits, pull requests with Claude Code kept an
attribution in {{hypotheses[hypothesis=H6].detail.by_tool.Claude Code[0]}} of
{{hypotheses[hypothesis=H6].detail.by_tool.Claude Code[1]}}, with GitHub Copilot in
{{hypotheses[hypothesis=H6].detail.by_tool.GitHub Copilot[0]}} of
{{hypotheses[hypothesis=H6].detail.by_tool.GitHub Copilot[1]}} and with Warp in
{{hypotheses[hypothesis=H6].detail.by_tool.Warp[0]}} of {{hypotheses[hypothesis=H6].detail.by_tool.Warp[1]}}.

We cannot say from the landed commit *why* attribution survives a squash. GitHub's documented default message
for a multi-commit pull request is its title and a list of its commits [@githubdocs2026squash], which may carry
the commits' trailers, and GitHub also credits every commit author as a co-author of the squash commit
[@github2019squash], which keeps an agent account's attribution even when the message is rewritten. A loss can
come from a repository's squash setting or from a person editing the message at merge. Pull requests with more
than a hundred commits were read only up to their hundredth commit. In the sampled repositories, then, little
attribution is lost at the merge; the other paths, trailers switched off, exports from internal repositories and
tools that never attribute, are not measured here, and the size of the undercount remains unknown.

![Share of sampled merged pull requests with an attributed commit whose attribution reached the default branch,
by merge method, with Wilson 95% intervals.](results/figures/f5_survival.svg){#fig:f5 width=60%}

**Policies.** Of the {{summary.snapshot.repositories}} repositories, {{summary.policy.bans}} bans AI
contributions in its contribution guidelines, {{summary.policy.requires_disclosure}} require disclosure,
{{summary.policy.mentions}} mention AI without a rule, and {{summary.policy.silent}} are silent;
{{summary.policy.agent_config}} carry a configuration file addressed to coding agents (`AGENTS.md`, `CLAUDE.md` or
Copilot instructions). In 2026-Q3 the pooled share was {{hypotheses[hypothesis=H7].detail.by_policy.requires_disclosure|pct1}}
in repositories that require disclosure, {{hypotheses[hypothesis=H7].detail.by_policy.mentions|pct1}} where AI
is mentioned without a rule and {{hypotheses[hypothesis=H7].detail.by_policy.silent|pct1}} where policies are
silent (Figure @fig:f6). The exploratory H7 difference is positive
({{hypotheses[hypothesis=H7].estimate|pp1}} percentage points), but it is not the largest contrast: repositories
that mention AI without a rule have a higher share than those that require disclosure. Without an
interval, and with everything else that distinguishes these repositories, we read nothing causal into it. The policy classes were checked against the guideline text by an AI assistant after the
attributed shares had been computed, so the check was not blind.

![AI-attributed share of commits in 2026-Q3 by the repository's AI-contribution policy (one dot per repository;
bars: pooled share of the class). Policies were read at the snapshot from the contribution guidelines,
classified by rule and checked by an AI assistant after the shares were known. AI-attributed commits are a lower
bound.](results/figures/f6_policy.svg){#fig:f6 width=75%}

**Tools that never attribute** cannot be measured from git metadata. Classifier-based estimates
[@daniotti2026; @horikawa2026] suggest that unattributed AI involvement is large, but they measure a different
quantity, and we make no estimate of it.

# Exploratory analyses (RQ6)

**Size.** In a stratified random sample of 2,000 window commits <!-- numbers-ok: pre-registered sample size --> the
median attributed commit changed {{size[period=all,stratum=S1].median_attr|.0f}} lines in S1 against
{{size[period=all,stratum=S1].median_unattr|.0f}} for unattributed commits; the ratios were similar in S2 and
S3 (Appendix, Table @tbl:size). Part of this is composition: attributed commits cluster in repositories whose
commits are large; part is time, because attributed commits are recent and commit sizes change over the years.
Restricted to 2026, the S1 ratio of medians is {{size[period=2026,stratum=S1].ratio|.2f}}
({{size[period=2026,stratum=S1].ratio_ci[0]|.2f}}–{{size[period=2026,stratum=S1].ratio_ci[1]|.2f}}). Within
repositories and calendar years (fixed effects for both, post hoc), attributed commits were larger by a factor of
{{size_within_repo[stratum=S1].ratio|.2f}} in geometric mean in S1, with an interval that includes one
({{size_within_repo[stratum=S1].ratio_ci[0]|.2f}}–{{size_within_repo[stratum=S1].ratio_ci[1]|.2f}}), and by
{{size_within_repo[stratum=S2].ratio|.2f}} in S2 and {{size_within_repo[stratum=S3].ratio|.2f}} in S3. In S1,
then, the size difference may be mostly composition and time.

**Reverts.** The crude revert rate of attributed commits is lower than that of other commits in every stratum,
but this too is composition and exposure: attributed commits are recent, so they have had less time to be
reverted, and they cluster in some repositories. Compared with unattributed commits of the same repository and
month (commits to June 2026; post hoc), attributed commits were reverted {{reverts_standardised[stratum=S1].ratio|.2f}}
times as often as expected in S1 (95% CI {{reverts_standardised[stratum=S1].ratio_ci[0]|.2f}}–{{reverts_standardised[stratum=S1].ratio_ci[1]|.2f}};
{{reverts_standardised[stratum=S1].observed}} observed, {{reverts_standardised[stratum=S1].expected|.1f}}
expected). Only reverts made with git's standard message are detected, and the counts are small, so these data
cannot say whether attributed commits are reverted more or less often.

**Breadth and intensity.** Repositories differ in whether attribution is concentrated in a few contributors or
spread across many (Figure @fig:f8). Repositories above the dashed line have a higher share of attributed
commits than of attributing authors, so a few contributors account for most attributed commits; repositories
below it have attribution spread thinly over many authors. The line is a visual reference, not a benchmark: the
two shares have different denominators.

![Per repository, 2026-Q3: intensity (share of commits attributed) against breadth (mean monthly share of active
authors with at least one attributed commit). Dashed line: equal shares. AI-attributed commits are a lower
bound.](results/figures/f8_breadth.svg){#fig:f8 width=70%}

# Discussion

**What the curve says about "AI building AI".** We had expected AI-infrastructure projects, staffed by people
who build models, to attribute earlier and more; in this population the data do not show that. The harnesses,
built by the vendors and communities of the tools themselves, attributed earliest, and by 2026 the other two
groups had reached similar levels. The comparison is weak in both directions, though: twelve to forty-two
repositories per group, one control repository with a large share of its group's attributions, and
AI-infrastructure repositories exported from internal monorepos make the intervals wide, and the data are
consistent with a moderate lead for either group. A plausible reading, which this design cannot test, is that
attribution in mid-2026 depends less on what a project is about than on which tools its contributors use and
whether those tools sign by default. <!-- numbers-ok: stratum sizes -->

**Attribution as a provenance artefact.** A co-author trailer is a cheap, machine-readable record of which tool
took part in a change, much as a software bill of materials records which components a build includes. In the
sampled repositories the record mostly survives the merge. Projects that want to know how their code was produced
could keep tool attribution switched on and choose a squash message that keeps commit trailers; whether to ask
contributors for that is a governance choice this study does not settle. Neither practice tells anyone how much
of a change a tool wrote, and neither should be read as a quality signal.

**What the curve does not say.** It does not say that one commit in
{{summary.quarterly[stratum=S1,q=2026-Q3].share|inv}} to AI infrastructure was written by AI. An attributed commit
may be mostly human work with a small tool contribution, and many AI-assisted commits are not attributed. The
curve also does not measure quality, safety or productivity. And it says nothing about model collapse or
similar concerns about recursive training [@shumailov2024]; those would require knowing what the attributed code
does.

# Limitations

**Lower bound.** Attribution undercounts AI involvement by an unknown and probably changing factor; tool
defaults, user settings, merge settings and exports from internal repositories all move it. **Attribution is not
adoption, nor authorship share.** We count signed commits, not use, lines or effort. **Selection.** S1 is a
purposive list of prominent projects; S3 is matched on popularity and activity, not on contributor population,
and its two largest contributors carry much of its attributed volume. The results describe these repositories,
not open source at large. **Validation.** The labelled sample was drawn from the pilot repositories and labelled
by an AI assistant, not an independent human; with no errors in it, the Wilson lower bounds of precision and recall
still allow error rates of a few percent. **Small numbers.** Twelve harnesses and forty-two repositories per comparison group give
wide intervals, and the pre-registered comparisons have little power against moderate differences. <!-- numbers-ok: stratum sizes --> **One snapshot.** Histories were read once, on 2026-10-28; force-pushes and later rewrites are
not reflected. **Tool mix.** Default-on signatures dominate the counts, so tool shares describe the instrument as
much as the market. **Survival sample frame.** Repositories that land pull requests with a merge bot and close
them, rather than merging, contribute few sampled pull requests, and pull requests opened long before the window
are outside the frame (`DEVIATIONS.md`). **Policies** were read from the pre-registered files only, and a few
repositories state policies elsewhere; the classification was checked by an AI assistant, not blind to the
shares. **Survivorship.** Only repositories that are popular and active in 2026
are included; projects that declined or were archived are not.

# Ethics

The study uses public git metadata and the public GitHub API within its terms. Identities are hashed at ingest
with a secret salt; no names, e-mail addresses or commit messages are stored or published, the paper and the
dataset report repository-level aggregates only, and no individual developer is named. Repositories are named,
because they are public projects and the comparison is between projects; a few live under a personal account,
and for those we report nothing beyond what we report for every repository. As pre-registered, only aggregates
are released: no per-commit records, and the survival and size samples carry neither pull request numbers nor
commit SHAs. The scanner's report command is meant for one's own organisation (`RESPONSIBLE_USE.md`). This is independent personal research using public data only, and it does
not represent the views of any employer or institution.

# Reproducibility

The pre-registration is tagged `prereg-v1` (commit `27a6847`); `DEVIATIONS.md` lists every later clarification.
`data/manifest.json` records the head SHA, default branch, commit count and git version of every repository at
the snapshot. `coauthored analyze` rebuilds every table, figure and number in this paper from the committed
aggregates, with no network and byte-identical output, and `coauthored paper` fills this text from the
resulting `results/numbers.json`; the build fails if a number is typed by hand. `coauthored scan` re-derives the
aggregates from the recorded SHAs. The code is released under Apache-2.0 and the data under CC BY 4.0.

# References {-}

::: {#refs}
:::

# Appendix {-}

## Repositories {-}

: Study repositories by stratum and S1 layer, at the 2026-10-28 snapshot. S3 controls are grouped by the layer of the S1 repository each was matched to; the pairs are in `data/s3_match.json`. Exclusions and their reasons: `configs/repos.yaml`, `configs/s3_screen.yaml`. {#tbl:repos}

<!-- include: paper/repositories.md -->

## Sensitivity analyses {-}

: Estimates under each sensitivity analysis (✓ supported, ✗ not supported); rows marked post hoc were not pre-registered. H1: S1 share, 2026-Q3; H2: odds ratio S1 : S3; H3: slope difference S1 − S3; H4: share difference S2 − S1. The GLMM row replaces the model in H3. {#tbl:sens}

<!-- include: results/tables/sensitivity.md -->

## Commit size {-}

: Lines changed (insertions plus deletions) in the size sample: median [interquartile range] for attributed and unattributed commits, and the ratio of medians with a bootstrap 95% CI. Rows labelled 2026 restrict both groups to January–September 2026. {#tbl:size}

<!-- include: results/tables/size.md -->

## Per-repository shares {-}

![AI-attributed share of commits per repository, 2026-Q3, with Wilson 95% intervals. One S1 repository had no commits
in the quarter. AI-attributed commits are a lower bound.](results/figures/f4_per_repo.svg){#fig:f4 width=100%}

![AI-attributed share per repository and month, 2025-01 to 2026-09; repository-months with fewer than ten commits
in grey. AI-attributed commits are a lower bound.](results/figures/f3_heatmap.svg){#fig:f3 width=100%}
