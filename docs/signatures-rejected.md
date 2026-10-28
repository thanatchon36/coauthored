# Rejected signature candidates

Candidates found during discovery (pilot repositories and GitHub commit search, 2026-10-28) that are **not** in
`configs/signatures.yaml`, with the reason. The catalogue counts only vendor-fixed identities and verbatim
markers; MISSION §1.6 forbids free-text matching.

| Candidate | Seen as | Reason |
|---|---|---|
| `opencode (<model>) <ai@local>`, `opencode/main (...) <opencode@local>` | co-author | User-configured identity on a non-routable placeholder address; not a vendor identity. `<noreply@opencode.ai>` is kept. |
| `Roo Code (...) <roo-code@example.com>`, `Roo Code <roo@code.local>` | co-author | User-configured placeholder addresses. Roo Code is archived. |
| `cline-<word>-<n> <...@cline-agent.local>` | co-author | Per-session generated names on a placeholder domain; too few public commits to qualify a pattern. |
| `OpenHands ... <agent@local>` | author | User-configured placeholder address. |
| `Committed-By-Agent: goose` | trailer | Not documented as a Goose default; appears to be one user's convention. |
| `Collab-Lane:`, `Collab-Session:` (with "kiro") | trailer | A third-party workflow convention, not Kiro's own attribution. |
| `Signed-off-by: <AI identity>` | trailer | A Developer Certificate of Origin certification, not attribution (DECISIONS D13). Commits that carry it usually also carry a co-author line. |
| `dependabot[bot]`, `github-actions[bot]` as co-author | co-author | Maintenance bots; not AI attribution. |
| `openai-sdks[bot]` | author, co-author | SDK release automation; a maintenance bot under the `[bot]` rule. |
| Vendor-employee addresses (`@anthropic.com`, `@openai.com`, `@codeium.com`, …) | author, co-author | People, not tools. A vendor domain is never a signature by itself. |
| Free text ("Claude helped", "made with Cursor", tool names in subjects) | message | Free-text matching is out of scope (MISSION §1.6). |
| `<name>-claude[bot]` (per-user GitHub apps) | co-author | Custom apps registered by individual users; names and ids are not fixed by the vendor. |
| `trae (<model>) <ai@local>` | co-author | User-configured placeholder address. `TRAE CLI <…@bytedance.com>` is kept. |
| `qwen-code-dev-bot`, `letta-integration[bot]` | author, co-author | Project CI/integration automation; maintenance bots under the `[bot]` rule or not AI attribution. |
| `Replit-Commit-*` trailers | trailer | Replit workspace checkpoints; they also mark human edits made in Replit. `Replit Agent <agent@replit.com>` is kept. |
| `Lab: kimi`, `Order: …/kimi-*` | trailer | One user's workflow convention. |
| `Sweep <236279702+sweep-ai@users.noreply.github.com>` | co-author | Only one public commit found by two searches (2026-10-29); fewer than the three evidence URLs required. |
