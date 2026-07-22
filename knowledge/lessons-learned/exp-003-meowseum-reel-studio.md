# Lessons Learned — exp-003 Meowseum Reel Studio

## Experiment reference
- Experiment ID: `exp-003-meowseum-reel-studio`
- Original location: `experiments/exp-003-meowseum-reel-studio/` (deleted)
- Date: 2026-07-22 to 2026-07-23
- Class topic: agentic source-to-video architecture, applied to a controlled
  real-world content library instead of an open-ended user upload
- Index row: `archive/experiment-index.md`

## What was attempted

Turn one page of a real product website into a narrated vertical video through a
chain of agents: source curator → characters/locations → concepts → outline →
outline critic → shots → shot critic → images → narration. A local server ran
the chain, streamed progress to a browser, played the result as a 9:16
slideshow, and exported it as an MP4.

The point was never the video. It was two questions: does constraining
generation to an extracted real source produce more inspectable output than
free-form prompting, and does tagging each shot with `source_basis` (facts from
the page) versus `creative_addition` (invented) make an agent chain auditable?

## What worked

- **Structurally withholding data beat instructing the model to avoid it.** The
  commercial-safety requirement — never narrate an unconfirmed price, stock
  level or dimension — held because those fields were kept out of the context
  the story agents ever saw, not because a prompt forbade them. The prompt rule
  existed as a second layer and was never the mechanism. Extracted as a pattern.
- **A deterministic audit was the only stage that ever caught a real defect.**
  A ~50-line function checking declared sources and regex-sweeping for
  commercial claims outperformed two LLM critic stages across four runs.
- **Probing an unfamiliar API beat assuming its shape.** Every model swap was
  preceded by a cheap live probe. This caught two 400-level incompatibilities
  before they could waste a run, and one free trick: sending a deliberately
  invalid enum value returns an error listing the valid ones, at no generation
  cost.
- **Discovering an optional binary rather than requiring it.** MP4 export needed
  ffmpeg; the machine already had one inside an unrelated application. Probing
  for it and reporting export as a capability kept the app runnable everywhere.
- **Splitting a run into per-shot artifacts on disk.** Images, audio and a
  manifest per run meant export, replay and grading all worked after a restart,
  and comparisons between runs were possible months-of-context later.

## What failed

- **Citation-shaped hallucination.** A shot cited a real field name and then
  asserted a claim that field never made ("scratching greatly improves health"
  attributed to a care instruction that only said where to mount the product).
  The audit passed it, because the audit checked that the cited *name* existed,
  not that the cited *value* supported the sentence.
- **Both critic stages reported work they had not done.** The shot critic
  claimed it had made every image prompt self-contained (it had not) and that it
  had shortened narration to fit the time budget (it had not — 12 of 12 lines
  overran across two runs). This survived a model upgrade and a language change.
- **Character drift across shots**, until a stronger model incidentally fixed
  it. Prompts said "a fluffy cat with distinct markings" — a placeholder *for*
  specificity rather than specificity itself — so each render invented its own.
- **Product identity drift**, unfixed. The product renders as the famous artwork
  it parodies rather than the physical object. A materially better image model
  changed nothing, confirming it as a prompt defect.
- **An untested provider fallback.** A second model provider was wired in and
  preferred-if-configured. No key ever selected it, so it never ran; it would
  have failed on its first call on parameter names and carried the wrong pricing.
- **C7 was recorded as unanswered when it had in fact been answered.** The
  experiment README said the uploaded-photo arm was "NOT RUN — no cat photo
  available to upload". A complete, error-free six-shot run using that path was
  sitting in the artifacts folder the whole time, found only during the
  pre-deletion inventory. See below — it refutes one of the four hypotheses.

## The result that nearly got deleted

The experiment's fourth hypothesis, written before any code:

> A fixed brand protagonist will produce more consistent output than a
> user-uploaded cat photo, because the reference is stable.

**This is wrong, and the opposite is true.** Graded on the same text model, same
source page, same settings — only the protagonist path differing:

| Protagonist path | Mechanism | Cross-shot identity |
|---|---|---|
| Brand character (described in text) | character description written into each image prompt | **2/5**, twice |
| User-uploaded photo | the photo passed as a reference image to the image-edit endpoint | **4/5** |

The brand runs changed the animal outright — a brown-and-white long-haired cat
in one shot and a cream-orange cat in another; in a second run, a four-legged
tabby and then an anthropomorphic tabby standing upright in a tweed jacket. The
uploaded-photo run kept a recognisably identical solid-black short-haired cat
across shots, drifting only in eye colour (amber in one shot, green in another).

The reason is mechanical, and it generalises: **a reference image is a fixed
artefact; a text description is re-interpreted on every call.** Words describing
an animal are re-rendered from scratch each time, and everything the words leave
unsaid gets re-invented. Pixels do not get re-interpreted. The hypothesis assumed
"brand asset" meant "stable reference" — but the brand asset was only stable as
*text*, which is the weakest possible form of visual reference.

**The process lesson is worth as much as the finding.** This sat undiscovered
because the criterion was marked NOT RUN in the README and nobody re-checked the
artifacts directory. An experiment's own notes are a claim about what happened,
not evidence of it. It surfaced only because the cleanup checklist forces an
inventory before deletion — the criterion had been open for the entire
experiment and would have been destroyed, unexamined, by a one-line "delete the
folder" request.

