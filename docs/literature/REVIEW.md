# Literature review

For: *Who Writes the Code That Trains the Models? AI Co-Authorship Trailers in AI Infrastructure Repositories, 2023–2026*.

Compiled 2026-10-28. There are 35 sources, and each one was checked by web search or fetch on that date. For papers, title, authors, year, venue and DOI were also checked against arXiv and Crossref. Every number quoted below comes from the source it is attributed to, and from the version stated. BibTeX is in `paper/refs.bib` and uses the keys given in brackets.

Each entry ends with how it relates to this paper:
- **Precedent**: prior work that measures the same or nearly the same thing.
- **Contrast**: a different measurement approach to the same question.
- **Method**: a source for a design or measurement choice.
- **Context**: background for the introduction or discussion.

---

## 1. Measuring AI's share of code on GitHub at scale

**Daniotti, Wachs, Feng & Neffke (2026), *Science* 391:831–835 — "Who is using AI to code? Global diffusion and impact of generative AI"** [`daniotti2026`]
The authors train a neural classifier to detect AI-generated Python functions in over 30 million GitHub commits (arXiv v2 abstract). They estimate that AI writes about 29% of Python functions in the US, that AI use raised quarterly online code output by 3.6%, and that experienced programmers capture most of the gains. *Relation: contrast and closest precedent.* It estimates AI-written code with a detector run on the code. This paper instead counts explicit attribution in commit metadata, and studies a narrower population: AI-infrastructure and harness repositories with matched controls. The two quantities measure different things and should not be compared one-to-one.

**Robbes, Matricon, Degueule, Hora & Zacchiroli (2026), *ACM TOSEM* — "Agentic Much? Adoption of Coding Agents on GitHub"** [`robbes2026`]
This is the first large-scale study of coding-agent adoption built from the traces agents leave in git and on GitHub. Those traces are co-author and author trailers (e.g. `Co-Authored-By: Claude <noreply@anthropic.com>`), agent configuration files (e.g. `.cursorrules`), branch names (e.g. `copilot/…`) and PR labels. The sample is 128,018 projects (≥10 stars, drawn with the Dabic et al. sampling tool). As of 21 February 2026, 12.08% of projects showed file-level traces and a further 11.51% showed commit-level traces, for an estimated adoption of 22.20%, and up to 28.66% at the high end. The authors map PR labels onto main-branch commits after rebase and squash merges, and note that a squash merge forces them to label the whole squashed commit as AI-assisted. *Relation: precedent, the most direct one.* It already counts co-author trailers at scale. This paper narrows to AI-infrastructure repos, reports a monthly commit-share series rather than project-level adoption, adds matched controls, and measures how often trailers survive squash merges.

**Horikawa, Li, Kashiwa, Ouatiti, Sayagh, Adams, Iida & Hassan (2026), arXiv:2610.36229 — "Agent or Human? Detecting Commits by AI Coding Agents in the Absence of Authorship Signatures"** [`horikawa2026`]
The dataset is 7,837,946 commits from 1,226 repositories. Copilot, Cursor, Devin and Jules commits are labelled by their author accounts (`Copilot`, `cursoragent`, `devin-ai-integration[bot]`, `google-labs-jules[bot]`), and Claude Code commits by a case-insensitive `Co-Authored-By: Claude` signature. OpenAI Codex is excluded because these rules do not identify its commits. After the signatures are masked, the best detector reaches ROC AUC 0.859 but only 0.332 precision at the observed agent share. Copilot AUC fell from 0.83 to 0.61 during a period when fewer of its commits carried its squash-merge template. The authors conclude that studies based on signatures report "a lower bound on agent activity". *Relation: precedent (signature catalogue) and method (justifies the lower-bound framing; squash templates and signatures at PR rather than commit level are measurement hazards).*

