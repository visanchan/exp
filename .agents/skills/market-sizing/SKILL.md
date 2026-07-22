---
name: market-sizing
description: Estimate how big a market is, defensibly. Use when asked how large an opportunity is, when writing the market section of a pitch or case study, when comparing two opportunities, or when a number like TAM, SAM or SOM is needed and must survive being questioned. Covers defining the market, three independent estimation methods, triangulating between them, sanity checks, and the errors that make a number collapse under scrutiny.
---

# Market Sizing

A market size is an argument, not a fact. It will be challenged, and it survives
or fails on whether the reasoning is inspectable — not on how big it is or how
confident it sounds.

The goal is a number a sceptical reader can follow, disagree with in one
specific place, and adjust. That is worth far more than precision.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## First, define the market

Most bad sizing is a definition problem, not an arithmetic problem. Before any
number, answer:

1. **Who is the buyer?** The person or organisation that pays. Not the user, if
   they differ.
2. **What problem, specifically?** Narrow enough to exclude near-neighbours.
3. **What do they spend on it today?** If the answer is nothing, you are sizing a
   behaviour change, which is a different and harder estimate.
4. **What is the unit?** Per seat, per device, per transaction, per year.
5. **What geography and time period?**

Write these down. A number without its definition is unusable, because nobody
can tell what was included.

## The three layers

| Layer | Meaning | Question it answers |
|---|---|---|
| **TAM** — total addressable | Everyone with the problem, if you had no constraints | Is this worth entering at all? |
| **SAM** — serviceable addressable | The part your product and channel can actually serve today — geography, segment, regulation, language | What could we grow into? |
| **SOM** — serviceable obtainable | What you can realistically win in a defined period, given competition and capacity | What is the plan? |

Each is a **subset** of the one above. If SAM is not visibly smaller than TAM,
one of them is wrong.

SOM is where credibility is won or lost. A SOM that is a flat percentage of SAM
("we'll take 1%") is not an estimate — it is a wish with a decimal point. Build
it from capacity: how many customers can you actually reach and serve, given
your sales motion, in this period?

## Estimate three ways, independently

Do not pick one method. Do all three where you can, then compare.

### Top-down — from a published total

Start from an industry figure and cut it down with explicit filters.

```
Published market total for the category          $4.0B
× share in your geography                        × 12%     → $480M
× share in your segment (e.g. SMB, not enterprise) × 40%   → $192M
× share your product actually addresses          × 25%     → $48M   ← SAM
```

Fast, and inherits whatever is wrong with the source. Always ask what the
published figure counted — revenue, spend, or "opportunity" — and whether the
category matches yours.

### Bottom-up — from units and price

Build from countable things. This is the most defensible method and the one to
lead with.

```
Number of potential buyers                       40,000 businesses
× share with the problem acutely enough to pay   × 30%       → 12,000
× realistic annual price                         × $4,000    → $48M   ← SAM
```

Every input is separately checkable. When someone disputes the number, they will
dispute one line, which is exactly what you want.

### Value-theory — from value created

Useful when nothing comparable exists, or when pricing is not yet set.

```
Value created per customer per year (hours saved × loaded cost)   $20,000
× share of that value you can capture in price                    × 20%     → $4,000
× number of buyers (from bottom-up)                               × 12,000  → $48M
```

Capture rates above ~30% are unusual and need justification.

## Triangulate

Put the three side by side.

- **Within ~2×** — reasonable. Take the middle, state the range.
- **3–5× apart** — find the disagreement. It is usually one input, and finding it
  teaches you something real about the market.
- **10× apart** — a definition mismatch. The methods are sizing different
  markets. Go back to the definition.

**Report the range, not a single number.** "$30–60M, most likely $45M" reads as
competence. "$47.3M" reads as false precision and invites attack on the
decimals rather than the logic.

## Sanity checks

Run these before showing anyone. Each one catches a common, embarrassing error.

- **Population bound.** Does the buyer count exceed the number of such entities
  that exist? Look up the real total.
- **Penetration realism.** What share of the market does your SOM imply? Above
  ~5% in year one, for a new entrant, needs a specific reason.
- **Comparable check.** What does the largest existing player actually earn? If
  your TAM is smaller than their revenue, the TAM is wrong. If your SOM exceeds
  their revenue, so is that.
- **Per-customer sense.** Divide the market size by the buyer count. Is that a
  plausible annual spend for that buyer? A $50,000 answer for a small business
  is a signal, not a result.
- **Order of magnitude.** Is the number in billions when the category is
  obviously a niche? Recompute rather than explain.

## Common errors

| Error | Why it fails | Fix |
|---|---|---|
| TAM as "everyone" | 8 billion people is not a market | Size the buyer with the problem, not the population |
| Percentage-of-a-big-number SOM | "1% of a $10B market" is not a plan | Build SOM from reachable capacity |
| Revenue and spend confused | Vendor revenue ≠ what buyers spend on the problem | State which one, and stay consistent |
| Double counting | Counting the same money in two segments | Draw the segments so they do not overlap |
| Frequency ignored | Yearly and one-off treated the same | Define the unit as per year, explicitly |
| Stale source | A pre-shift figure applied to a changed market | Note the source year; adjust or say you cannot |
| Precision without accuracy | "$47.3M" from three guessed inputs | Report a range and name the biggest assumption |

## Write it up

A defensible market size shows its work:

1. **The definition** — buyer, problem, geography, unit, period.
2. **Each method**, with every input and where it came from.
3. **The triangulation** and what you concluded.
4. **The range**, with the most likely value.
5. **The one assumption that matters most** — the input that, if wrong, moves the
   answer furthest. Name it before someone else does.
6. **Sources**, with dates. "Industry report" is not a source.

## Using AI for this

Models are useful for structuring the estimate and terrible as a source for the
inputs. They will produce confident, specific, plausible figures that are
unverifiable or invented.

- Use it to **build the model** — which factors, in what order.
- Do **not** take a market figure, growth rate, or buyer count from it without a
  citation you have checked yourself.
- Ask it to list what would have to be true for the estimate to be wrong.
- Any number it supplies without a source is a placeholder. Mark it as one.
