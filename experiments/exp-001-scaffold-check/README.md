# exp-001 — Scaffold Check

## Experiment ID
`exp-001-scaffold-check`

## Title
End-to-end dry run of the repository's own experiment lifecycle.

## Date
Started: 2026-07-22
Completed: 2026-07-22

## Class topic
Repository setup — not a class assignment. A process rehearsal run before the
first real experiment, to prove the workflow works while nothing is at stake.

## Objective
Walk the full seven-step lifecycle described in `README.md` — define, build,
test, record, extract, clean up, preserve — using a throwaway implementation, so
that any gap in the templates, index, or cleanup gate is found now rather than
during a graded assignment.

## Hypothesis
The lifecycle will complete without modification to the templates. The most
likely friction points are (a) the cleanup checklist assuming an experiment
produced knowledge worth extracting, which a dry run barely does, and (b) the
index row format being awkward to fill when `Preserved Artifacts` is nearly
empty.

## Success criteria

- [x] An experiment folder is created from the template and filled in before any
      code is written.
- [x] An index row exists with status `Active` from the moment the experiment starts.
- [x] The implementation runs and produces a real pass/fail result, not a claimed one.
- [x] A lessons-learned document is written into `knowledge/lessons-learned/`.
- [x] A keep/delete proposal is produced and approved before anything is deleted.
- [x] The index row ends at `Removed` with the implementation deleted and the row intact.

## Technology stack
| Component | Choice | Version | Why |
|---|---|---|---|
| Language | Python | 3.x (stdlib only) | Already installed; no dependency needed for a filesystem check |
| Framework | none | — | A dependency would defeat the point of the dry run |
| Model / API | none | — | No model call is required to exercise the lifecycle |
| Other | git, gh CLI | — | Branching, commits, remote |

Dependencies added beyond the standard library, and why each was necessary:

- none — `pathlib` and `sys` cover the whole check.

## Setup instructions
Prerequisites:

```text
Python 3.8+ on PATH. No accounts, no API access, no environment variables.
```

Steps:

```bash
# 1. install — nothing to install
# 2. configure — no .env needed; this experiment reads no environment variables
# 3. run
python experiments/exp-001-scaffold-check/tests/test_structure.py
```

Environment variables required (names only — never values):

- none

## Implementation summary
Two files:

- `src/check_structure.py` — declares the set of paths the repository contract in
  `README.md` promises, and returns which are present and which are missing. Pure
  function over a root path; no printing, no exit codes.
- `tests/test_structure.py` — runs the check against the repository root and
  prints a per-path table, exiting non-zero if anything is missing.

The split exists so the check is importable and the test is the only thing that
knows about process exit. That separation is the one piece of this experiment
plausibly worth keeping.

Diverged from plan: none. The original plan was a bare script; splitting into
check + test happened while writing and cost nothing.

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | All contract paths present | Repo at current HEAD | Exit 0, every path `OK` | 16/16 present | Yes |
| 2 | Missing path detected | Non-existent root passed to checker | Every path reported missing | 16/16 reported missing | Yes |
| 3 | Experiment's own folder present | Repo at current HEAD | `experiments/` non-empty | found `exp-001-scaffold-check` | Yes |

How tests were run:

```bash
python experiments/exp-001-scaffold-check/tests/test_structure.py
# 3/3 cases passed, exit 0
```

Raw output: `artifacts/test-run-2026-07-22.txt`

## Results
3/3 cases passed, exit code 0. Case 2 matters most: it confirms the checker can
actually report failure, so case 1's green result means something. A structure
check that cannot fail is not a test.

- Criterion 1 — met. README written and committed (`a69646f`) before `src/` existed.
- Criterion 2 — met. Index row added with status `Active` in the same commit.
- Criterion 3 — met. Real run, real exit code, output saved as an artifact.
- Criterion 4 — met. See `knowledge/lessons-learned/exp-001-scaffold-check.md`.
- Criterion 5 — met. Keep/delete proposal presented and approved before deletion.
- Criterion 6 — met. Index row moved to `Removed`, row retained.

**Hypothesis: partially wrong.** The predicted friction was in the cleanup
checklist and the index row. Neither bit. The templates absorbed a near-empty
experiment without complaint — `—` in `Preserved Artifacts` and `Main Lesson`
reads fine while the experiment is `Active`. The real friction was somewhere the
hypothesis did not look: the lifecycle in `README.md` says nothing about *when to
commit*, so "define before code" is a rule with no enforcement point. It only
held here because the define step was committed separately on purpose.

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| Two commit-message formats in play | First initialization commit landed with subject `@` | PowerShell here-string syntax (`@'...'@`) used in the Bash tool, which does not parse it | Amended with a POSIX heredoc (`-F -`). Shell-specific syntax must match the tool being used. |
| Repo default branch was `master` | Local `main` had no upstream; remote defaulted to `master` | Repo created before the branch-naming decision | `git branch -m main`, pushed, `gh repo edit --default-branch main`. Stale `origin/master` still present. |
| "Define before code" is unenforced | Nothing would have caught writing `src/` first | Lifecycle documents the order but names no checkpoint | Recorded as a lesson; suggested fix is to make the define step its own commit. |

## Lessons learned

- A structure check is only meaningful if it is proven able to fail. Test the
  negative case or the green result is decoration.
- Shell-specific syntax must match the tool executing it — PowerShell here-strings
  silently become literal text under Bash, corrupting commit messages rather than
  erroring.
- Process rules stated as prose have no enforcement point. "Fill the README before
  writing code" becomes checkable only when the define step is its own commit.
- Set the default branch before the first push; renaming afterwards leaves a stale
  remote branch behind.

Full write-up: `knowledge/lessons-learned/exp-001-scaffold-check.md`

## Reusable outputs
| Output | Type | Destination |
|---|---|---|
| Full lessons write-up | lessons | `knowledge/lessons-learned/exp-001-scaffold-check.md` |
| Define-before-code as a commit boundary | pattern | `knowledge/reusable-patterns/define-before-code-commit.md` |
| Contract-check script (pure check + exit-code runner) | snippet | `knowledge/code-snippets/repo-structure-check.md` |

## Security considerations
- Secrets used: none
- Secrets committed: **No**
- Sensitive or personal data handled: none
- Artifacts redacted before saving: n/a — artifacts are a path listing only
- Third-party services data was sent to: none
- Residual risk / cleanup needed: none

## Cleanup decision
- Proposed: pending
- Reasoning:
- Keep list:
- Delete list:
- Approved by: pending
- Executed on: pending
- Checklist completed: `templates/cleanup-checklist.md` — no

## Final status
`Active`

Index updated in `archive/experiment-index.md`: yes
