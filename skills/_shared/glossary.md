# Glossary — how the workflow vocabulary is rendered in the user's language

Shared by every skill and agent in this set. The cardinal rule (`skills/CLAUDE.md`) says: respond in
the language the user addressed you in. This file says **which words to translate and which to keep**,
so the same concept doesn't come out as three different words across a pipeline.

The table below is written for **Russian**, the case where a careless rendering hurts most
(transliterated verbs like *«отскаффолжен»*, *«зафайлить»*, *«элиситация»* read as broken speech).
For any other language the principle is the same: translate the workflow prose, keep the technical
names.

## Never translated, in any language

Code, identifiers, file and directory paths, commands, flags, env vars, API and product names — and,
critically, **the structural anchors of this skill set**: document section headings from the
`references/*.md` templates (`## Sources`, `## Forks / Decisions log`, `## Acceptance criteria`),
task fields and their values (`type: rework`, `status: done`, `review: auto`), config keys
(`mode: interactive`, `mode: autopilot`), skill and agent names. Skills locate these by exact string;
translating one breaks the pipeline. Prose *about* an anchor follows the user's language — the anchor
itself stays verbatim.

This governs **new** names too: identifiers you author — variables, functions, classes, fixtures,
parameters, test-function names — are written in **Latin script**, whatever language the conversation
is in. The user's language belongs in comments, docstrings and human-visible strings, never in a name.

**Anything a tool turns into a path is a name, not prose.** That includes the title string of a test
(`test('...')`, `it('...')`, `describe('...')`), snapshot names, fixture and artefact filenames, and
task-file slugs — all **Latin script, whatever language the conversation is in**. This is not
pedantry: Playwright and most runners derive an output directory from the test title, so a Russian
title becomes a Cyrillic path under `test-results/`, which then has to be quoted, matched and read
back by shell commands — and that combination has already produced both `ENAMETOOLONG` failures and a
run whose own evidence the agent could not open. A test title also has to stay stable across the
project's lifetime; a translated one silently changes identity the moment someone answers in another
language.

Write the criterion the test proves in a **comment or docstring above it** in the user's language if
that helps a person read it; keep the title itself a stable Latin identifier
(`test('criterion 3: an empty project shows no count')`). Do not mix the two conventions inside one
suite — half-Russian, half-English test titles in the same directory is the state this rule exists to
prevent.

## Kept in Latin script (Russian output)

`fork` · `commit` · `backlog` · `mockup` · `deploy` · `checklist` · `baseline` · `harness` ·
`onboarding` · `sanity check`

Write them in Latin script, **uninflected**, and let a Russian carrier word take the grammar:
«отметь fork в журнале», «два fork без ответа», «зафиксируй одним commit», «добавь в backlog»,
«пройди по checklist», «запусти deploy», «замерь baseline».

**No hybrid verbs** — never «закоммитить», «задеплоить», «отскаффолдить», «зафайлить», «драйвить»,
«прувить». Use a Russian verb plus the term: «сделать commit», «выполнить deploy», «завести задачу».

## Established loanwords — use the usual Cyrillic form

репозиторий · релиз · рефакторинг · аудит · линтер · хук · токен · промпт · стек · миграция · кэш ·
эндпоинт · дашборд · логи · автопилот · вердикт · регрессия · секреты · бюджет · `CI` · `MCP` ·
`staging` / `production` (environment names stay Latin).

## Translated (Russian output)

| English | Russian | Never |
|---|---|---|
| scaffold, scaffolding | создать каркас проекта, заготовка; «каркас репозитория ещё не создан» | «отскаффолжен», «скаффолдинг» |
| findings | замечания; в аудите — выявленные проблемы | «финдинги» |
| rework | доработка (задача-доработка) | «реворк» |
| elicit, elicitation | опрос, выявление требований; стадия Elicit — «Опрос» | «элиситация» |
| intake | первичный опрос; intake interview — вводное интервью | «интейк» |
| gate, hard gate | контрольная точка, обязательная остановка | «гейт», «хард-гейт» |
| quality gate | порог качества | «квалити-гейт» |
| seed, seeded, seed data | начальные данные, наполнить начальными данными | «сид», «засидить» |
| handoff | передача (следующему этапу) | «хендофф» |
| tooling | инструменты, оснастка | «тулинг» |
| runbook | регламент эксплуатации, инструкция дежурного | «ранбук» |
| smoke test | базовая проверка запуска, проверка на живость | «смоук-тест» |
| seam (testing seam) | точка подмены в коде, стык | «сим» |
| stub | заглушка | «стаб» |
| throwaway | черновой, одноразовый | — |
| rubric | шкала оценки, критерии оценки | «рубрика» (false friend) |
| claim | утверждение | «клейм» |
| surface (verb / noun) | выявить, вынести наружу / экран, раздел интерфейса | «серфейс» |
| commit (the non-git sense) | обязательство, зафиксироваться на решении | — |
| amend | дополнить commit; о плане — внести правку | «эмендить» |
| brief | вводная, краткое задание | «бриф» |
| drive (the app, a flow) | прогнать сценарий, поработать с приложением как пользователь | «драйвить» |
| prove | доказать, подтвердить | «прувить» |
| file (a task, a finding) | завести задачу, оформить замечание | «зафайлить» |
| draft | черновик | «драфт» |
| spec, specification | спецификация | «спека» |
| pipeline | конвейер, цепочка этапов | «пайплайн» |
| feature | функция, возможность | «фича» |
| blocker | блокирующая проблема | «блокер» |
| scope | границы работ, охват | «скоуп» |
| gap | пробел, нехватка | «гэп» |
| rollback | откат | «роллбэк» |
| coverage | покрытие тестами | «каверидж» |
| fixture | подготовленные данные | «фикстура» |
| hardcode | зашить в код, прописать жёстко | «захардкодить» |
| trade-off | компромисс, размен | «трейд-офф» |
| spike | разведочная задача | «спайк» |
| polish | доводка | «полишинг» |

## When a term isn't listed

Prefer the Russian word if a natural one exists; keep the English term only when the Russian
equivalent would be ambiguous or unheard-of in the trade. Whatever you choose, **stay consistent for
the whole run** — one concept, one word.