## Root causes

| Failure | Symptom | Root cause | How it was found |
|---|---|---|---|
| Citation-shaped hallucination | Invented health claim with a valid `source_basis` | Audit validated field *names* against a whitelist; nothing compared the claim to the field's *value* | Manual read of a generated shot |
| Critic false self-report | "Shortened narration to fit" while every line overran | A generator asked to grade its own output reports intent, not outcome; nothing external verified the claim | Only after narration became audible and could be measured |
| Character drift | Different cat in shots 1 and 4 | "Describe the same cat" is satisfiable by repeating a vague phrase; no literal shared string was required | Looking at the rendered images |
| Product drift | Real oil painting instead of the physical product | The character description is repeated in every prompt; the product noun phrase is not | Persisted across two image models |
| Untested fallback path | None — it never executed | A branch selected by a key nobody had; no test ever exercised it | Reading it before deleting it |
| Silent parameter breakage | Every text call 400s after a model swap | Parameter names and accepted value ranges differ between model families of the same provider | Live probe before the rewrite |

## Reusable patterns

| Pattern | When to use it | Where it lives |
|---|---|---|
| Quarantine unverified data structurally instead of forbidding it in the prompt | Any generation touching prices, medical, legal or safety-critical facts | `knowledge/reusable-patterns/structural-data-quarantine.md` |
| Put the check in deterministic code, not in a second model | Any pipeline with a "reviewer" or "critic" stage | `knowledge/reusable-patterns/deterministic-audit-over-critic.md` |
| Discover an optional binary and report it as a capability | A feature needing a system tool not everyone has | `knowledge/reusable-patterns/discovered-optional-binary.md` |
| Stills + per-shot audio → one MP4 | Slideshow video from generated assets | `knowledge/code-snippets/stills-plus-audio-to-mp4.md` |
| Probing an unfamiliar model API before writing against it | Any model swap | `knowledge/tool-notes/openai-model-api-surface.md` |

## Anti-patterns

| Anti-pattern | Why it fails | Warning sign | Do instead |
|---|---|---|---|
| Asking a model to audit its own output | It reports intent, not outcome; the report is fluent and false | The critic's "changes" list reads like a to-do list rather than a diff | Verify externally in code; keep the model for judgement, not for guarantees |
| Validating that a citation *exists* | A real field name can carry an invented claim | Audit passes but a human reading the output finds nonsense | Check the claim against the field's value, not its name |
| Instructing a model to "be consistent" | Satisfiable by repeating a vague phrase that specifies nothing | The phrase recurs but the output does not | Require a literal shared string, and check for it |
| Keeping an unexercised fallback path | It is a second, unverified way to fail, wearing the costume of resilience | No test ever selects it; it exists "just in case" | Delete it, or make a test force it to run |
| Reusing a pricing table across a model swap | The number stays confident and becomes wrong; a cost metric looks measured | Cost figures unchanged after switching models | Key rates to the model, and report "unpriced" rather than guessing |
| An output nobody can perceive | Nobody checks it; defects accumulate silently | A feature that has never been seen, heard or opened by a human | Render it, then look at it |
| Trusting the experiment's own notes as evidence | A criterion marked "NOT RUN" had in fact run; the result sat unexamined for a day | A status claim in a README that nothing re-verified | Inventory the actual outputs before concluding, and always before deleting |
| Describing a visual identity in words when you hold an image of it | Text is re-interpreted per call; whatever it leaves unsaid is re-invented | The same phrase recurs across prompts and the output still varies | Pass the image as a reference; reserve text for what no image can carry |

## Useful prompts

The strongest finding here is about a prompt *failure* and its fix. Saved to
`knowledge/prompt-library/character-sheet-for-visual-consistency.md`.

```text
The protagonist is <NAME>: describe the same cat in every prompt, with
identical markings and the same small detail, so the animal is recognisable
from shot to shot.
```

- Why it *failed*: "identical markings" is an instruction to be specific, not a
  specification. A weaker model satisfied it by repeating the words "distinct
  markings" in each prompt while inventing different markings each render.
- Why a stronger model succeeded on the same text: it generated a literal
  description once and repeated it verbatim — supplying the missing
  specification itself.
- Transferable form: generate the sheet once, substitute it as a literal string,
  and check every prompt contains it. Do not leave it to the model's discretion.

## Transfer opportunities

- Any retrieval-grounded generation where "cite your source" is a requirement —
  the citation-versus-entailment gap applies directly to RAG.
- Any multi-agent pipeline with a reviewer stage; the finding that a
  deterministic check outperformed two LLM critics is the cheap lesson here.
- Any product or marketing automation touching unconfirmed commercial data —
  the quarantine pattern generalises to medical, legal and financial copy.
- Cost instrumentation in any LLM project: rates belong to models, not providers.

## Recommended next step

- **Next step:** none for this line of inquiry as an experiment. The
  architectural questions were answered: grounding makes *auditing* cheap and
  effective, but only where the audit is deterministic; per-shot source tagging
  exposes unattributed invention and not confabulation wearing a valid citation.
- **Rationale:** the two remaining defects (narration length, product noun
  phrase) both have known, small, deterministic fixes. They are engineering
  work, not research; nothing further would be learned by doing them here.
- **Follow-up experiment:** none required. If the pipeline is ever rebuilt for
  real use, start from the patterns above rather than from this code.
