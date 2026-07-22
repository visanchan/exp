# Lessons Learned — exp-001 Scaffold Check

## Experiment reference
- Experiment ID: `exp-001-scaffold-check`
- Original location: `experiments/exp-001-scaffold-check/` (deleted)
- Date: 2026-07-22
- Class topic: Repository setup — a process rehearsal, not an assignment
- Index row: `archive/experiment-index.md`

## What was attempted
Run this repository's own seven-step experiment lifecycle end to end on a
deliberately trivial subject, to find gaps in the templates, the index, and the
cleanup gate before a graded assignment depends on them. The implementation was a
Python script that turns the structure contract in `README.md` into a checkable
list of paths, plus a runner that prints a table and sets an exit code.

## What worked

- **Committing the define step separately.** The experiment README — objective,
  hypothesis, success criteria — and the `Active` index row went in as one commit
  before `src/` existed. This converted "fill the README before writing code" from
  an honour-system rule into something visible in `git log`. It is the single most
  useful thing this experiment produced.
- **Testing the negative case.** Case 2 ran the checker against a non-existent
  directory and confirmed it reported all 16 paths missing. Without it, case 1's
  16/16 green would have proved only that the checker returns something.
- **Splitting pure check from exit code.** `check_structure.py` returns data and
  never prints or exits; `test_structure.py` owns process semantics. The pure half
  was reusable as a snippet with no edits; a single script would have needed
  rewriting to extract.
- **The templates absorbed a near-empty experiment.** `—` in `Main Lesson` and
  `Preserved Artifacts` reads fine for an `Active` row. No template edits needed.

## What failed

- **PowerShell here-string syntax used in the Bash tool.** `git commit -m @'...'@`
  did not error — Bash treated `@'` as literal text, so the commit landed with the
  subject line `@` and the real message pushed into the body. Caught only by
  reading `git log` afterwards. Required an amend.
- **Default branch set after the first push.** The remote was created with
  `master`. Renaming locally to `main` and pushing left `origin/master` behind as a
  stale branch that still has to be cleaned up manually.
- **The hypothesis looked in the wrong place.** It predicted friction in the
  cleanup checklist and the index row format. Neither caused trouble. The actual
  gap was that the lifecycle in `README.md` describes an order of steps but names
  no checkpoint that enforces it.

## Root causes

| Failure | Symptom | Root cause | How it was found |
|---|---|---|---|
| Corrupted commit message | Commit subject was `@` | Shell-specific syntax used in the wrong shell; Bash treats PowerShell here-strings as literal text rather than erroring | Reading `git log --oneline` after committing |
| Stale `origin/master` | Two branches on the remote, one abandoned | Repo created and pushed before the branch-naming decision was made | `git branch -r` during remote reconciliation |
| Unenforced "define before code" | Nothing would have caught writing `src/` first | Process documented as prose with no artifact boundary attached to it | Noticed while deciding where to place commits |

## Reusable patterns

| Pattern | When to use it | Where it lives |
|---|---|---|
| Define-before-code as a commit boundary | Any experiment where the objective must be fixed before results can bias it | `knowledge/reusable-patterns/define-before-code-commit.md` |
| Pure check + thin exit-code runner | Any validation script that might later be imported or reused | `knowledge/code-snippets/repo-structure-check.md` |

## Anti-patterns

| Anti-pattern | Why it fails | Warning sign | Do instead |
|---|---|---|---|
| Assertion-free structure check | A check that cannot fail proves nothing; it reports green regardless | No test exercises the failure path | Run the checker against a path you know is missing and assert it complains |
| Mixing shell dialects in one session | Wrong-dialect syntax often parses as literal text instead of erroring, so corruption is silent | Output looks odd but exit code is 0 | Match syntax to the tool executing it; verify commit messages with `git log` |
| Editing the hypothesis to match the result | Destroys the only evidence of what you actually expected | Hypothesis reads suspiciously accurate | Leave it wrong and write down where it was wrong — that is the finding |
| Renaming the default branch after first push | Leaves a stale remote branch and a mismatched default | `git branch -r` shows an abandoned branch | Decide the branch name before creating the remote |

## Useful prompts

Not applicable — no model calls were made in this experiment. Nothing worth
promoting to `knowledge/prompt-library/`.

## Transfer opportunities

- Every future experiment in this repository: commit the define step on its own.
- Any repository with a documented structure — the contract check turns README
  prose into something CI can run.
- Any Windows machine where both PowerShell and Bash are available: the
  mixed-dialect trap recurs, and it fails silently rather than loudly.

## Recommended next step

- Next step: Add the define-step commit convention to `AGENTS.md` §11, so the rule
  has a home in the file agents actually read rather than only in this document.
- Rationale: This experiment found exactly one process gap. Writing it into the
  agent rules is what converts the finding into behaviour; leaving it here means
  it gets rediscovered.
- Follow-up experiment: none. The line of inquiry is closed — the lifecycle works
  and the one gap is identified.
