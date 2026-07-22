---
name: debug-mantra
description: Four-mantra debugging discipline — reproduce, know the fail path, falsify the hypothesis, cross-reference every breadcrumb. Recite the mantra block verbatim at the start of any debugging session, then apply the four steps in order before proposing any fix. Use whenever debugging starts — something is broken, throwing or failing, a test passes locally and fails elsewhere, behaviour changed after an edit, a stack trace or error log is pasted, or two or three attempted fixes have already missed.
---

# Debug Mantra

Four-step discipline for any debug session. Recite verbatim, then apply in order.

The failure this prevents: changing things until the symptom disappears. That
produces code nobody understands, fixes that mask the cause, and bugs that
return in a different shape. Debugging is an investigation with a verdict, not a
sequence of edits.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## Recite this — verbatim, as the first thing in your first response

> **Mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it?
> 4. **Every run is a breadcrumb.** Cross-reference all of them.

Then begin work.

---

## 0. State the symptom before anything

Two sentences, written down:

1. **What was expected.**
2. **What actually happened** — quoted exactly. The real error text, the real
   wrong value, not a paraphrase.

If both cannot be filled in, you are not debugging yet. "It doesn't work" is the
absence of a symptom, not a symptom.

## 1. Reproduce reliably

Build a runnable repro before anything else.

- **Reliable repro** → capture the exact steps, inputs, and environment as a
  runnable artifact: failing test, curl script, CLI invocation, replay harness.
- **Flaky repro** → the bug is not yet debuggable. Raise the rate first: loop the
  trigger, parallelise, add stress, narrow timing windows, inject sleeps. 50%
  flake is debuggable; 1% is not.
- **No repro at all** → stop. Say so explicitly. Ask for env access, captured
  artifacts (HAR, log dump, core), or permission to instrument. Do **not**
  proceed to hypothesise.

Target: a fast (1–5 s), deterministic pass/fail signal. Pin time, seed the RNG,
freeze network, isolate filesystem.

Then **shrink it**. Cut the failing case down until nothing can be removed
without the bug disappearing — delete inputs, remove steps, replace dependencies
with constants. Most bugs become obvious here, and the shrunken case is the
regression test you will write in step 5.

## 2. Know the fail path

Once reproducible, find *where* the code breaks and *what stops it from
breaking*. The differential narrows the search. Try in this order — escalate
only when the prior tactic fails.

1. **Attach a debugger.** If the env supports it, attach and step to the failure
   site. One breakpoint beats ten logs. Do this **before** turning any knobs.
2. **Source trace + knob enumeration.** If no debugger (or it can't reach the
   bug), trace the code path end-to-end and list every knob that can influence
   the outcome:
   - config flags, env vars, feature toggles
   - branch conditions, input shape
   - timing, concurrency, build options

   Each knob is a candidate axis to flip in the differential. Flip one at a time.
3. **In-code instrumentation.** If outside knobs can't move the failure, go
   inside: `printf` / log statements at the suspected fail site, dump the
   relevant internal state. Tag every probe with a unique prefix (e.g.
   `[DBG-a4f2]`) so cleanup is a single grep. Let the trace show where reality
   diverges from your model.

**Read the stack trace properly** while you are here. The top frame is where it
surfaced, which is often not where it broke; the first frame in your own code is
usually the real starting point; and the exact wording matters —
`undefined is not a function` and `cannot read property of undefined` are
different bugs.

**When nothing suggests itself, bisect instead of staring.** In time: was it
working before? `git bisect`, or check out an older commit and walk forward —
the commit that introduces the failure usually names the cause. In space:
disable half the code path; whichever half still fails contains it; repeat. Ten
minutes of bisection beats an hour of theorising.

## 3. Falsify the hypothesis

When a candidate root cause surfaces, scrutinise it **before** testing it.

- Does it actually explain the symptom end-to-end? Walk it through.
- What is the simplest **proof**? What is the cleanest **disproof**?
- Run the **disproof first**. If the hypothesis survives, it's real. If it dies,
  you saved yourself from chasing a phantom.
- Generate 3–5 ranked hypotheses, not one. Single-hypothesis thinking anchors on
  the first plausible idea.

State each one precisely enough to be wrong — *"`total` is `NaN` because `price`
arrives as a string and `+` concatenates"*, not *"something's wrong with the
total"*.

## 4. Every run is a breadcrumb

Maintain a running **ledger** of every experiment in this session. Each entry:
what changed, what happened, what it ruled in or out.

- When a new hypothesis surfaces, walk the ledger. Does it hold for **every**
  prior observation, not just the most recent?
- If any past run contradicts it, the hypothesis is wrong or incomplete — refine
  or discard.
- When in doubt, design the **single experiment** whose outcome makes it certain.
  Run that next, instead of churning on adjacent runs.
- Update the ledger after every run. It is your memory across the session.

## 5. Fix the cause, then prove it

Before committing, answer: **why did this happen?**

If the answer is "the value was null so I added a null check", ask why it was
null. A guard that hides an upstream bug will be paid for later, with interest.
Legitimate fixes correct the wrong logic, the bad input at its source, or the
wrong assumption. A defensive check is legitimate only when that state is
genuinely valid.

Then prove it:

- The original repro now passes.
- **Write a test that fails without the fix and passes with it.** If you cannot
  write one, you probably do not understand the bug yet.
- Nothing else broke — run the wider suite.
- Remove the tagged probes: `grep -rn "\[DBG-" .`
- Report what you ran and what it returned. "Should be fixed" is not a result.

---

## Operating rules

- Recite the mantra block **once** per debug session, in your first response. Do
  not re-recite mid-session.
- Recite **verbatim**. Never paraphrase, shorten, or skip lines of the recital.
- If the user says "skip the mantra" → skip the recital but still apply the four
  steps silently.
- Apply the four steps **in order**:
  - Do not propose a fix before #1 is satisfied (reliable repro exists).
  - Do not start testing hypotheses before #2 has narrowed the fail path.
  - Do not commit to a hypothesis before #3 has tried to disprove it.
  - Do not declare a hypothesis correct until #4 confirms it against every prior
    breadcrumb.
- If you catch yourself proposing a fix without a reliable repro, stop and return
  to step 1.
- The mantra is a constraint **you** carry through the session — not advice to
  deliver back to the user.

## When you are stuck

- **Explain it out loud.** Articulating it exposes the assumption you skipped.
- **Re-read the symptom you wrote in step 0.** People routinely spend an hour
  debugging the wrong thing.
- **Question the assumption you never tested** — the one so obvious you did not
  check it. It is usually there.
- **Check the boring causes**: stale cache, wrong file, wrong branch, wrong
  environment, server not restarted, editor not saved.
- **Take a break.** Diminishing returns arrive faster than expected.

## When an agent is doing the debugging

- Give it the **exact** error and the repro, not a summary.
- Require the cause **before** the patch. A fix without an explanation is a guess
  wearing a diff.
- Be suspicious of a large diff for a small symptom — see
  `reviewing-ai-written-code`.
- Verify the fix yourself. An agent will often report success on the strength of
  having made an edit; that is a claim, not evidence.
- If two agent fixes in a row miss, stop and return to step 0 — the shared
  understanding of the symptom is probably wrong.

## Do not

- Do not change several things at once. You will not know which one mattered.
- Do not "fix" a bug you cannot reproduce; you cannot know you fixed it.
- Do not delete the failing test to make the suite pass.
- Do not leave `[DBG-…]` probes behind.
- Do not claim a fix works without running the thing.