**Li, Zhang & Hassan (2026), MSR 2026 — "AIDev: Studying AI Coding Agents on GitHub"** [`li2026aidev`]
AIDev is a dataset of 932,791 agent-authored pull requests from five agents (OpenAI Codex, Devin, GitHub Copilot, Cursor, Claude Code) across 116,211 repositories and 72,189 developers. It includes a curated subset of 33,596 PRs from 2,807 repositories with more than 100 stars. *Relation: precedent (PR-level, agent-identified population) and method (a check on our signature list).* The unit here is PRs, whereas this paper's unit is commits on the default branch.

**GitHub (2024) — "Octoverse: AI leads Python to top language as the number of global developers surges"** [`github2024octoverse`]
GitHub reported more than 70,000 new public generative-AI projects in 2024, a 98% increase in such projects, and a 59% increase in contributions to generative-AI projects. Python became the most used language on GitHub. *Relation: context.* The AI-infrastructure ecosystem this paper samples was growing fast before agentic tools arrived.

**GitHub (2025) — "Octoverse: A new developer joins GitHub every second as AI leads TypeScript to #1"** [`github2025octoverse`]
GitHub reported "1+ million pull requests" created by Copilot coding agent between May and September 2025, more than 4.3 million AI-related repositories, 1.1 million public repositories using an LLM SDK, and nearly 1 billion commits pushed in 2025 (+25.1% year on year). *Relation: context.* It gives platform-level figures for the agent era, from GitHub's internal data.

**GitHub (2026) — "Octoverse: Commits, pushes, reach new highs in 2026 as developers build with agents"** (published 2026-10-28) [`github2026octoverse`]
GitHub reports that developers start "more than 40% of pull requests with an agent" as of September 2026, up from 17% in March, and that agents started 110 million PRs in September 2026. Its glossary defines an agent signal as a floor, "since not all agent use may be detected". The report does not say how agents are detected, and it gives no figures for co-authored or AI-authored commits. *Relation: context and contrast.* It is a telemetry-based share of PRs from inside the platform. This paper's share is commit-level, built from public metadata, and reproducible from outside GitHub.

## 2. Informal and dashboard counts of AI-attributed commits

**Kinlan (2026), blog post — "damn claude, that's a lot of commits"** [`kinlan2026`]
Kinlan wrote scripts against GitHub's search API. They count commits carrying a Co-Authored-By trailer for Claude, Cursor, Copilot, Codex and others, count the Copilot agent, Jules and Devin by their bot author accounts, and find Claude Code PRs by the "Generated with Claude Code" marker. Claude Code went from about 180,000 of 27.7 million public commits (≈0.7%) in the week of 29 September 2025 to 2.6 million of 57.8 million (≈4.5%) in the week of 16 March 2026. The post itself warns that "The GitHub search API is unreliable at this scale" and that the data "overrepresents tools that tag their output". *Relation: precedent.* This is the blog-scale trailer count that the paper formalises, with a fixed repository population, full-history scans instead of search-API estimates, controls, and pre-registration.

**O'Laughlin, Eliahou Ontiveros, Nanos et al. (SemiAnalysis, 2026) — "Claude Code is the Inflection Point"** [`semianalysis2026`]
The post states that "4% of GitHub public commits are being authored by Claude Code right now" (5 February 2026), and projects 20%+ of daily commits by the end of 2026. The method is behind a paywall. The only visible attribution is a chart credit to "Tokenomics Team, Github". *Relation: precedent (a widely cited headline share) and contrast (method not disclosed).*

**Amplifying (2026), "Coding Agents Index" — Claude Code profile** [`amplifying2026`]
This is a public dashboard that counts commits and PRs "provably produced by" each agent, using attribution "declared in metadata". For the week ending 2026-10-25 it reports 11.5M signed Claude Code commits, as a search estimate. The page says squash merges and private repositories "sit outside" the count, so the number is a floor, and that estimates "can swing 30 to 40 percent between measurement runs". *Relation: precedent (a live trailer-count dashboard).* It also names squash merges as an unmeasured source of undercount, which this paper measures directly.

## 3. Mining-software-repositories method: bots, trailers and merges

