# Experiment README Template

> Copy this file into `experiments/exp-NNN-short-description/README.md` and fill
> it in. Delete this quote block and any section that genuinely does not apply.
> Fill Objective, Hypothesis, and Success criteria **before** writing code.

---

# exp-NNN — <Title>

## Experiment ID
`exp-NNN-short-description`

## Title
<One-line name of the experiment.>

## Date
Started: YYYY-MM-DD
Completed: YYYY-MM-DD

## Class topic
<Which class, module, lecture, or assignment this belongs to.>

## Objective
<What this experiment is trying to find out or build, in 1–3 sentences.>

## Hypothesis
<What you expect to happen, and why. Written before building. Being wrong here
is a useful result — do not edit it afterwards to match reality.>

## Success criteria
<Concrete, checkable conditions. Decided up front.>

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technology stack
| Component | Choice | Version | Why |
|---|---|---|---|
| Language | | | |
| Framework | | | |
| Model / API | | | |
| Other | | | |

Dependencies added beyond the standard library, and why each was necessary:

- `package` — reason

## Setup instructions
Prerequisites:

```text
<runtime + version, accounts, access needed>
```

Steps:

```bash
# 1. install
# 2. configure — copy ../../.env.example to .env and fill in values
# 3. run
```

Environment variables required (names only — never values):

- `VAR_NAME` — what it is for

## Implementation summary
<What was actually built. Key files, key decisions, how the pieces fit. Note
anywhere the implementation diverged from the original plan and why.>

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

How tests were run:

```bash
<command>
```

## Results
<What happened, measured against the success criteria. Include numbers where
they exist. State plainly whether the hypothesis held.>

- Criterion 1 — met / not met, evidence
- Criterion 2 — met / not met, evidence

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| | | | |

## Lessons learned
<The transferable takeaways. If substantial, write a full document from
`../../templates/lessons-learned-template.md` into
`../../knowledge/lessons-learned/` and link it here.>

- Lesson 1
- Lesson 2

Full write-up: `knowledge/lessons-learned/<file>.md`

## Reusable outputs
What was extracted, and where it went:

| Output | Type | Destination |
|---|---|---|
| | pattern / prompt / snippet / tool note | `knowledge/.../<file>.md` |

## Security considerations
- Secrets used: <names only>
- Secrets committed: **No** (confirm before completing)
- Sensitive or personal data handled: <none / describe>
- Artifacts redacted before saving: yes / no / n/a
- Third-party services data was sent to: <list>
- Residual risk / cleanup needed: <e.g. rotate a key, delete a test project>

## Cleanup decision
- Proposed: keep / delete / partially keep
- Reasoning:
- Keep list:
- Delete list:
- Approved by: <name> on YYYY-MM-DD
- Executed on: YYYY-MM-DD
- Checklist completed: `templates/cleanup-checklist.md` — yes / no

## Final status
`Planned` | `Active` | `Complete` | `Abandoned` | `Archived` | `Removed`

Index updated in `archive/experiment-index.md`: yes / no
