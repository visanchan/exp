# Lessons Learned — exp-002 Insight Observer

## Experiment reference
- Experiment ID: `exp-002-insight-observer`
- Original location: `experiments/exp-002-insight-observer/`
- Date: 2026-07-22
- Class topic: unrecorded — see below
- Index row: `archive/experiment-index.md`

## What was attempted

Unknown, and that is the finding.

The folder contains an empty `src/`, an empty `public/`, and 59 MB of installed
JavaScript packages (Vite, oxlint, rolldown). There is no README, no
`package.json`, and no source file. Nothing was ever committed — the folder has
no git history at all. Filesystem timestamps show it was created at 18:34 and
last touched at 18:37 on 2026-07-22.

A frontend scaffold was started, the dependency install completed, and the work
stopped three minutes later. The name suggests an "insight observer" of some
kind; nothing in the folder says what that meant.

## What worked

Nothing to report. No code ran.

## What failed

- **The experiment was never defined.** The repository's lifecycle requires a
  README with objective, hypothesis, and success criteria *before* any source or
  tooling. Here, `npm install` ran first, and the definition never followed.
- **It left 59 MB of dependencies behind for zero source files** — the tooling
  cost was paid in full and none of the value was.
- **It became invisible.** With no commit and no index row, the folder existed
  on disk and nowhere in the project's record. It was found only during an
  unrelated cleanup of another experiment, a day later.

## Root causes

| Failure | Symptom | Root cause | How it was found |
|---|---|---|---|
| No record of intent | A named folder nobody can explain | Scaffolding is fast and satisfying; writing the objective is neither, so the order gets inverted | Pre-deletion inventory of a different experiment |
| Invisible to the project | Absent from the index and from git | Nothing forces an index row at folder-creation time | Comparing `experiments/` against the index |

## Reusable patterns

None from the work. The relevant pattern already exists and is precisely what
would have prevented this:

| Pattern | When to use it | Where it lives |
|---|---|---|
| Define-before-code as a commit boundary | Starting any experiment | `knowledge/reusable-patterns/define-before-code-commit.md` |

## Anti-patterns

| Anti-pattern | Why it fails | Warning sign | Do instead |
|---|---|---|---|
| Scaffolding before defining | Produces tooling with nothing to apply it to; the abandoned result carries no information about what was intended | Running an installer as the first action in a new experiment | Write the README and commit it first — one commit, no source files |
| A folder with no index row | The project's own record disagrees with its filesystem; work becomes undiscoverable | `ls experiments/` and the index return different lists | Add the `Active` row in the same commit that creates the folder |

## Transfer opportunities

- Any project with a "start here" template: the cheap enforcement is making the
  definition its own commit, so the ordering is visible in `git log` rather than
  relying on discipline.
- Periodically diffing a directory listing against whatever index claims to
  describe it — the two drifting apart is how work goes missing.

## Recommended next step

- **Next step:** done — the folder was deleted on 2026-07-23 after this document
  was written. It held no source, no notes, and no history; the 57 MB of
  `node_modules` was the only thing lost, and that is regenerable by definition.
- **Rationale:** keeping it preserved nothing. This document is the part worth
  keeping, and it does not depend on the folder existing.
- **Follow-up experiment:** none. If the "insight observer" idea is revived, it
  starts fresh with a definition first.