**Dey, Mousavi, Ponce, Fry, Vasilescu, Filippova & Mockus (2020), MSR 2020 — "Detecting and Characterizing Bots that Commit Code"** [`dey2020`]
The BIMAN method identifies bot committers from author names, commit messages, the files changed and the projects involved, with AUC-ROC 0.9. It produced a dataset of 461 bots with more than 1,000 commits each (13,762,430 commits in total). *Relation: method.* It is precedent for separating automated authors from humans in commit history. This paper's bot list has to separate dependency and CI bots (non-AI) from AI-agent bot accounts.

**GitHub Docs — "Creating a commit with multiple authors"** [`githubdocs2026coauthors`]
The page defines the convention: one `Co-authored-by: name <name@example.com>` line per co-author, placed after a blank line at the end of the message. A co-author is credited only if the email is associated with their GitHub account. *Relation: method.* It is the formal definition of the trailer this paper matches.

**GitHub Docs — "Configuring commit squashing for pull requests"** [`githubdocs2026squash`]
By default a squash commit message uses the commit title and message when the PR has one commit, and the PR title plus a list of commits when it has two or more. Maintainers can instead choose "just the pull request title, the pull request title and commit details, or the pull request title and description". *Relation: method.* The setting decides whether a trailer from an individual commit can reach the default branch. It is the mechanism behind the survival analysis.

**GitHub Changelog (2019-12-19) — "Improved attribution when squashing commits"** [`github2019squash`]
"Now, we will automatically credit every commit author in the pull request as a co-author on the squash commit." Before this change, the person who opened the PR was the sole author of the squash commit. *Relation: method.* GitHub may add Co-authored-by trailers itself at squash time, for commit authors. This is a separate path from trailers written by the tool, and the matcher must handle it. A bot-authored commit inside a squashed PR can come back as a co-author trailer.

## 4. Vendor documentation of attribution behaviour

**Anthropic — Claude Code settings reference (`attribution`, `includeCoAuthoredBy`)** [`anthropic2026claudecode`]
By default, Claude Code adds `Co-Authored-By: <name> <noreply@anthropic.com>` to commits. The name is the active model (e.g. `Claude Sonnet 5`), or `Claude` or `Claude Code` when the version cannot be determined. PR descriptions get a robot emoji followed by `Generated with [Claude Code](https://claude.com/claude-code)`. Both can be changed or removed through the `attribution` object, and the older `includeCoAuthoredBy` Boolean is deprecated. *Relation: method.* It is the source of the Claude signature, and evidence that the signature is on by default but can be switched off, so absence does not mean non-use.

**GitHub Docs — "Risks and mitigations for GitHub Copilot cloud agent"** [`github2026copilotagent`]
"Copilot cloud agent's commits are authored by Copilot, with the developer who assigned the issue or requested the change to the pull request marked as the co-author". The commits are signed and shown as Verified. *Relation: method.* Here the AI is the author and the human is the co-author, the reverse of the trailer convention, so the paper's "bot author" signature class is needed.

**Cursor Docs — "Secrets & Network" (Cloud Agents) and "Git" integration** [`cursor2026docs`]
"Cloud Agents author and commit as Cursor Agent <cursoragent@cursor.com>". When Cursor can identify the person who started the agent, it adds that person as a Co-authored-by trailer, and commits are signed. Separately, agent commits and PRs made from the IDE and CLI can carry a `Made with Cursor` trailer, which is "on by default" and can be turned off per user or by enterprise admins. *Relation: method.* One vendor uses two different signatures depending on the surface.

**Google — Jules changelog, 2026-02-19 ("configure Jules to commit as you")** [`jules2026`]
Jules added three commit-authorship modes: Jules only, co-authored by the user and Jules, or the user only. Previously, "Jules authored every commit". *Relation: method.* From February 2026 Jules attribution depends on a user setting, and the "user only" mode leaves no trace. This is a dated change the time series has to note.

**Aider documentation — "Git integration"** [`aider2026`]
By default Aider marks its commits by appending "(aider)" to the git author (and/or committer) name. `--attribute-co-authored-by` instead appends a Co-authored-by trailer, which disables the name suffix unless that is explicitly re-enabled. `--attribute-commit-message-author` adds an `aider: ` prefix to the message. *Relation: method.* Aider has its own attribution channels (author-name suffix, message prefix) beyond trailers.

