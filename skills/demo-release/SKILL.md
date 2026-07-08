---
name: demo-release
disable-model-invocation: true
description: "Webinar DEMO variant of the release phase — runs the real security + performance audits and prints a pre-deploy CHECKLIST, for a live before/after demo. Use only for the vibe-coding course demo, NOT for real releases (that's release-product). It spawns the genuine audit-security and audit-performance skills as fresh, read-only subagents in parallel, collects what they find, and renders it as a green/red pre-deploy checklist — the payoff being to SHOW that the method knows what to check before shipping (leaked keys, missing auth, injection, slow queries) versus a vibe-coder who doesn't. REPORT-ONLY: it does NOT file rework tasks, does NOT loop fixes, and does NOT cut a release. Reuses the real audits; only the fix/ship machinery is stripped."
argument-hint: "[--audit security|performance]"
---

# Demo Release Skill (webinar variant — audits → checklist, report-only)

You are running the **demo** version of the release phase for a live webinar. The payoff of this act is
a **pre-deploy checklist**: the method automatically knows the things a vibe-coder doesn't even know to
check (a leaked API key, an unprotected endpoint, an injection hole, an N+1 query) — and checks them
every single time before shipping. The "before" (a co-host who just deploys and hopes) is set up live;
your job is the "after".

This is **not** `release-product`. You do not file rework tasks, you do not run the fix loop, and you do
not `cut-release`. You **audit and report** — that's the whole act.

## Language

Respond and reason in whatever language the user addressed you in — write the checklist in that language.
Never translate code, identifiers, commands, file paths, or CVE/CWE ids.

## What stays REAL

- **`audit-security`** and **`audit-performance`** are the genuine skills — spawn each as a **fresh,
  independent, read-only subagent**. They probe the real running/checked-in system and prove findings
  with evidence; you don't hand-wave the results.
- They are read-only and independent, so **run them in parallel** (one message, two agent spawns) — just
  like the real release phase.

## What you STRIP (report-only)

Tell each audit subagent, in its spawn prompt, to run **report-only**: probe, rank, and **return the
findings** (and write its `.buildloop/release/<name>-audit.md` doc), but **do NOT file rework tasks**, do
NOT invoke `plan-development`, and do NOT try to fix anything. You then render the checklist. No fix
loop, no `cut-release`.

## Prerequisites

- **A contract to audit against** — `audit-security` reads the trust boundaries + STRIDE-lite threat
  model from `.buildloop/project-spec/architecture.research.md` (which `demo-spec` wrote); `audit-performance`
  reads the quality-attribute scenarios there. If the spec is thin, the audits fall back to their
  baseline checklists and note the gap — fine for a demo.
- **A running/buildable project** — the audits need the demo SEO service (or whatever target) present so
  they can actually probe. Dynamic checks may need the stack up (the audits bring it up themselves).

## Procedure (copy this checklist into your response and check off as you go)

```
- [ ] Stage 0: Frame — say this is the demo deploy-checklist: real audits, report-only, no fixes/ship
- [ ] Stage 1: Audit — spawn audit-security + audit-performance in PARALLEL as fresh read-only subagents (report-only)
- [ ] Stage 2: Collect — gather each agent's findings + verdict
- [ ] Stage 3: Checklist — render a pre-deploy checklist (✅/❌ per checked item, with the evidence one-liner)
- [ ] Stage 4: Close — say what the real release adds (files rework, fixes + re-audits, then cut-release)
```

### Stage 0: Frame
State plainly: this is the **demo** deploy checklist — the real security and performance audits, run
read-only, rendered as a checklist. No fixes are applied and nothing is shipped here.

### Stage 1: Audit (parallel fan-out)
Honor `--audit <name>` to run just one; otherwise spawn **both** in one message:
- `audit-security` (`subagent_type` per the audit; it preloads its skill) — secrets in code/history,
  authn/authz on protected paths, injection, the lethal trifecta, insecure data handling, supply chain.
- `audit-performance` — the quality-attribute scenarios: slow paths, N+1 queries, unbounded work,
  missing indexes/caching, payload sizes.
In each spawn prompt, include the **report-only** instruction above. They are read-only and independent —
they collide on nothing.

### Stage 2: Collect
Gather each subagent's returned findings and verdict (clean / N blockers / N majors) and its written
`.buildloop/release/<name>-audit.md`. Don't re-derive — use what they proved.

### Stage 3: Render the checklist (the payoff)
Print a compact **pre-deploy checklist** grouped by audit. One line per checked item with a status and a
short evidence note, e.g.:

```
🔒 Security
  ✅ No secrets in code or git history (gitleaks sweep clean)
  ❌ /api/articles/:id returns another user's article — missing ownership check (IDOR)  [blocker]
  ✅ SQL is parameterized (no string-built queries)
  ❌ OpenAI key logged in request logs on error  [major]

⚡ Performance
  ✅ Article list paginated (no unbounded query)
  ❌ N+1 on the dashboard: one query per article to fetch its status  [major]
```

Lead with what's **red** (that's the value — it caught something real), then what passed. Each red item
is what a naive deploy would have shipped. Keep it scannable — this is the frame that "sells" the act.

### Stage 4: Close
Say what the **real** `release-product` does on top: it files each 🔴/🟡 as a rework task, drives
`build-product` to fix them, **re-audits to confirm the hole is closed**, and only then invokes
`cut-release` (version + changelog + tag + PR, always confirmed, stops before prod deploy). The demo
stops at the checklist on purpose.

## Rules

1. Real audits, spawned as fresh **read-only** subagents, run in **parallel**.
2. **Report-only** — instruct each audit not to file rework tasks or fix anything; you never `cut-release`.
3. Render findings as a pre-deploy **checklist**, red items first — that contrast is the act.
4. Prove-backed only: each item reflects what the audit actually checked; no invented passes.
5. Close by naming what the full release phase adds (file → fix → re-audit → cut).
