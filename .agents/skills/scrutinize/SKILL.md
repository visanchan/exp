---
name: scrutinize
description: Outsider-perspective end-to-end review of a plan, PR, or code change. First questions intent and whether a simpler approach would achieve the same goal, then traces the actual code path — not just the diff — to verify the change does what it claims. Use when asked to review, audit, sanity-check, or give a second opinion on a plan, PR, diff, design doc, or proposed change; when deciding whether an approach is right before committing to it; or when something works but feels more complicated than it should.
---

# Scrutinize

Stand outside the change and ask whether it should exist at all, then verify it
actually does what it claims end-to-end.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

**Related but different:** `reviewing-ai-written-code` is about the defects
*generated* code specifically produces — invented APIs, silent scope creep,
tautological tests, fabricated self-reports. Use that one when checking a patch
an agent just wrote. Use **this** one to question whether the change should
exist in that shape at all, and to verify behaviour by tracing real code paths.
On an agent-written change that matters, both apply — run this one first, since
"this shouldn't exist" makes the defect hunt moot.

## Operating stance

- **Outsider.** Forget who wrote it and why they think it is right. Read the
  artifact cold.
- **End-to-end, not diff-local.** The diff is the entry point, not the scope.
  Follow the call graph through real code paths.
- **Actionable, concise, with rationale.** Every finding states *what to change*,
  *why*, and *what evidence* led you there. No filler, no restating the diff.

## Workflow

Run these in order. Do not skip ahead.

### 1. Intent — what is this actually trying to do?

- State the goal in one sentence, in your own words. If you cannot, the artifact
  is underspecified — say so and stop.
- Ask: **is there a simpler, smaller, or more elegant way to achieve the same
  goal?** Consider:
  - Doing nothing — is the problem real and load-bearing?
  - Using something that already exists instead of adding new surface.
  - A smaller change that solves 90% of the goal with 10% of the risk.
  - Solving it at a different layer — config vs code, framework vs app, build vs
    runtime.
- If a better alternative exists, name it explicitly with rationale. **This is
  the most valuable thing you can output** — surface it before the line-by-line
  review.

### 2. Trace — walk the actual code path

- For each behaviour the change claims, trace the path end-to-end through the
  real code, not just the lines in the diff:
  entry point → call sites → branches taken → state mutated → exit / return /
  side effect.
- Include the unchanged code on either side of the diff. **Bugs hide at the
  seams.**
- For a plan or design doc: trace the proposed flow against the existing system.
  Where does it touch reality? What does it assume that is not true?
- Note every place the trace surprises you — an unexpected branch, dead code
  reached, state you did not know existed. Surprises are signal.

### 3. Verify — does it actually do what it claims?

For each claim the change or plan makes:

- **Does the traced path actually produce that behaviour?** Walk it explicitly:
  *"It claims X. Path: A → B → C. At C, [observation]. Therefore [holds /
  does not hold]."*
- **What inputs or states would break it?** Edge cases, concurrent callers,
  error paths, partial failures, retries, empty / null / unicode / huge inputs,
  ordering assumptions.
- **What does it silently change?** Performance, error semantics, observability,
  the contract for other callers, on-disk or on-wire format.
- **How is it tested?** Do the tests exercise the traced path, or pass while
  skipping it — mocks that hide the bug, asserts on intermediate state, happy
  path only?

### 4. Report

One tight section per finding, ordered by severity (blocker → major → nit):

- **Finding** — one sentence, specific. Cite `file:line` where applicable.
- **Why it matters** — the consequence, not the principle.
- **Evidence** — the trace step or input that exposes it.
- **Suggested change** — concrete, minimal.

Close with a one-line verdict: **ship / fix-then-ship / rework / reject** — with
the single biggest reason.

## Operating rules

- **No rubber-stamps.** "LGTM" is not an output. If you genuinely find nothing,
  say what you traced and what you checked, so the reader can judge whether the
  review covered the surface they cared about.
- **Cite or it did not happen.** Every claim about the code references a
  specific path, file, or line. No vague "this might break under load".
- **Distinguish claim from verification.** "The PR says X" and "I traced X and
  confirmed it" are different things — keep them separate in the output.
- **The simpler-alternative pass is mandatory.** Even on small changes, spend one
  breath asking whether the whole thing is necessary. Skip only if the person
  explicitly says not to question scope.
- **Do not pad with style nits when there is a structural problem.** If step 1 or
  2 surfaces a real issue, lead with it; defer the nits or drop them.
- **No flattery, no hedging.** "This is a great PR, but…" adds nothing. State the
  finding.

## Scrutinising your own plan

The same workflow works before you build, and it is cheaper there. Run step 1
against your own approach before writing code:

- Say the goal in one sentence. If it takes three, the plan is not ready.
- Name the simpler alternative you rejected, and why. If you cannot name one,
  you have not looked.
- Say which assumption, if wrong, breaks the whole plan. Then check that one
  first.

Ten minutes here routinely saves a day of building the wrong thing well.