**OpenAI — Codex source, `codex-rs/ext/git-attribution`** [`openai2026codex`]
When the user's backend setting `commit_attribution_enabled` is on, the Codex extension tells the model that commit messages "must end with `Co-authored-by: Codex <noreply@openai.com>`". It also tells the model to keep existing trailers and not to duplicate this one. *Relation: method.* The Codex trailer is added by an instruction to the model, not by a git hook, so whether it appears depends on model compliance as well as the setting. This is consistent with Horikawa et al. being unable to identify Codex commits with signature rules.

## 5. Repository AI-contribution policies

**Gentoo Council (2024) — AI policy** [`gentoo2024`]
Adopted by Council vote on 14 April 2024: "It is expressly forbidden to contribute to Gentoo any content that has been created with the assistance of Natural Language Processing artificial intelligence tools". The stated grounds are copyright, quality and ethics. *Relation: context and method.* This is an example of the "bans" category in this paper's policy classification.

**NetBSD (2024) — Commit guidelines, "Do not commit tainted code"** [`netbsd2024`]
"Code generated by a large language model or similar technology … is presumed to be tainted code, and must not be committed without prior written approval by core." *Relation: context and method.* It is a ban with an approval exception, which is a boundary case for the classification.

**QEMU (2025) — "Code provenance" developer documentation** [`qemu2025`]
QEMU's policy is to "DECLINE any contributions which are believed to include or derive from AI generated content". The reason given is that contributors cannot certify the Developer's Certificate of Origin for AI output whose copyright status is "ill-defined". Non-contribution uses of AI, such as researching APIs, are outside the policy. *Relation: context and method.* It is a ban grounded in the DCO.

**curl (2025) — "Contributing to the curl project", section "On AI use in curl"** [`curl2025`]
The section was added on 2025-05-12. It accepts "code written with the help of AI" provided it meets the project's standards, requires reporters to disclose AI use in security reports, and bans users who submit "made up fake reports". *Relation: context and method.* It permits AI and requires disclosure for reports, with no attribution format specified for code.

**Ghostty (2026) — `AI_POLICY.md`** [`ghostty2026`]
"All AI usage in any form must be disclosed", including the tool used (e.g. Claude Code, Cursor, Amp) and the extent of assistance. The rules "apply only to outside contributions", and maintainers are exempt. *Relation: context and method.* The policy requires disclosure but leaves its form open, and exempts the core team. Attributed share can therefore differ from actual use even inside a repository that has a disclosure policy.

**Linux kernel — "AI Coding Assistants" (`Documentation/process/coding-assistants.rst`)** [`kerneldocs2026`]
"AI agents MUST NOT add Signed-off-by tags", because only humans can certify the DCO. Contributions should carry an `Assisted-by:` tag. In the v7.0 documentation the format is `Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]`, while the version at docs.kernel.org/process (fetched 2026-10-28) gives `Assisted-by: LLM [TOOL1] [TOOL2]`. Sasha Levin's v2 patch (23 December 2025) says the text follows "the consensus reached at the 2025 Maintainers Summit". His July 2025 RFC had proposed `Co-developed-by` tags for AI instead. *Relation: method and context.* It is a project-defined attribution trailer that differs from `Co-authored-by` and has changed format over time, so the signature catalogue must include it.

**Hora & Robbes (2026), ICSME 2026, arXiv:2605.16706 — "AI Policy, Disclosure, and Human in the Loop: How Are Contribution Guidelines Adapting to GenAI?"** [`hora2026policy`]
Across 1,000 popular GitHub repositories the authors found 118 AI policies for contributors. Of these, 78% allow AI-assisted contributions and 22% explicitly discourage AI use, while 51% require disclosure and 74% require a human in the loop. *Relation: precedent (policy classification) and method (category scheme).* It classifies policies but does not measure attributed commit shares against them, which this paper does.

