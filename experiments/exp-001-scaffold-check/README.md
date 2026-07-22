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
| 1 | All contract paths present | Repo at current HEAD | Exit 0, every path `OK` | see Results | see Results |
| 2 | Missing path detected | Non-existent root passed to checker | Every path reported missing | see Results | see Results |
| 3 | Experiment's own folder present | Repo at current HEAD | `experiments/` non-empty | see Results | see Results |

How tests were run:

```bash
python experiments/exp-001-scaffold-check/tests/test_structure.py
```

## Results
Filled in after the run — see the Results section update below.

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| | | | |

## Lessons learned
Filled in after the run.

## Reusable outputs
| Output | Type | Destination |
|---|---|---|
| | pattern / prompt / snippet / tool note | `knowledge/.../<file>.md` |

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
