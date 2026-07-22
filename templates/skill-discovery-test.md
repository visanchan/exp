# Skill Discovery Test

A skill nobody loads does nothing. This test checks whether an agent that has
read only `AGENTS.md` reaches for the **right** skill when given a realistic
request — and exposes the descriptions that are not triggering.

**Run it when:** a skill is added, renamed, merged, or has its description
changed; when onboarding a new agent or tool; or when someone reports that an
agent "didn't use the skill".

**Time:** about 10 minutes.

---

## Two variants — run both, they measure different things

**Variant A (below) is a wording audit, not a discovery test.** Most agent
environments load `AGENTS.md` and the skill catalog into context automatically
at session start. When they do, the descriptions are already in front of the
agent, and matching a scenario to one is far easier than noticing a skill exists
in the first place. A perfect score on Variant A tells you the descriptions are
*distinguishable from each other*. It does not tell you they *trigger*.

**Variant B is the discovery test.** It contains no mention of skills at all, so
the only thing being measured is whether the agent goes looking. Run it first —
once an agent has seen Variant A, it cannot be used for Variant B in the same
session.

| | Variant A | Variant B |
|---|---|---|
| Measures | Are descriptions distinguishable? | Does the skill get found at all? |
| Mentions skills | Yes | No |
| Valid when the catalog is pre-loaded | Yes | Yes |
| Sessions needed | 1 | 1 fresh session per scenario |

---

## Variant B — the discovery test

For each scenario, open a **fresh session** and paste **only the quoted request**
— nothing about skills, nothing about this test. Then observe what the agent
does before answering.

Score it on behaviour, not on its self-report:

- **Pass** — it opened the intended `SKILL.md` (or the skills index) before
  answering. Check its tool calls or file reads; do not just ask it afterwards.
- **Partial** — it produced advice consistent with the skill but never opened
  the file. The skill did not fire; the model already knew some of it.
- **Fail** — it neither opened the file nor followed the method.

Use the same eleven requests as Variant A, one per session, in whatever order.
Three or four is usually enough to see the pattern — if none of the first three
fire, the problem is systemic and testing seven more will not add information.

**If most come back Partial:** the descriptions are fine and the loading
instruction is weak. Strengthen the directive in `AGENTS.md` §13, not the
individual descriptions.

**If some fire and others do not:** compare their descriptions. The ones that
fire share something the others lack — usually the person's own words rather
than a category name.

---

## Variant A — the wording audit

1. Open a **fresh session** with the agent you want to test, in a clone of this
   repository.
2. Paste **block 1 only** and wait for the ten answers. Then paste **block 2**.
   They are split on purpose: block 2 names a skill file, which would give
   away one of the answers if it were visible during block 1.
3. Do not paste the answer key that follows them.
4. Record the results in the log at the bottom of this file, **including whether
   the catalog was pre-loaded** — without that note the score is not
   interpretable later.

---

### Block 1 — paste first

<!-- ==== BEGIN BLOCK 1 — copy from here ==== -->

```text
You are working in this repository. Read AGENTS.md first — it governs your work here.

I need you to do three things, in order. Do not skip ahead, and do not fix
anything until Part 1 is finished and recorded.

=== PART 1: BLIND SKILL-DISCOVERY TEST ===

This repository has skills under .agents/skills/. I want to know whether an
agent that has only read AGENTS.md picks the right one.

Do NOT open .agents/skills/README.md or any SKILL.md yet.

Based only on what AGENTS.md told you, answer each scenario below with:
  (a) which skill you would load, or "none",
  (b) how confident you are: high / medium / low,
  (c) the words in the scenario that made you choose it.

Write all eleven answers out before checking anything.

 1. "My login test passes on my laptop but fails in GitHub Actions. I've
     already tried three fixes and none worked."
 2. "The agent just wrote 200 lines to fix a one-line typo. Should I keep it?"
 3. "I want to build a booking tool for my aunt's salon, but I don't really
     know what she needs it to do."
 4. "I need uvicorn and npm run dev going at the same time, and something keeps
     killing one of them."
 5. "This feature would take two weeks. Is it worth building?"
 6. "How many small cafes in this city could actually use this product?"
 7. "I'm running out of context and I'm halfway through a task."
 8. "Here's my plan for restructuring the auth flow. Does this approach make
     sense before I start?"
 9. "I keep having to correct you about the same thing every session."
10. "I need to start a new experiment for class."
11. "The script finished and wrote all six files with no errors. Can I tell my
     professor it's done?"

Now open .agents/skills/README.md and compare your answers to the intended
mapping. Report a table: scenario | your answer | intended | match?

Be blunt. If you got one wrong, say so plainly — a wrong answer is the useful
result here, because it means a description is not triggering. If you got all
eleven right, do not just assert that: say which specific wording in AGENTS.md
drove each choice, so I can judge whether you actually reasoned or pattern-
matched from the numbering.

Also answer honestly: did you read AGENTS.md automatically at the start of this
session, or only because I told you to? I need to know whether it is discovered
by default in your environment.
```

