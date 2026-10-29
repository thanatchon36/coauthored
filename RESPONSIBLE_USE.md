# Responsible use

`coauthored` counts commits whose metadata declares AI involvement. It is meant for describing **projects and
organisations**, not people.

## Do

- Report shares for repositories, groups of repositories or organisations, with the denominator and the window.
- Call them **AI-attributed** commits and a **lower bound**. Attribution can be switched off, lost at merge, or
  never added, and the rate of each varies by tool and by repository.
- Say which tools sign by default when you compare tools. A tool that signs every commit will look more popular
  than one that signs none.
- Keep the snapshot date and head SHAs (`data/manifest.json` does this) so that someone else can check your
  numbers.

## Do not

- **Do not rank, assess, monitor or discipline individual developers** with this tool or its data. An
  attributed commit says a tool took part, not how much, and an unattributed one says nothing at all. Who
  enables attribution is a matter of settings and habit, so per-person counts measure disclosure, not use.
- Do not try to recover identities from the hashes. The released dataset holds aggregates only; the scanner's hashes
  are salted with a secret that stays on the machine that ran the scan (`.env`, git-ignored).
- Do not describe attributed commits as "written by AI", or the share as the fraction of code produced by AI.
- Do not read a high or low share as a sign of quality, safety or productivity. The paper finds no difference
  in revert rates within repositories, and measures nothing else about quality.
- Do not use a low share as evidence that a project does not use AI tools, or a high share as evidence that it
  breaks its own contribution policy. Policies and attribution defaults differ, and many projects exempt
  maintainers.

## Scanning your own organisation

`coauthored report --org <org>` clones public repositories with commit objects only and prints monthly
repository-level shares. It stores hashed identities in `data/raw/` so that distinct authors can be counted;
delete that directory when you are done if you do not need it. If you publish results, publish aggregates.

## Data

The dataset (CC BY 4.0) holds no names, e-mail addresses, commit messages or identity hashes, and dates are in
UTC. Commit SHAs are included and link to public commits; please do not use them to single out the people who
made those commits.

Questions or concerns: open an issue on the repository.
