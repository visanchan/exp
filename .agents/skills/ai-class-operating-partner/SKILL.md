---
name: ai-class-operating-partner
description: Run practical AI-class work in this repository from problem framing through a tested artifact and preserved learning. Use for class experiments, prototypes, coding, debugging, business or data analysis, spreadsheets, documents, presentations, UI work, experiment cleanup, and requests that should combine reusable methods from multiple skill areas without depending on the repository owner's private machine or projects.
---

# AI Class Operating Partner

Turn class requests into simple, useful, evidence-backed outputs while preserving what future students can reuse.

## Establish repository truth

Read these files before acting:

1. `../../../AGENTS.md` for mandatory boundaries.
2. `../../../README.md` for the experiment lifecycle.
3. `../../../archive/experiment-index.md` for the next experiment number and current status.
4. The target experiment's `README.md`, when one exists.

Treat `AGENTS.md` as authoritative if this skill and repository policy ever differ.

## Classify the request

- For an explanation, review, or status question, inspect the relevant files and answer without creating an experiment.
- For code, a prototype, data analysis, or another generated artifact, create or continue one isolated experiment.
- For a repository-wide process improvement, record the decision in `docs/decisions/`; do not disguise it as experiment output.
- For cleanup, preserve knowledge and prepare a keep/delete proposal before deleting anything.

If the task crosses several disciplines, read `references/capability-router.md`. Read `references/output-standards.md` before producing a business, data, UI, spreadsheet, document, presentation, or handoff artifact. Read `references/provenance-and-scope.md` before expanding or redistributing this skill.

## Frame the outcome

State, in plain language:

1. Business or learning objective.
2. Expected practical benefit.
3. Simplest suitable approach.
4. Difficulty and cost or complexity tradeoff.
5. Evidence that will prove success.

Make reasonable, reversible assumptions and record important ones. Ask only when a missing decision would materially change the result or create risk.

## Define before code

For a new experiment:

1. Allocate the next `exp-NNN-short-description` ID from the permanent index.
2. Create the experiment folder and copy `templates/experiment-readme-template.md` to its `README.md`.
3. Fill Objective, Hypothesis, and measurable Success criteria.
4. Add an `Active` row to `archive/experiment-index.md`.
5. Make the definition its own commit before any source file exists, but only when the user has explicitly authorized committing.

If source work is requested without commit authorization, prepare the definition and explain that the separate definition commit is the required next gate. Do not backfill a hypothesis after observing results.

## Choose the lightest effective route

- Prefer HTML, CSS, JavaScript, Python standard library, CSV, and Excel-compatible files.
- Add a framework, package, database, hosted service, or paid tool only when its benefit clearly exceeds its setup and maintenance cost.
- Keep all experiment-specific dependencies, configuration, source, tests, notes, and artifacts inside that experiment.
- Preserve human review before consequential business submissions, pricing changes, customer communication, or destructive actions.

Use the decision table in `references/capability-router.md` to select a more specific workflow.

## Implement and validate

1. Inspect before editing and preserve unrelated work.
2. Make the smallest coherent change that satisfies the defined criteria.
3. Add validation and error handling where failure matters.
4. Exercise the real workflow, including at least one meaningful failure or edge case.
5. Record commands, cases, actual outcomes, and skipped checks in the experiment README.
6. Never call work verified when it was not run.

## Hand off the result

Lead with the outcome, then report:

- What changed and where.
- How to run or use it.
- What was tested and the actual result.
- Risks, assumptions, or limitations.
- The single best next improvement.

Connect technical results to revenue, margin, cost, demand, customer behavior, operational efficiency, or learning value when relevant.

## Preserve knowledge and clean up

At completion:

1. Finish the experiment README while evidence is fresh.
2. Extract durable lessons, patterns, prompts, snippets, and tool notes into `knowledge/`.
3. Update the permanent experiment index.
4. Use `templates/cleanup-checklist.md`.
5. Present explicit KEEP, DELETE, and UNCERTAIN lists.
6. Delete implementation only after explicit human approval.

Never delete `knowledge/`, `archive/`, `docs/`, `templates/`, or Git history.

## Protect portability

- Depend only on files committed in this repository unless the user explicitly approves an external dependency.
- Never assume the clone has the owner's user-level, system, plugin, or other project skills installed.
- Never copy credentials, personal paths, customer data, private company rules, or production configuration into this skill.
- Synthesize reusable methods; do not reproduce third-party or project-local skill text without permission and compatible licensing.
- Keep examples synthetic and safe to share with classmates.