## 6. Productivity and usage evidence

**Peng, Kalliamvakou, Cihon & Demirer (2023), arXiv:2302.06590 — "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot"** [`peng2023`]
In a controlled experiment, developers given GitHub Copilot finished an HTTP-server task in JavaScript 55.8% faster than the control group. *Relation: context.* It is the canonical early estimate of AI-assisted coding speed, from the autocomplete era, before attribution trailers existed.

**Cui, Demirer, Jaffe, Musolff, Peng & Salz (2026), *Management Science* — "The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers"** [`cui2026`]
The study runs randomised trials of an AI code-completion assistant at Microsoft, Accenture and an anonymous Fortune 100 firm. Pooled across 4,867 developers, it finds a 26.08% increase (SE 10.3%) in completed tasks (February 2025 working-paper abstract). Less experienced developers adopted more and gained more. *Relation: context.* It is causal evidence on volume, whereas this paper measures attribution, not productivity.

**Yeverechyahu, Mayya & Oestreicher-Singer (2024; v4 2026), arXiv:2409.08379 — "The Impact of Large Language Models on Open-source Innovation: Evidence from GitHub Copilot"** [`yeverechyahu2024`]
The design uses the fact that Copilot supported Python but not R at launch (October 2021). The authors find that "Copilot availability increases open-source contributions by 28 to 40 percent", with incremental (maintenance) contributions growing more than substantive ones (v4 abstract). *Relation: context and method.* It is a treatment–comparison design on open-source package commits, close in spirit to the matched non-AI controls used here.

**Becker, Rush, Barnes & Rein (2025), arXiv:2507.09089 — "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity"** [`becker2025`]
In an RCT with 16 experienced developers on 246 tasks in mature repositories they knew well, allowing AI increased completion time by 19%. The developers had forecast a 24% speed-up and afterwards believed they had been sped up by 20%. *Relation: context.* Use and perceived benefit can diverge from measured effect. Attributed share likewise measures use, not value.

**Anthropic (2025) — "Anthropic Economic Index: AI's impact on software development"** [`anthropic2025eisoftware`]
79% of Claude Code conversations were classified as "automation", where the AI directly performs tasks, against 49% on Claude.ai. Startup work accounted for 32.9% of Claude Code conversations, a figure the authors flag as preliminary. *Relation: context.* It is vendor-side usage data showing that agentic tools are used mostly to delegate tasks, which is the kind of use most likely to produce agent-written commits.

## 7. AI building AI (discussion)

**Kwa, West, Becker, et al. (2025), arXiv:2503.14499 / NeurIPS 2025 — "Measuring AI Ability to Complete Long Software Tasks"** [`kwa2025`]
The authors define the 50%-task-completion time horizon. Frontier models such as Claude 3.7 Sonnet reach about 50 minutes, and the horizon has doubled roughly every seven months since 2019. *Relation: context.* Capability trends explain why the attributed share might rise, but benchmark horizons are not evidence about real repositories.

**Favaro & Clark (2026), Anthropic — "When AI builds itself"** [`favaro2026`]
"As of May 2026, more than 80% of the code we merge into Anthropic's codebase was authored by Claude." This is measured as the share of lines merged to production "that can be attributed to Claude". The authors call it conservative because of gaps in their attribution pipeline. *Relation: precedent (an attribution-based share inside a frontier lab) and contrast.* The figure is internal, line-based and not reproducible. This paper measures the public, open-source part of the AI software stack from outside.

**Shumailov, Shumaylov, Zhao, Papernot, Anderson & Gal (2024), *Nature* 631:755–759 — "AI models collapse when trained on recursively generated data"** [`shumailov2024`]
Training on recursively generated model output causes "model collapse" in LLMs, VAEs and Gaussian mixture models. *Relation: context (discussion only).* It motivates asking how much AI-written code enters the training and inference stack. The paper does not claim any collapse-type effect for code infrastructure.

---

## Gap statement

