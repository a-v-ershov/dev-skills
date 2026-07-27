# Operating context & measurement (elicitation guide)

The full question set behind two of `design-architecture`'s stage-1 dimensions: **where the product
will actually run** and **how its success will be observed**. The skill body names the dimensions;
this file holds the questions, the reasoning, and the traps. Ask only what changes the decision and
isn't already answered by the brief, the prior phases, or the repo — every answer lands as a
quality-attribute scenario or a constraint.

---

## Part 1 — Operating context (hosting)

Hosting belongs in the architecture, not in a later chore: it bounds which components are even
available (a managed all-in-one platform vs assembling auth and storage yourself), and reversing it
later is a migration with the data attached.

### The questions

| # | Question | Why it changes the architecture |
|---|----------|--------------------------------|
| 1 | **Where are the users?** One region · several · global. | The strongest single filter. Decides reachability without workarounds, which payment rails work, and what "close to the user" means for latency. |
| 2 | **How many users are expected?** A handful (me and some friends) · dozens · hundreds-to-thousands · existing traffic. | The real load measure. Decides the tier, whether a free tier's ceiling gets hit, whether a service that idles to sleep is acceptable, and whether backups are worth their cost. |
| 3 | **Must the data sit in a particular jurisdiction, and are there rules to satisfy?** (GDPR, a national data law, sector rules.) | Ask it **directly** and never infer it. "Not a requirement" opens the managed platforms — cheaper, less to build. "Required" narrows the field, usually costs more, and often means assembling auth and file storage by hand plus paperwork. |
| 4 | **Monthly budget?** 0 · small · real. | The second-strongest filter after geography. |
| 5 | **How can it be paid?** | Some platforms are unreachable for some payment methods. Better known now than at checkout. |
| 6 | **Under a traffic spike, which is worse — a surprise bill or slowness?** | Usage-based vs fixed pricing. A temperament question, not a technical one — so ask, don't assume. |
| 7 | **Appetite for operations?** "Press a button and forget" vs "happy to run a server". | Managed vs self-hosted. |
| 8 | **Is there a domain?** Which zone, who owns it. | Feeds the manual setup checklist. |
| 9 | **Deadline?** Ship today vs a month. | Urgency legitimately favors the path of least resistance even when it costs more. |
| 10 | **How painful would losing the data be?** | Decides whether backup + a *tested* restore path is in scope. |

For a mobile product, add: **is a store listing needed** (or does an installable web app do), **which
stores**, and the willingness to pay the fee and wait for review. If in-app payment is planned, say
plainly that the channel dictates the legal form of the seller, and ask whether that is acceptable.

### Traps

- **Never ask for the project's status** — "is this a real project or just practice?", "demo or
  production?". It is an unanswerable self-assessment and nothing can be computed from it. Everything
  you wanted from it is available from questions 2, 3, 4 and 10, which have measurable answers.
- **Never infer a compliance requirement.** "It's a serious product" does not imply data residency,
  a registered business, or a privacy policy. That is the user's answer to give, not your deduction.
- **Never let "we'll figure out hosting later" stand.** Postponing it is itself a decision, and the
  one that costs the most to unwind.
- **Don't quote prices from memory.** Tiers, free-tier ceilings and regions move constantly — verify
  the shortlist in stage 2 (this is usually the best use of the phase's research budget), and label
  anything unverified rather than dressing it in a plausible number.

### What it produces

The `## Deployment & environments` section of the architecture doc: 2–3 platform options compared on
cost at the stated scale, payment and reachability, regions and residency, pricing shape, ops burden
and lock-in; the recommendation and its ADR; environments (prod / staging?); domain and TLS; where
secrets live; backups and the restore path; and the **manual setup checklist** — everything a human
must click through once (domain, DNS, payment method, provider or store accounts, any registration),
listed rather than assumed.

**Who executes it:** `setup-production-environment`, invoked by hand from the build or release phase.
That skill reads this section as its contract and turns it into a real environment — sorting each gap
into what it fixes in the repo, what it can do through an authorized provider CLI, and what only the
human can do in a dashboard. So write this section for an executor, not for a reader: name the
platform, the environments, and the manual items concretely enough to act on. This phase **decides**;
it never configures, never deploys, and never opens an account.

---

## Part 2 — Measurement (analytics & telemetry)

`define-product-requirements` committed to success metrics. Unless something actually produces them,
they stay aspirations. Work the order **question → metric → event** — never "let's add a counter and
see what accumulates", which yields dashboards nobody reads.

### The questions

1. **What questions must the product answer?** "Where do people drop off before paying?" "Is anyone
   coming back after week one?" For each: what would you *do* differently depending on the answer? A
   question that changes no decision needs no metric.
2. **Which of those does the product's own database already answer?** For a small product, most of
   them — a funnel over rows the app already writes is a query, not an integration. Name those
   metrics and sketch the query. This is the step that prevents reflexively bolting on a third-party
   tool.
3. **What genuinely needs client-side events?** Only what never reaches the backend: page views,
   scroll depth, an abandoned form, which variant was seen. That, and only that, justifies a counter.
4. **How does a production failure become visible at all?** Logs someone reads, an error tracker, an
   alert — and who receives it. "We'd notice" is not an answer.
5. **What are the constraints?** May user data go to a third-party service (this ties straight back
   to the residency answer above)? Budget? Consent obligations that follow from the audience?

### Traps

- **A metric with no owner and no decision attached** is decoration — cut it.
- **A third-party tool for something the database already answers** is cost and a privacy surface for
  nothing.
- **"None — the database is enough"** is a perfectly good outcome. Record it as the decision, with
  the queries, so the next phase knows it was decided rather than forgotten.
- **Errors are not analytics.** Product measurement and operational visibility are two different
  needs; answer both.

### What it produces

The `## Analytics & telemetry` section: the question → metric → source → how table; which metrics the
own database answers (with query sketches); which need client events and the chosen tool (or none);
how errors surface and to whom; and what user data leaves the system, checked against the residency
decision.

**Who executes it:** the same skill, `setup-production-environment` — it installs the counter, wires
the named events, sets up error tracking, and checks that the metrics the own database is supposed to
answer are actually answerable (a funnel step with no timestamp cannot be counted). So name the events
and the metrics precisely: a vague "we'll add analytics" becomes nothing installed.
