# Pattern — Quarantine Data Structurally, Don't Forbid It in the Prompt

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)

## Problem

A generator must never state certain facts: an unconfirmed price, a stock level,
a dosage, a legal deadline, a customer's real name. The obvious approach is a
firm instruction —

```text
Never state or imply a price, availability, shipping terms, weight, or
dimensions. That information is not confirmed for marketing.
```

— and it mostly works, which is the trap. "Mostly" is not a property you can
report to anyone. The rule holds until a prompt is rephrased, a model is
swapped, a user asks directly, or the instruction drifts far enough up a long
context to stop mattering. You cannot prove absence of leakage by reading a
prompt, and every model change re-opens the question.

## Pattern

Split the extracted record in two at the point of extraction, and never pass the
forbidden half to the generating stages.

```python
@dataclass
class SourceRecord:
    title: str
    summary: dict
    fields: dict          # safe: story material
    transactional: dict   # quarantined: price, stock, shipping, weight, size
    verified_for_marketing: bool = False

    def story_context(self) -> dict:
        """The only view any generating stage is given."""
        context = {
            "title": self.title,
            "summary": self.summary,
            "fields": self.fields,
            "allowed_basis": sorted(f"fields.{k}" for k in self.fields),
        }
        if self.verified_for_marketing:
            context["transactional"] = self.transactional
        return context
```

Every agent receives `record.story_context()`. Nothing receives `record`.

Keep the prompt instruction as well — it is a cheap second layer, and it makes
the intent legible to whoever reads the prompt next. But it is no longer the
mechanism.

## Why it works

The model cannot leak what was never in its context. This converts an
unfalsifiable claim ("the prompt tells it not to") into a checkable one ("the
value is not in the payload"), and the check is a test rather than a judgement:

```python
def test_no_price_survives_anywhere_in_story_context(self):
    blob = json.dumps(record.story_context(), ensure_ascii=False)
    for forbidden in ("890", "฿", "In stock", "700 g", "Free shipping"):
        self.assertNotIn(forbidden, blob)
```

That test does not care which model runs, how the prompt is worded, or how
adversarial the user is. It passed against a prompt explicitly asking for the
price.

The flag matters as much as the split: `verified_for_marketing` gives a single
place to open the gate once a human has confirmed the data, so the quarantine is
a workflow state rather than a permanent amputation.

## When to use it

Any generation touching data that is unconfirmed, regulated, private, or simply
someone else's to approve — pricing and availability, medical or dosage detail,
legal terms and dates, PII, internal-only figures.

## When not to use it

When the model genuinely needs the value to do the task. Quarantine is not
redaction-by-default; withholding a field the task depends on produces confident
invention instead, which is worse. If the model must reason over a price, pass
it and check the output instead.

## Related

- `knowledge/reusable-patterns/deterministic-audit-over-critic.md` — the same
  instinct applied to verification: put the guarantee in code, not in a model.