Counting explicit AI attribution in git history is established practice, not a new idea:
- Robbes et al. (2026) estimate coding-agent adoption across a 128,018-project GitHub sample from co-author trailers, agent author accounts, configuration files, branch names and PR labels.
- Horikawa et al. (2026) and Li et al. (2026) build agent-commit and agent-PR datasets from the same kinds of signatures.
- Kinlan (2026), SemiAnalysis (2026) and the Amplifying dashboard (2026) publish platform-wide counts of `Co-Authored-By: Claude`-type commits.
- GitHub's Octoverse 2026 reports agent-started PR shares from internal telemetry.
- Anthropic reports an internal attributed-line share above 80% (Favaro & Clark, 2026).

This paper formalises that practice and does not claim to have invented it.

The searches documented here (to 2026-10-28) found no prior work that does any of the following:

1. **Defined population.** A pre-registered, monthly, commit-level series (2023–2026) of the explicitly AI-attributed share of default-branch commits for a defined population of open-source AI-infrastructure repositories, meaning the frameworks, inference engines and training libraries that models are built with. The series also covers the coding-agent harness repositories themselves, each set against matched non-AI control repositories. Prior counts either sample GitHub broadly (Robbes et al.; Kinlan; Amplifying), estimate AI-written code by classifier rather than attribution (Daniotti et al.), or are internal to one organisation (Favaro & Clark).
2. **Trailer survival through squash merges.** Robbes et al., Horikawa et al. and Amplifying each name squash merges, or signatures attached at PR level, as a reason their counts are floors or noisy. None reports how often an AI trailer present on PR commits survives into the squash commit on the default branch, or how that depends on each repository's squash-message setting (GitHub Docs; GitHub Changelog 2019).
3. **Policy linkage.** A link between measured attributed shares and each repository's stated AI-contribution policy (bans / requires disclosure / mentions without a rule / silent). Hora & Robbes (2026) classify policies in 1,000 repositories but do not relate them to attributed commit shares.

The paper's quantity is *attributed* commits, not *AI-written* commits:
- **It is a lower bound.** Vendors let users disable or change attribution (Claude Code, Cursor, Jules, Codex), and policies such as Ghostty's exempt maintainers.
- **It is complementary to detection.** Classifier-based estimates (Daniotti et al.) and signature-free detectors (Horikawa et al.) answer a different question with different error profiles.

## Could not verify (not cited)

- **Gemini CLI attribution behaviour.** No official documentation of a default commit trailer or attribution setting was found. A GitHub code search of `google-gemini/gemini-cli` for `Co-authored-by` returned no hits. The paper should establish Gemini CLI's behaviour empirically (fixture or observed commits) or describe it as undocumented.
- **Cursor `Co-authored-by: Cursor <cursoragent@cursor.com>` trailer form.** It appears in Cursor community-forum thread titles but not in Cursor's official docs, which document `Cursor Agent <cursoragent@cursor.com>` as the author identity for cloud agents. Signature qualification should rely on observed commits.
- **theconsensus.dev, "Source-available projects and their AI contribution policies" (2026-03-02).** The fetch returned HTTP 403. A search snippet claimed some projects that ban AI still contain AI-tool commits. This is relevant but unverified.
- **SemiAnalysis method.** The source is cited, but its measurement method is behind a paywall and could not be checked.
- **NetBSD exact adoption date.** The guideline text was verified; the May 2024 date comes only from secondary press.
- **QEMU 2026 relaxation proposal (P. Bonzini, reported by Phoronix).** Secondary only, and not confirmed as merged. The QEMU master documentation fetched on 2026-10-28 still says DECLINE.
- **Ghostty pre-2026 disclosure rule and the reported ~50% of PRs with AI disclosure.** Secondary only. The cited `AI_POLICY.md` history starts 2026-01-22.
- **RepoComplianceBench (Yang, He & Zhou, 2026).** Seen only second-hand in a blog post; the arXiv listing was not checked.
- **Hoffmann et al. sample size (~180,000 developers) and Daniotti et al. developer counts.** Figures differ across secondary sources and paper versions, so none are quoted.
