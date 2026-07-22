# Pattern — Put the Check in Code, Not in a Second Model

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)

## Problem

The standard fix for unreliable generation is a critic stage: a second model
pass that reviews the first and returns a corrected version. It is easy to add,
it produces confident and well-structured output, and it is very hard to tell
whether it is doing anything.

Across four runs and two model generations, the critic stages in this experiment
**reported work they had not performed**:

- *"Ensured that the character is consistently described in each image prompt."*
  Two of six prompts omitted the description entirely.
- *"Shortened the narration so it can be spoken within five seconds."* All six
  lines ran 6.1–8.8 seconds. Twelve of twelve failed across two runs.

Both claims were fluent, specific, plausible, and false. The second one survived
a model upgrade *and* a change of output language — this is not a weak-model
artifact. A generator asked to grade its own work reports **intent**, not
outcome, and nothing in the pipeline contradicted it.

## Pattern

Every property you actually need guaranteed gets a deterministic check. The
model stays for judgement; code provides the guarantee.

```python
def audit_shots(shots: list[dict], record) -> dict:
    """No model calls. This is what still holds if every agent misbehaves."""
    allowed = set(record.story_context()["allowed_basis"])
    problems = []

    for shot in shots:
        number = shot.get("shot_number", "?")

        # 1. Did it declare a source at all?
        basis = shot.get("source_basis") or []
        if not basis and not shot.get("creative_addition"):
            problems.append({"shot": number, "kind": "ungrounded"})

        # 2. Is every cited field real?
        for name in basis:
            if name not in allowed:
                problems.append({"shot": number, "kind": "unknown_basis",
                                 "detail": f"cites {name!r}, not a field"})

        # 3. Forbidden claims, by regex over everything the viewer sees.
        text = " ".join(str(shot.get(k, "")) for k in ("narration", "caption"))
        for pattern, label in FORBIDDEN:
            if (match := pattern.search(text)):
                problems.append({"shot": number, "kind": "claim",
                                 "detail": f"{label}: {match.group(0)!r}"})

    return {"problems": problems, "clean": not problems}
```

Run it **before and after** the critic and keep both results. The difference is
the only honest measure of whether the critic earned its cost.

## What a deterministic audit cannot do — and the trap that follows

Check 2 above validates that a cited field *exists*. It does not validate that
the field's *value* supports the sentence. A shot cited a real `care` field —
which said only "mount within your cat's reach, brush off loose fibres" — and
narrated *"scratching greatly improves health"*. The audit passed it.

**A citation is not evidence.** Name-level checking catches sloppiness;
confabulation wearing a valid citation walks straight through. Closing that gap
needs a value-level check: does the cited text actually entail the claim?

Equally, an audit only sees what you hand it. This one read narration, captions
and prompts — so visual drift across images was structurally invisible to it,
and it called two visibly broken runs clean. **Know which dimensions your audit
is blind to and say so**, rather than reading "clean" as "correct".

## Rules of thumb

- If the property is checkable in code, check it in code. Length, presence,
  format, whitelist membership, forbidden patterns — all cheap, all exact.
- If a critic claims to have done something, that claim is a hypothesis. Test it
  once. If it is false, the critic is decoration.
- Keep the before/after audit in the run manifest. Without it you cannot tell a
  useful critic from an expensive one.
- Upgrade the model to buy judgement. Write a check to buy a guarantee. In this
  experiment a stronger model fixed the defect requiring knowledge (a consistent
  character description) and did nothing for the defect requiring measurement
  (narration duration) — because no model grades its own output against a
  stopwatch.

## When a model critic is still worth it

For genuinely subjective properties — is this funny, is this on-brand, does this
beat land — where no deterministic check exists. Just don't mistake its
self-report for verification, and don't let it own a property you could have
checked.

## Related

- `knowledge/reusable-patterns/structural-data-quarantine.md`
