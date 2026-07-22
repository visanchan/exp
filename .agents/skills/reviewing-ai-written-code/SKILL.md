---
name: reviewing-ai-written-code
description: Review code an AI agent wrote before you keep it. Use after accepting a generated patch, before committing agent output, when a change is larger than the request warranted, when tests pass but something feels off, or when you are about to say "looks good" to code you have not actually read. Covers the failure modes specific to generated code, a fast review order, and how to verify claims an agent makes about its own work.
---

# Reviewing AI-Written Code

Generated code fails differently from hand-written code. It is fluent,
plausibly structured, and confidently wrong in specific, recurring ways. Reading
it the way you would read a colleague's patch misses most of them, because the
usual signals — hesitant naming, obvious gaps, visible confusion — are absent.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

**Related but different:** `scrutinize` asks whether a change should exist in
that shape at all, and traces real code paths to verify it does what it claims.
This skill assumes the change is wanted and hunts the defect classes that
*generated* code specifically produces. On anything that matters, run
`scrutinize` first — if the answer is "this shouldn't exist", the defect hunt is
moot. And if the change produces something a person sees, hears or clicks,
`artifact-verification` comes last: this skill reads the code, that one opens
the output.

## The core rule

**An agent's description of its work is a claim, not evidence.**

"I updated all the call sites", "I made the prompts self-contained", "tests
pass" — each is a hypothesis you can check in seconds and should. Claims like
these are frequently sincere and false: the model reports what it *intended*,
and nothing in the loop contradicts it.

Check the diff, not the summary.

## Review in this order

Cheapest and highest-yield first. Stop early if something fails.

### 1. Is the scope right?

Compare what you asked for against what changed. Generated patches routinely
include unrequested refactors, renamed variables, reformatted regions, extra
abstractions, and new files.

```bash
git diff --stat        # a one-line fix should not touch nine files
```

Anything outside the request is either a bug or a decision you did not make.
Both need attention now — unrelated changes bundled into a diff are how
regressions arrive unnoticed.

### 2. Does it delete anything?

Search the diff for removed lines you did not ask to remove: dropped error
handling, deleted validation, removed test cases, weakened assertions, skipped
checks.

The specific thing to look for: **a failing test that was changed rather than a
bug that was fixed.** It resolves the symptom and destroys the signal.

### 3. Do the imports and calls actually exist?

Generated code invents plausible APIs — functions that sound right, parameters
that should exist, methods from a different library or an older version.

For anything unfamiliar, confirm it is real: check the import resolves, the
signature matches, the parameter is spelled the way this version spells it.
This is the single most common defect class and the easiest to catch.

### 4. Read the parts that were not in the request

Skim the code you asked for; **read carefully the code you did not.** Volunteered
material gets the least scrutiny from everyone, including the model that wrote
it.

### 5. Check the edges

Generated code handles the described case well and the surrounding cases
carelessly. Ask specifically:

- Empty input, empty list, empty string.
- The value is missing versus present-but-falsy — `0`, `""`, `false`, `null`.
- The error path. Is the exception caught and silently swallowed?
- Off-by-one at boundaries.
- Concurrency, if anything is shared.

### 6. Run it

Not the tests it wrote — **the thing itself.** A patch can pass its own tests and
fail the actual use.

### 7. Check the tests test something

Read the generated tests before trusting a green run:

- Would this test **fail** if the implementation were wrong? If not, it asserts
  nothing.
- Is it asserting on real behaviour, or on a mock it also defined?
- Does it duplicate the implementation's logic instead of stating the expected
  result?
- Is the failing case actually covered, or only the happy path?

A tautological test is worse than no test: it produces confidence without
coverage.

## Failure modes specific to generated code

| Pattern | What it looks like | Why it happens |
|---|---|---|
| Plausible-but-absent API | A method that ought to exist | Trained on many versions and libraries at once |
| Confident wrong constant | A field name, port, enum, or unit that is subtly off | Fluency is independent of accuracy |
| Silent scope creep | A tidy-up you did not request, inside your fix | Optimising for a "good" patch rather than a minimal one |
| Symptom fix | A guard added where the cause is upstream | The symptom is visible, the cause is not |
| Fabricated self-report | "Updated all six" when four changed | Reports intent, not outcome |
| Tautological test | Asserts what the code does, whatever that is | Written from the implementation, not the requirement |
| Stale assumption | Correct for an older version of the library | Training data is not versioned to your project |

## Verifying claims fast

```bash
# "I updated every call site"
grep -rn "old_function_name" .          # should return nothing

# "I added tests for it"
git diff --stat -- '*test*'             # did test files change at all?

# "It handles the empty case"
grep -n "len(\|empty\|None\|\[\]" <file>

# "Tests pass"
<run them yourself>                     # the only version that counts
```

## Sizing the review to the risk

Not every diff deserves the full pass.

- **Skim** — throwaway scripts, formatting, comments, generated boilerplate you
  will not maintain.
- **Full review** — anything touching data you cannot regenerate, authentication,
  money, external calls, deletion, or anything that will outlive this week.
- **Full review plus a second run** — anything that deletes, sends, publishes, or
  charges. Irreversible actions get read twice.

## Do not

- Do not approve a diff you have not opened, however good the summary reads.
- Do not accept "tests pass" without running them.
- Do not let an unrelated refactor ride along in a bug-fix diff; ask for it split.
- Do not merge generated code you cannot explain. If you cannot say what a line
  does, you cannot maintain it — ask, or cut it.
- Do not assume that because it is fluent it is considered. Those are unrelated.
