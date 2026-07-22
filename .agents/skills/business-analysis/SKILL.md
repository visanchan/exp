---
name: business-analysis
description: Turn a business question into an analysis that actually changes a decision. Use when asked whether something is worth doing, when comparing options, when building a business case, when working out unit economics or a break-even, or when presenting numbers to someone who has to act on them. Covers starting from the decision, structuring the calculation, sensitivity testing, and writing it up so the recommendation is the first thing read.
---

# Business Analysis

The common failure is not bad arithmetic. It is a competent analysis that
nobody can act on — because it answered an interesting question instead of the
one in front of the decision-maker, or because the recommendation is on slide
fourteen.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

## Start from the decision, not the data

Before opening a spreadsheet, write down:

1. **What decision does this inform?** Someone will do something differently
   depending on the answer. Name the action.
2. **Who decides**, and what do they already believe?
3. **What would change their mind?** This defines the analysis. If nothing
   would, the analysis is decoration — say so and stop.
4. **When is it needed?** A rough answer on Tuesday beats a precise one next
   month, when the decision was Wednesday.

The test: *if the number came out the opposite way, would anyone act
differently?* If not, you are measuring, not analysing.

## Structure before you calculate

Break the question into parts that can be estimated separately, then recombine.
"Should we launch this?" is not calculable. Its parts are:

```
Contribution per unit  = price − variable cost
Volume                 = reach × conversion × frequency
Fixed cost             = build + run
Result                 = contribution × volume − fixed cost
```

Now each input is a separate, arguable question — which is the point. An
analysis that can only be accepted or rejected whole is not useful. One where a
reader can dispute a single line is.

## The numbers that usually matter

**Contribution margin** — what one more unit earns after the costs that scale
with it. If this is negative, volume makes things worse, and nothing else in the
model matters.

```
Contribution margin = price − variable cost per unit
Contribution ratio  = contribution / price
```

**Break-even** — how much you need before the fixed cost is covered.

```
Break-even units = fixed cost / contribution per unit
```

Always compare it to something real. "Break-even at 12,000 units/year" means
nothing until you add "against current volume of 3,000."

**Payback period** — how long until the money comes back. Shorter is not just
safer, it compounds: cash returned is cash redeployable.

**Customer economics**, when relevant:

```
Acquisition cost (CAC)     = total acquisition spend / customers acquired
Lifetime value (LTV)       = contribution per period × expected lifetime
```

Rules of thumb worth knowing and worth doubting: LTV/CAC above ~3 is healthy;
payback under ~12 months is comfortable. Both assume the retention estimate is
honest, which early on it usually is not — a lifetime assumption longer than the
business has existed is a guess, not a measurement.

**Opportunity cost** — the option you give up. An analysis that compares a
project against doing nothing, when the real alternative is a different project,
is answering the wrong question.

## Test the assumptions, not just the answer

A single-point answer is the least useful output. Two extra steps make it
decision-grade:

**Sensitivity.** Vary each input alone and see how far the answer moves. Usually
one or two dominate. Those are the ones to research, and the ones to talk about.

```
Base case                       $180k profit
Conversion 3% → 2%              $40k        ← dominates
Price −10%                      $120k
Fixed cost +20%                 $160k
```

This turns "here is my forecast" into "the answer hinges on conversion, and here
is what we know about it" — which is far more defensible and far more useful.

**Break-even on the worst assumption.** Instead of defending a number, invert it:
*how bad can conversion get before this stops being worth doing?* An answer of
"below 1.8%" lets the decision-maker use their own judgement, which they will
trust more than yours.

**Three cases.** Pessimistic, base, optimistic — each with its assumptions
stated. If the pessimistic case is still acceptable, the decision is easy. If the
optimistic case is barely acceptable, that is also decisive.

## Sanity checks

- **Does the total make sense from the other direction?** Recompute one number a
  second way. Disagreement means an error, not a rounding difference.
- **Are the units consistent?** Monthly and annual mixed in one formula is the
  most common arithmetic error in business models.
- **Is the growth rate survivable?** Sustained growth compounds absurdly.
  Extend the projection two more years and see whether it implies more customers
  than exist.
- **Does it double-count?** A saving counted in two places, or revenue counted in
  both an existing and a new segment.
- **Would the result surprise someone who knows this business?** If yes, either
  you have found something, or you have made a mistake. Find out which before
  presenting it.

## Writing it up

Lead with the answer. The reader wants the recommendation, not the journey.

```
Recommendation — one sentence, with the action.
Why — the two or three numbers that drive it.
What it depends on — the assumption that matters most, and what happens if it
  is wrong.
What we do not know — honestly.
Detail — the model, the inputs, the sources.
```

Rules that consistently improve these write-ups:

- **Round.** "$180k" not "$183,472". False precision invites arguments about
  decimals rather than logic.
- **Show one number's derivation** in the body, in full. It demonstrates the rest
  can be checked.
- **State assumptions inline** where they are used, not in an appendix nobody
  opens.
- **Give the range**, and say which direction you would bet.
- **Never hide the weak assumption.** Naming it yourself makes the analysis
  credible. Having it found makes everything else suspect.

## Common failure modes

| Failure | Tell | Fix |
|---|---|---|
| Analysis that cannot change the decision | Nobody acts either way | Ask what would change their mind, first |
| Precision as a substitute for accuracy | Six significant figures from guessed inputs | Round, give a range, name the weak input |
| Best case presented as the case | One scenario, all assumptions favourable | Three cases, assumptions stated |
| Ignoring the alternative | Compared against zero | Compare against the real next-best option |
| Sunk cost | "We have already spent…" | Only future costs and benefits count |
| Survivorship in the comparables | Only successful examples cited | Ask what happened to the ones that failed |
| Fixed and variable confused | Break-even is wrong, often badly | Classify each cost by whether it scales with volume |

## Using AI for this

- Good at **structuring** — decomposing the question, listing what to consider,
  building the model skeleton, catching a missing cost category.
- Good at **stress-testing** — ask it to argue the opposite conclusion, or list
  what would have to be true for the recommendation to be wrong.
- **Not a source for facts.** Market figures, benchmarks, growth rates and
  industry averages it supplies without a citation are placeholders. Mark them
  and replace them.
- **Check the arithmetic.** Multi-step calculations in prose are frequently
  wrong in ways that read fluently. Recompute anything load-bearing.
