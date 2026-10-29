# LinkedIn drafts (not posted)

Numbers match `results/numbers.json` at the commit that adds this file. Keep "AI-attributed"; never "written by
AI". Variant D is the launch post; it goes with `poster.png` (1200×1500, built by `scripts/poster.py` from the
same `numbers.json`). LinkedIn shows about the first 210 characters before "…more", so the hook is the first
three lines; links go in the first comment, where they do not cost reach.

Links: paper <https://thanatchon36.github.io/coauthored/paper/> · code and data
<https://github.com/thanatchon36/coauthored> · DOI <https://doi.org/10.5281/zenodo.23752989>.

---

## Variant D: launch post (with `poster.png`)

In 2024, 102,709 commits landed in 42 open-source repositories that train and serve AI models: PyTorch, JAX,
vLLM, Transformers, DeepSpeed, llama.cpp and more.

How many declared AI help? Zero.

Two years later: one in eleven.

I pre-registered the study, then read 2.85 million commits from 96 repositories on a single day. A commit
counts only if it carries an explicit AI attribution: a Co-authored-by trailer naming a tool, an AI-agent
account, or a "generated with" marker. No guessing from code style.

What the data say:

→ July–September 2026: 8.7% of commits to AI infrastructure were AI-attributed (95% CI 4.0–14.5%).

→ The twist: 42 popular non-AI projects (Django, CPython, Home Assistant…), matched on stars, language and
activity, were at 7.1%. In six of the nine months of 2026 they were ahead. The intervals overlap: no evidence
that the people building AI declare more AI help than everyone else, and no proof that they don't.

→ Even the coding agents' own repositories (OpenHands, Cline, Codex, Gemini CLI…) were at 10.3%. Not clearly
ahead either.

→ The record survives the merge: 92% of sampled pull requests with an attributed commit still carried the
attribution on the main branch (184 of 200).

→ Attributed commits are larger: median 108 lines changed vs 32. Mostly which repositories and when, though;
within a repository and year the gap shrinks to 1.4×.

→ Only 1 of the 96 projects bans AI contributions. 20 require disclosure. 55 ship instructions for coding
agents (AGENTS.md, CLAUDE.md).

→ The leading tool changed every few quarters: OpenHands in early 2025, Gemini Code Assist by late 2025,
Claude Code through 2026, partly because it signs by default and many tools don't.

Two caveats that belong on every chart:
1. Every number is a lower bound. Attribution can be switched off, stripped at merge, lost when code is
exported from a company monorepo, or never added.
2. AI-attributed is not "written by AI". The trailer says a tool took part, not how much of the change it
produced.

Of the five pre-registered hypotheses about the curve, only the level one met its rule, and only on its point
estimate. The ones that failed are in the paper too.

Everything is open: paper, code, repository-month aggregates and a catalogue of 52 signatures for 28 tools,
each backed by three public commits. No API keys. Run it on your own organisation in ten minutes:

pip install coauthored
coauthored report --org <your-org>

Independent personal research. Public data only. Does not represent the views of any employer or institution.

#OpenSource #AI #SoftwareEngineering #CodingAgents #Research

First comment:
📄 Paper: https://thanatchon36.github.io/coauthored/paper/
💻 Code and data: https://github.com/thanatchon36/coauthored
🔗 DOI: https://doi.org/10.5281/zenodo.23752989

---

## Variant D, Thai

ปี 2024 มี commit 102,709 รายการเข้า repository โอเพนซอร์ส 42 แห่งที่ใช้ฝึกและรันโมเดล AI: PyTorch, JAX, vLLM,
Transformers, DeepSpeed, llama.cpp และอื่น ๆ

กี่รายการที่ระบุว่าใช้ AI ช่วย? ศูนย์

สองปีต่อมา: หนึ่งในสิบเอ็ด

ผมลงทะเบียนแบบวิจัยไว้ล่วงหน้า (pre-registration) แล้วอ่าน commit 2.85 ล้านรายการจาก 96 repository ในวันเดียว
commit จะถูกนับก็ต่อเมื่อมีการระบุ AI อย่างชัดเจน: trailer "Co-authored-by" ที่ระบุชื่อเครื่องมือ บัญชี AI agent
หรือเครื่องหมาย "generated with" ไม่มีการเดาจากสไตล์โค้ด

