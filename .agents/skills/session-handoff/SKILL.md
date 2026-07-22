---
name: session-handoff
description: Carry work across a context limit, a session end, or a change of agent without losing what was learned. Use when a session is getting long, when an agent starts repeating questions it already answered or contradicting earlier decisions, before stopping work that is not finished, or when handing a task to a different agent or person. Covers what to write down, what to leave out, and how to restart cleanly.
---

# Session Handoff

Agent sessions end — context fills, the window closes, the tool restarts, the
day finishes. What is lost is not the code, which is on disk, but everything
around it: what was tried and rejected, why a decision went the way it did,
which dead ends are already ruled out.

Without a handoff the next session re-derives it, usually differently, and
often re-introduces a bug the last one fixed.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## When to write one

- Before stopping work that is not finished.
- When responses start showing context strain — repeated questions, forgotten
  decisions, contradicting an earlier choice.
- Before a task changes hands.
- Before any long-running or risky step, so a failure is recoverable.

Writing one takes two minutes. Reconstructing an afternoon takes an afternoon.

## What to write

Keep it in the repository — a scratch file, a note in the experiment folder, or
a commit message. Not in the chat, which is the thing about to disappear.

```markdown
## Handoff — <date>

### Goal
<What we are trying to achieve. One or two sentences.>

### State
<What is done and verified. What is half-done and how. What has not started.>

### Decisions made
<Each with its reason. This is the part that is expensive to rediscover.>
- Chose X over Y because Z.

### Ruled out
<Approaches already tried and rejected, and why. Prevents the next session
walking the same dead end.>
- Tried A — failed because B.

### Next step
<The single next action, concrete enough to start without re-reading anything.>

### Watch out for
<Traps found the hard way: a flaky test, a service that must be restarted, a
file that looks unused but is not.>
```

**"Ruled out" is the highest-value section and the one most often skipped.**
Finished work is visible in the diff; failed attempts leave no trace, so they
get repeated.

## What to leave out

- Anything reconstructable from the code or `git log`. Do not summarise the diff.
- Full file contents. Reference paths.
- Narrative of the session. The next reader needs the state, not the story.
- Anything already written in the experiment README or a decision record — link
  to it instead.

## Restarting

At the start of the next session:

1. Read the handoff **first**, before opening any file.
2. Verify the state claims — "tests pass" was true when written, not
   necessarily now. Re-run before building on it.
3. Check `git status` and `git log` for anything the handoff does not mention.
4. Confirm the goal still holds. Priorities move between sessions.

Verifying the state before continuing is the step people skip, and it is the one
that prevents building on a stale assumption.

## Working with a fresh agent

A new agent has no memory of the session, only what it can read. So:

- **Point at files, not at recollection.** "See the handoff at `notes/handoff.md`"
  beats explaining it again in prose.
- **Give the constraints, not just the task.** The task is usually obvious from
  the code; the constraints are not, and violating them is the common failure.
- **Say what is already settled**, so it does not re-open a decided question and
  quietly change direction.
- **Say what was already tried.** Otherwise it will suggest it.

## Handing to a person

Same content, different emphasis. Lead with:

1. **Where things stand**, in one sentence.
2. **What they need to do next**, concretely.
3. **What will bite them** if nobody says it.

Everything else is reference material they can read if they need it.

## Do not

- Do not rely on the conversation surviving. It will not.
- Do not write a handoff that says only what was done. Done is visible; *why*
  and *what failed* are not.
- Do not leave a running background process out of the handoff — say what is
  running, on which port, and whether it survives the session.
- Do not hand off a claim you have not verified. Mark unverified state as
  unverified.
