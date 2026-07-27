# Review return format (shared — spec pipeline)

How the `spec-reviewer` agent reports. Its **final message is the deliverable** — it writes no file,
so there is nothing to keep, merge, or delete. The phase's fix stage reads this list and applies it
to `<artifact>.research.md` directly.

Rules: at most **7 findings**, most severe first. No preamble, no restatement of the draft, no
praise for what is right, no summary of the phase. Findings only.

```
ИТОГО — <N> problems · 🔴 <c> · 🟡 <m> · ⚪ <k>

1. 🔴 <short title>
   Where: <section / quoted claim from the draft>
   Type: <internal contradiction | unsupported claim | unverified claim | weak source | stale
     source | vendor metric as objective | feature traces to nothing | flow needs missing feature |
     metric not measurable | audience too vague | weak fork justification | contradicts prior
     phase | placeholder left in>
   Problem: <one or two lines — what's wrong and why it changes something>
   Fix: <fix | drop | reword | attribute | verify (worth one reserved fetch) | ask the human>

2. 🟡 <short title>
   …
```

If the draft is clean, return one line — `ИТОГО — 0 problems · 🔴 0 · 🟡 0 · ⚪ 0` — and nothing
else. A clean review is a valid outcome; do not manufacture findings to look useful.

## Gaps

A gap — something the draft did **not** answer — is reported as a finding like any other, typed
`unsupported claim` or `placeholder left in` as fits, with `Fix:` naming what should fill it. The
reviewer does not fill gaps itself: it is offline, and filling them is the phase's job (within its
research budget, see `research-method.md`).
