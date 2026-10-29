# LinkedIn drafts (not posted; for after STOP 2)

Numbers match `results/numbers.json` at the commit that adds this file. Replace `<link>` with the paper URL once
the repository is public. Keep "AI-attributed"; never "written by AI".

---

## Variant A: the surprise

I expected the code that trains AI models to be the most AI-assisted code in open source.

So I counted. 42 AI-infrastructure repositories (PyTorch, JAX, Transformers, vLLM, llama.cpp, DeepSpeed and
more), every commit since 2023, read on one day. A commit counts only if it carries an explicit AI attribution:
a co-author trailer, an agent account, or a tool's "generated with" marker.

In July–September 2026: 8.7% of commits were AI-attributed. In 2024: almost none.

The twist: 42 popular non-AI repositories, matched on stars, language and activity, were at 7.1%. In six
months of 2026 they were *ahead*. The data can't tell the groups apart, so no "AI builds AI faster" headline.

Two caveats I'd put on every chart: this is a lower bound (attribution can be switched off, lost at merge, or
never added), and an attributed commit says a tool took part, not how much of the change it wrote.

Pre-registered before scanning; every number in the paper is generated from the data.

Independent personal research. Public data only. Does not represent the views of any employer or institution.

paper + code public — run `coauthored report --org <yours>` on your own organisation in 10 minutes

---

## Variant B: the method

How much of the code behind AI is made with AI? You can't answer that from inside one company. You can
answer a narrower question in public: how many commits *declare* AI involvement?

What I did:
• Pre-registered the design, hypotheses and repository lists before scanning anything
• Built a catalogue of 52 AI signatures for 28 tools, each backed by three public example commits
• Read the full history of 96 repositories on one day: 2.85M commits
• Checked how often attribution survives the merge: 92% of sampled attributed pull requests keep it

Result: 8.7% of commits to AI-infrastructure repositories were AI-attributed in 2026-Q3, about one in 11.
Matched non-AI repositories: 7.1%. Of five pre-registered hypotheses about the curve, only the level one met
its rule, and only on its point estimate. I'm publishing the ones that failed too.

Independent personal research. Public data only. Does not represent the views of any employer or institution.

paper + code public — run `coauthored report --org <yours>` on your own organisation in 10 minutes

---

## Variant C: short

AI-infrastructure repositories, 2026-Q3: 8.7% of commits carry an explicit AI attribution. 2024: almost none.

Matched popular non-AI repositories: 7.1%. The people building models aren't measurably ahead of everyone else.

A lower bound, not a share of code "written by AI". Pre-registered; 96 repositories, 2.85M commits, one snapshot.

Independent personal research. Public data only. Does not represent the views of any employer or institution.

paper + code public — run `coauthored report --org <yours>` on your own organisation in 10 minutes
