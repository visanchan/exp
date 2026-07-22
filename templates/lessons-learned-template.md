# Lessons-Learned Template

> Copy into `knowledge/lessons-learned/exp-NNN-short-description.md` and fill in.
> Delete this quote block.
>
> This document outlives the code. Write it so it is useful to someone who will
> never see the implementation — including yourself, months from now.

---

# Lessons Learned — exp-NNN <Title>

## Experiment reference
- Experiment ID: `exp-NNN-short-description`
- Original location: `experiments/exp-NNN-short-description/` (may be deleted)
- Date: YYYY-MM-DD
- Class topic:
- Index row: `archive/experiment-index.md`

## What was attempted
<The goal and the approach taken, in a few sentences. Enough context that this
document stands alone without the code.>

## What worked
<Concrete things that succeeded. Be specific — "X worked" is not useful; "X
worked because Y" is.>

- 
- 

## What failed
<Concrete failures, dead ends, and wasted effort. This is the most valuable
section — record it honestly.>

- 
- 

## Root causes
<Why the failures happened. Push past the symptom to the actual cause.>

| Failure | Symptom | Root cause | How it was found |
|---|---|---|---|
| | | | |

## Reusable patterns
<Approaches worth repeating. Link to anything extracted into
`knowledge/reusable-patterns/` or `knowledge/code-snippets/`.>

| Pattern | When to use it | Where it lives |
|---|---|---|
| | | `knowledge/reusable-patterns/<file>.md` |

## Anti-patterns
<Approaches to avoid, and the cost of each. Name the trap and the tell that
warns you it is happening.>

| Anti-pattern | Why it fails | Warning sign | Do instead |
|---|---|---|---|
| | | | |

## Useful prompts
<Prompts that produced good results, with enough context to reuse them. Move the
strongest into `knowledge/prompt-library/` and link them.>

```text
<prompt text>
```

- Why it worked:
- Model / tool used:
- Saved to: `knowledge/prompt-library/<file>.md`

## Transfer opportunities
<Where else this knowledge applies — other classes, other projects, future
experiments, production work.>

- 
- 

## Recommended next step
<The single most useful thing to do next, and why. If nothing — say the line of
inquiry is closed and why.>

- Next step:
- Rationale:
- Follow-up experiment: `exp-NNN-...` / none
