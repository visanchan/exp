---
name: systematic-debugging
description: Find the actual cause of a bug instead of guessing at fixes. Use when something throws, returns the wrong value, works locally but not elsewhere, broke after a change, or fails intermittently — and especially when two or three attempted fixes have already failed. Covers reproducing reliably, shrinking the failure, forming and falsifying hypotheses, and proving the fix.
---

# Systematic Debugging

The failure mode this prevents: changing things until the symptom disappears.
That produces code nobody understands, fixes that mask the cause, and bugs that
return in a different shape. Debugging is an investigation with a verdict, not a
sequence of edits.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## Before touching any code

Write down two sentences:

1. **What I expected to happen.**
2. **What actually happened**, quoted exactly — the real error text, the real
   wrong value, not a paraphrase.

If you cannot fill both in, you are not ready to debug. "It doesn't work" is not
a symptom; it is the absence of one.

## The loop

### 1. Reproduce it on demand

A bug you cannot trigger is a bug you cannot fix or verify. Find the exact
sequence that produces it, every time, and write it down.

If it only happens *sometimes*, that is information — it points at time,
ordering, concurrency, caching, network, or leftover state. Note what differs
between the runs that fail and the runs that don't.

If it only happens in one environment, list what differs: versions, environment
variables, file paths, permissions, data.

**Do not skip this to save time.** Without reproduction you cannot tell a fix
from a coincidence.

### 2. Shrink it

Cut the failing case down until nothing can be removed without the bug
disappearing. Delete inputs, remove steps, replace dependencies with constants,
comment out layers.

Most bugs become obvious at this step, and a small reproduction is also the
test you will write later. Aim for something that fits on a screen.

### 3. Read the error properly

Stack traces are usually skimmed. Read them:

- **The top frame** is where it surfaced, which is often *not* where it broke.
- **The first frame in your own code** is normally the real starting point.
- **The exact wording** matters. `undefined is not a function` and
  `cannot read property of undefined` are different bugs.
- **Search the exact string** before theorising.

### 4. Form one hypothesis and try to kill it

State it precisely enough to be wrong:

> *"`total` is `NaN` because `price` arrives as a string and `+` concatenates."*

Not: *"something's wrong with the total."*

Then **look for evidence that it is false**, not evidence that it is true. Print
the value. Check the type. Assert the assumption. Confirmation bias is the main
reason debugging sessions run long — a hypothesis you only tried to confirm will
survive far past its usefulness.

If the hypothesis is wrong, that is progress. Write down what it ruled out.

### 5. Bisect when you have no hypothesis

If nothing suggests itself, stop thinking and start halving.

- **In time:** was it working before? `git bisect`, or check out an older commit
  and walk forward. The commit that introduces the failure usually names the
  cause.
- **In space:** disable half the code path. Whichever half still fails contains
  it. Repeat.

Ten minutes of bisection beats an hour of staring.

### 6. Fix the cause, not the symptom

Before you commit, answer: **why did this happen?**

If the answer is "the value was null so I added a null check", ask why it was
null. A guard that hides an upstream bug will be paid for later, with interest.

Legitimate fixes: correct the wrong logic, fix the bad input at its source, fix
the wrong assumption. A defensive check is legitimate only when the null is a
genuinely valid state.

### 7. Prove it

- The original reproduction now passes.
- **Write a test that fails without the fix and passes with it.** If you cannot
  write one, you probably do not understand the bug yet.
- Nothing else broke — run the wider suite.
- Say what you actually ran and what it returned. "Should be fixed" is not a
  result.

## When you are stuck

- **Explain it out loud**, to a person or to nothing. Articulating it exposes the
  assumption you skipped.
- **Re-read your two sentences.** People routinely spend an hour debugging the
  wrong symptom.
- **Question the assumption you have not tested** — the one so obvious you never
  checked it. It is usually there.
- **Check the boring causes**: stale cache, wrong file, wrong branch, wrong
  environment, server not restarted, editor not saved.
- **Take a break.** Diminishing returns are real and arrive faster than expected.

## Working with an AI agent

- Give it the **exact** error and the reproduction, not a summary.
- Ask it to explain the cause **before** it proposes a patch. A fix without an
  explanation is a guess wearing a diff.
- Be suspicious of a fix that changes a lot for a small symptom.
- Verify the fix yourself. An agent will often report success on the strength of
  having made an edit; that is not evidence.
- If two agent fixes in a row miss, stop and go back to step 1 — the shared
  understanding of the symptom is probably wrong.

## Do not

- Do not change several things at once. You will not know which one mattered.
- Do not "fix" a bug you cannot reproduce; you cannot know you fixed it.
- Do not delete the failing test to make the suite pass.
- Do not leave debugging output behind — remove it or convert it to real logging.
- Do not claim a fix works without running the thing.
