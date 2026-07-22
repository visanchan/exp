# Capability Router

Use this reference when a class request spans several kinds of work. Select only the smallest relevant route; do not invoke every capability for every task.

## Repository and engineering work

| Need | Working method | Expected evidence |
|---|---|---|
| Understand an unfamiliar repository | Map locally, read instructions and entry points, separate code/data/docs/generated output, report risks before improvements | File inventory, Git status, important paths, concrete next action |
| Build or change code | Clarify success criteria, make a surgical implementation, preserve existing behavior, keep dependencies light | Focused diff, run command, tests, limitations |
| Diagnose a bug | Reproduce, trace the failing path, falsify competing hypotheses, minimize the case, fix the root cause | Reproduction, cause/mechanism, regression test |
| Test-driven work | Write a failing test, implement the smallest passing change, refactor only after green | Red/green evidence and final suite result |
| Review or improve architecture | Question whether the change is needed, inspect domain boundaries, find the simplest durable structure | Findings ordered by risk, proposed boundary, validation plan |
| Preserve a finished session | Record decisions and evidence, extract transferable knowledge, provide a compact handoff | Standalone lesson, links to preserved files, next owner/action |

Related source capability families: safe repo mapping, software engineering, surgical coding, disciplined diagnosis, TDD, scrutiny, architecture review, continuous improvement, handoff, and post-mortem writing.

## Business, product, and operations work

| Need | Working method | Expected evidence |
|---|---|---|
| Improve a real workflow | Map current people, channels, inputs, handoffs, exceptions, and review points before automating | Current-state flow, bottleneck, low-cost next move |
| Decide what to build | Define user/job, outcome, constraints, options, and measurable acceptance criteria | Prioritized requirements and explicit tradeoffs |
| Compare opportunities | Use value, effort, confidence, risk, and reversibility; show assumptions | Decision table and recommendation |
| Understand customers | Separate functional, emotional, and social jobs; identify trigger and current alternative | Interview questions, evidence, unmet job |
| Size a market | Triangulate top-down, bottom-up, and value-based estimates | Assumptions, ranges, sensitivity, sources |
| Model a business | Make drivers explicit; separate inputs, calculations, scenarios, and outputs | Auditable model, base/upside/downside cases |
| Plan inventory | Classify demand pattern, quantify lead time and uncertainty, preserve human override | Forecast logic, reorder point, safety stock, exceptions |
| Design KPIs | Tie each measure to a decision, owner, frequency, target, and source | Small metric hierarchy, not a crowded dashboard |
| Communicate analysis | Separate observation from interpretation and recommendation; lead with the decision | Concise narrative with evidence and action |

Related source capability families: practical business operations, product management, jobs-to-be-done, market sizing, startup finance, inventory planning, KPI design, data storytelling, management communication, and Thai-market localization.

## Data and spreadsheet work

1. Explain what the dataset appears to contain.
2. Check missing values, duplicates, inconsistent types or formats, key integrity, units, dates, and suspicious outliers.
3. Preserve raw inputs; transform into a separate working or output layer.
4. Separate observations from recommendations.
5. Prioritize actions as high, medium, or low.
6. Connect findings to revenue, margin, cost, demand, customer behavior, or operating efficiency.
7. For workbooks, keep inputs, calculations, and outputs visibly separate and verify formulas plus exports.

Expected outputs include validated CSV files, Excel-compatible workbooks, reconciliation reports, charts that support a decision, and reproducible scripts.

## UI, web, and prototype work

| Need | Working method | Expected evidence |
|---|---|---|
| Internal tool | Optimize speed, clarity, low training, validation, human review, and printable/exportable output | Runnable workflow and task-based test |
| Interface design | Establish hierarchy, states, actions, keyboard behavior, responsive layout, and accessibility | Screen/state inventory and visual validation |
| Prototype | Build only enough to test the risky assumption; label disposable shortcuts | Runnable prototype and learning result |
| Accessibility fix | Check semantics, labels, keyboard path, focus, contrast, errors, and reduced motion | Before/after behavior and targeted checks |
| Web quality audit | Review performance, accessibility, SEO where relevant, and basic reliability | Findings ordered by impact and practical fixes |

Related source capability families: interface design, frontend engineering, UX/UI, accessibility, baseline UI quality, interaction polish, prototyping, web auditing, directory/gallery apps, and static website setup.

## Documents, presentations, and visual artifacts

| Artifact | Default standard |
|---|---|
| Document | Logical structure, concise business language, consistent formatting, rendered verification |
| Presentation | One decision or message per slide, evidence-led story, readable visuals, presentation-ready flow |
| PDF | Inspect or render pages where layout matters; verify final appearance |
| Visualization | Use only when relationships become materially clearer than prose or a small table |
| HTML decision workbook | One standalone file, clear questions, local saving/export where useful, explicit approval gate |

Related source capability families: documents, presentations, PDFs, spreadsheets, visualization, data storytelling, and HTML thinking workbooks.

## AI workflow and reusable knowledge

- Use structured decomposition when the task is complex, but keep the delivered artifact simple.
- Ask one question at a time when discovery is explicitly requested.
- Turn a mature conversation into a PRD, issue set, handoff, post-mortem, reusable pattern, or skill only when the user requests that artifact.
- Keep user-level behavior separate from project-specific truth.
- Treat external tools and plugins as optional enhancements, never hidden requirements for a clone.

Related source capability families: structured thinking, discovery interviews, PRDs, issue decomposition, skill creation, knowledge graphs, handoffs, and reusable artifact templates.