ข้อมูลบอกอะไร:

→ กรกฎาคม–กันยายน 2026: 8.7% ของ commit ในโครงสร้างพื้นฐาน AI ระบุว่าใช้ AI (95% CI 4.0–14.5%)

→ จุดพลิก: โปรเจกต์ยอดนิยมที่ไม่ใช่ AI 42 แห่ง (Django, CPython, Home Assistant ฯลฯ) ที่จับคู่ตามจำนวนดาว ภาษา
และความคึกคัก อยู่ที่ 7.1% และใน 6 จาก 9 เดือนของปี 2026 กลุ่มนี้นำอยู่ด้วยซ้ำ ช่วงความเชื่อมั่นซ้อนทับกัน:
ไม่มีหลักฐานว่าคนที่สร้าง AI ระบุการใช้ AI มากกว่าคนอื่น และไม่มีข้อพิสูจน์ว่าไม่ใช่

→ แม้แต่ repository ของ coding agent เอง (OpenHands, Cline, Codex, Gemini CLI ฯลฯ) ก็อยู่ที่ 10.3%
ไม่ได้นำอย่างชัดเจนเช่นกัน

→ บันทึกรอดผ่านการ merge: 92% ของ pull request ที่สุ่มตรวจและมี commit ระบุ AI ยังคงมีการระบุนั้นบน main
branch (184 จาก 200)

→ commit ที่ระบุ AI มีขนาดใหญ่กว่า: มัธยฐาน 108 บรรทัดเทียบกับ 32 แต่ส่วนใหญ่มาจากว่าเป็น repository ไหนและช่วงเวลาใด
เมื่อเทียบภายใน repository และปีเดียวกัน ช่องว่างเหลือ 1.4 เท่า

→ มีเพียง 1 ใน 96 โปรเจกต์ที่ห้าม AI มีส่วนร่วม 20 แห่งกำหนดให้ต้องเปิดเผย 55 แห่งมีไฟล์คำสั่งสำหรับ coding agent
(AGENTS.md, CLAUDE.md)

→ เครื่องมือที่นำเปลี่ยนหน้าทุกไม่กี่ไตรมาส: OpenHands ต้นปี 2025, Gemini Code Assist ปลายปี 2025, Claude Code
ตลอดปี 2026 ส่วนหนึ่งเพราะมันลงชื่อโดยอัตโนมัติ ขณะที่หลายเครื่องมือไม่ทำ

ข้อควรระวังสองข้อที่ควรติดไว้กับทุกกราฟ:
1. ทุกตัวเลขเป็นขอบล่าง (lower bound) การระบุปิดได้ ถูกตัดออกตอน merge ได้ หายไปตอน export จาก monorepo
ของบริษัทได้ หรือไม่เคยถูกใส่เลย
2. "ระบุว่าใช้ AI" ไม่ใช่ "AI เขียน" trailer บอกแค่ว่ามีเครื่องมือมีส่วนร่วม ไม่ได้บอกว่าเขียนไปมากแค่ไหน

จากสมมติฐานที่ลงทะเบียนไว้ล่วงหน้า 5 ข้อเกี่ยวกับเส้นกราฟ มีเพียงข้อเดียวเรื่องระดับที่ผ่านเกณฑ์
และผ่านเฉพาะค่าประมาณจุด ข้อที่ไม่ผ่านก็อยู่ใน paper ด้วย

ทุกอย่างเปิดเผย: paper โค้ด ข้อมูลรวมราย repository-เดือน และแคตตาล็อก 52 ลายเซ็นของเครื่องมือ 28 ตัว
แต่ละรายการมี commit สาธารณะ 3 รายการเป็นหลักฐาน ไม่ต้องใช้ API key รันกับองค์กรของคุณเองได้ใน 10 นาที:

pip install coauthored
coauthored report --org <your-org>

Independent personal research. Public data only. Does not represent the views of any employer or institution.

#OpenSource #AI #SoftwareEngineering #CodingAgents #Research

คอมเมนต์แรก:
📄 Paper: https://thanatchon36.github.io/coauthored/paper/
💻 Code and data: https://github.com/thanatchon36/coauthored
🔗 DOI: https://doi.org/10.5281/zenodo.23752989

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