<!-- ==== END BLOCK 1 ==== -->

### Block 2 — paste after the ten answers

<!-- ==== BEGIN BLOCK 2 — copy from here ==== -->

```text
=== PART 2: FIX WHAT THE TEST EXPOSED ===

For every mismatch or low-confidence answer:
  - Diagnose the cause. Usually it is a weak `description:` in the SKILL.md
    frontmatter, or a vague when-to-use line in AGENTS.md §13.
  - Fix the wording so the trigger is the situation and the words a person
    would actually type, not the topic.
  - Do not restructure the skills, rename them, merge them, or change their
    content. Wording and triggers only.
  - Re-run the affected scenarios to confirm the fix.

Two scenarios (2 and 8) are deliberately close together — one is about reviewing
code an agent wrote, the other about reviewing an approach before building. If
you confused them, that boundary needs sharpening in both descriptions.

If nothing needs fixing, say so and show your evidence. Do not invent work.

=== PART 3: WHAT IS MISSING ===

Read .agents/skills/write-a-repo-skill/SKILL.md, then propose any skills this
repository should have and does not.

Constraints, from that skill and from AGENTS.md:
  - Repeatable, non-obvious, stable, portable. No private business context, no
    personal paths, no third-party skill text.
  - Must not duplicate an existing skill. If it overlaps one, say whether to
    merge or sharpen the boundary, and why.
  - The test: has this come up at least twice, and did an agent get it wrong at
    least once?

For each proposal give: name, one-line description, the failure it prevents,
and why the existing eleven do not already cover it. Rank them.

DO NOT create any new skill yet. Propose only — I will choose.

=== RULES ===

- Follow AGENTS.md. It wins over anything I have said here.
- Commit your Part 2 fixes with a clear message. Do NOT push.
- Record what you changed and why in docs/decisions/ if the change affects a
  skill's scope, per AGENTS.md §13.
- Report back: the Part 1 table, what you fixed, and your Part 3 proposals.
```

<!-- ==== END BLOCK 2 — stop copying here ==== -->

---

## Answer key

**Do not paste this into the agent.** It is here so the test stays maintainable.

| # | Scenario summary | Intended skill |
|---|---|---|
| 1 | Test passes locally, fails in CI, three fixes missed | `debug-mantra` |
| 2 | Agent wrote 200 lines for a one-line fix | `reviewing-ai-written-code` |
| 3 | Wants a tool but cannot say what it must do | `requirements-workbook` |
| 4 | Two dev servers, one keeps dying | `local-dev-servers` |
| 5 | Is this two-week feature worth building? | `business-analysis` |
| 6 | How many potential customers exist? | `market-sizing` |
| 7 | Running out of context mid-task | `session-handoff` |
| 8 | Review my approach before I start | `scrutinize` |
| 9 | Keeps needing the same correction each session | `write-a-repo-skill` |
| 10 | Starting a new class experiment | `ai-class-operating-partner` |
| 11 | Script ran clean, files written — is it done? | `artifact-verification` |

**Scenarios 2 and 8 are the load-bearing pair.** Both are "review this". One is
a defect hunt on generated code; the other asks whether an approach should exist
at all. If an agent swaps them, the boundary between those two skills is not
sharp enough — fix both descriptions, not just one.

## Reading the results

- **A wrong answer is the useful outcome.** It names a description that does not
  trigger, which is the only thing this test can tell you.
- **Treat a perfect Variant A score sceptically**, and check what was in context
  before believing it. If the catalog was pre-loaded — which is the normal case
  — the agent was matching descriptions it could already see, not discovering
  anything. The score is still worth having: it says the descriptions are
  distinguishable from each other. It is not evidence that they fire.
- **Only Variant B is evidence of discovery**, and only from observed behaviour.
  An agent's account of whether it "would have" loaded a skill is not data.
- **Low confidence is a finding too**, even when the answer is right. It means
  the description is doing less work than it should.
- **"None" is sometimes correct.** If a scenario genuinely has no matching
  skill, that is a gap, not a failure.

## Keeping this test current

The test decays the moment the skills change.

- **Added a skill?** Add a scenario for it, and a row to the answer key. Write the
  scenario in a person's words — the symptom, not the topic — and never use the
  skill's name in it.
- **Removed or merged a skill?** Remove or re-point its scenario.
- **Sharpened a boundary between two skills?** Make sure the pair that could be
  confused both appear, adjacent, as scenarios 2 and 8 do.

Keep the count of scenarios equal to the count of skills, so a missing scenario
is visible at a glance.

## Log

Record each run. A result that is never written down cannot show a trend.

| Date | Agent / tool | Variant | Score | Catalog pre-loaded? | Notes |
|---|---|---|---|---|---|
| 2026-07-23 | Codex | A | 10/10 | **Yes** — `AGENTS.md` and the skill catalog were supplied automatically at session start | Not a discovery result; descriptions are distinguishable. Scenarios 2 and 8 were separated correctly. Confirmed Codex loads `AGENTS.md` without being asked. Variant B added afterwards because of this run. |
| | | | | | |
