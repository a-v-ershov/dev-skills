# The production checklist (derived from the stack, not memorized)

What "ready for production" means, by area. **Derive the concrete checks from this project's
technologies** — the manifest, the deploy config in the tree, the code, and the architecture doc — never
from the examples below. The examples are web-shaped because that is the common case; a mobile,
desktop, CLI, or library product has its own version of each row, and a check that does not apply is
recorded as N/A rather than silently dropped.

Each item below is **detected** in Stage 2 and, if missing, **sorted** in Stage 3 into ① repo ·
② authorized CLI with a per-action yes · ③ human in the dashboard.

---

## 1. Platform & release channel

The build has somewhere to land and people have a way to reach it.

| Check | Typical group | Notes |
|-------|---------------|-------|
| The deploy target is connected to the repository and the build actually lands there | ③ | The one thing that cannot be done from a terminal on most platforms |
| A deploy config exists in the tree and matches the stack (`vercel.json`, `Dockerfile`, `fly.toml`, `app.json` / `eas.json`, a platform CI file) | ① | Read the platform's current official format — these go stale |
| The **production build** is green | ① | A deploy of something that does not build is the classic failure; run the stack's own production build |
| The access channel is ready | ③ | web: domain + TLS · mobile: store account, signing certificate and profile · desktop: signing + installer/auto-update · CLI/library: registry account and a free package name |
| Environments match what the architecture decided (prod only, or prod + staging) | ②/③ | A staging environment that shares the production database is worse than no staging |

## 2. Data

Real data is separated from test data, and the schema in production matches the code.

| Check | Typical group | Notes |
|-------|---------------|-------|
| Production does not read or write the test database, and no test/preview environment writes to the production one | ③ | The human confirms this — you usually cannot see it from the repo |
| **Migrations / schema are applied to the production database**, not only locally | ② | Irreversible on live data. Name it as irreversible before running |
| Seed / demo data is not loaded into production | ①/② | Seeding production with fixtures is a real and common accident |
| Backups exist **separately from the database**, and the restore path has been walked once | ③ | Required when the architecture called data loss painful; otherwise offered |
| A rollback path for a bad release exists and is written down | ②/③ | Belongs in the runbook either way |

## 3. Configuration & secrets

Everything the code reads from the environment is set **in the target environment**, not just in a
local `.env`.

| Check | Typical group | Notes |
|-------|---------------|-------|
| The list of environment variables the code actually reads is extracted **from the code** and handed over for confirmation | — | This list is the contract for everything else in this section |
| Each of them is set on the platform for the production environment | ② | Set through the CLI where one is authorized; otherwise ③ with the exact variable names |
| `.env` is in `.gitignore` and `.env.example` is current | ① | |
| The framework's **public** prefix (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, …) is on public values only | ① | A secret behind a public prefix ships to every visitor |
| The production build does not hand secrets to the client | ① | For mobile/desktop, anything in the bundle is visible — that belongs to the threat model |
| A key that has ever been committed is **rotated at the provider** | ②/③ | Deleting it from the code does not help: history, forks, caches, bots |

## 4. Money

Every paid provider and the platform itself has a **hard stop**, not a notification.

| Check | Typical group | Notes |
|-------|---------------|-------|
| A hard spending cap on each paid API and on the platform | ③ | Spend management / a billing limit. A notification is not a cap — it tells you afterwards |
| Rate limiting on every endpoint that calls a paid API | ① | The threat model names these surfaces |
| Sign-up and public forms have some abuse protection | ① | |
| The expected monthly cost is compared against the budget the architecture recorded | — | A large gap is a finding, not a rounding error |

## 5. Observability (analytics, errors, logs)

The architecture's **Analytics & telemetry** section is the contract here — question → metric → event.
Own database first: a metric answerable by a query needs no third-party tool.

| Check | Typical group | Notes |
|-------|---------------|-------|
| The metrics the architecture said the **own database** answers are actually answerable — the columns and timestamps exist | ① | A funnel with no timestamp on the step cannot be counted |
| The client-side counter it chose (if any) is installed and fires the **named events** | ① | Only events that never reach the backend belong here |
| Error tracking / operational visibility exists: a production error becomes visible to a named person | ①/③ | The client library is ①, the account and alert routing is ③ |
| The privacy line the architecture drew is held: what leaves the system, to whom, consent where the audience requires it | ①/③ | |

## 6. Continuous integration (offered, not required)

| Check | Typical group | Notes |
|-------|---------------|-------|
| Checks run automatically on push, using the **same commands** as the local gate | ① | Write it from the project's own `make check`, not from a template |
| The default branch cannot take a red merge | ② | `gh api` where authorized |

CI does not gate readiness to deploy. Offer it; build it if the human wants it.

---

## How to use this in the report

Every item ends in exactly one of three states, and the state is what the record and the runbook are
built from:

- **✅ done / verified** — with what proves it (a command's output, the smoke test, a value read back
  from the platform).
- **🔧 your turn** — group ③ and anything blocked on it: what, why, where, and what to bring back.
- **❓ open** — what cannot be seen from here. Say so plainly; an unverifiable item silently marked
  green is how a product ships pointing at the test database.
