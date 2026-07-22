# Pattern — Define-Before-Code as a Commit Boundary

**Source:** `exp-001-scaffold-check` (2026-07-22)

## Problem

The experiment lifecycle says to fill in objective, hypothesis, and success
criteria *before* writing code. Stated as prose, this is an honour-system rule.
Nothing catches you writing `src/` first and back-filling the hypothesis to match
what you found — which is the exact failure the rule exists to prevent, and the
one that leaves no trace.

## Pattern

Make the define step its own commit, containing only:

- `experiments/exp-NNN-*/README.md` with Objective, Hypothesis, and Success
  criteria filled in.
- The `Active` row in `archive/experiment-index.md`.

No source files. Commit it before creating `src/`.

```bash
git checkout -b experiment/exp-NNN-short-description
mkdir -p experiments/exp-NNN-short-description/{src,tests,notes,artifacts}
cp templates/experiment-readme-template.md \
   experiments/exp-NNN-short-description/README.md
# fill in Objective / Hypothesis / Success criteria, add the index row
git add archive/experiment-index.md experiments/exp-NNN-short-description/README.md
git commit -m "chore: initialize experiment NNN"
# only now write code
```

## Why it works

The commit is a timestamp. `git log --diff-filter=A` shows the README landing
before the first source file, so the ordering is verifiable by anyone later —
including you, when you have forgotten. A hypothesis committed before results
exist cannot have been quietly adjusted to fit them; if it is edited afterwards,
the diff says so.

It also forces the objective to be written while it is still genuinely open. A
hypothesis written after the code runs is a description, not a prediction.

## When to use it

- Any experiment where the result could bias the stated objective.
- Any work where "what did I actually expect?" matters more than "did it pass?".
- Assignments where the reasoning is graded, not just the output.

## When not to

- Pure chores with no hypothesis (dependency bump, typo fix).
- Exploration so open-ended that no success criterion is honest yet — in that
  case write `Planned` in the index and define criteria once the question has a
  shape.

## Cost

One extra commit per experiment. That is the whole cost.

## Related

- [[exp-001-scaffold-check]] — where this came from
- `templates/experiment-readme-template.md` — the file the define commit contains
