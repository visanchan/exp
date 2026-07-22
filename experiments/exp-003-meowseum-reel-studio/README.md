# exp-003 — Meowseum Reel Studio

## Experiment ID
`exp-003-meowseum-reel-studio`

## Title
Turn a Meowseum product or journal page into a narrated vertical Reel through a
multi-agent source-to-story pipeline.

## Date
Started: 2026-07-22
Completed: —

## Class topic
Agentic source-to-video architecture (professor's pipeline pattern), applied to a
controlled real-world content library instead of an open-ended user upload.

## Objective
Build a browser app that takes one page from `themeowseum.pages.dev` (a collection
piece or a journal article), extracts its content into a structured source record,
and drives a chain of agents — source curator, character, location, concept,
outline + critic, shot + critic — to produce a 6-shot 9:16 Reel with generated
images and Thai narration, playable full-screen in the browser.

The point of the experiment is not the Reel. It is to find out whether **constraining
generation to an extracted real source** produces better, more inspectable output
than free-form prompting, and whether per-shot `source_basis` / `creative_addition`
tagging makes an agent chain auditable.

## Hypothesis
Written before building:

1. Grounding the story in an extracted source record will make the two critic
   stages cheap and effective, because "does this match the source?" is a
   checkable question, whereas "is this a good story?" is not.
2. Splitting each shot into `source_basis` (facts from the page) and
   `creative_addition` (invented) will expose hallucination without needing a
   separate fact-check agent.
3. The expensive, unreliable step will be **visual consistency of the cat across
   shots**, not story quality. Still-image generators drift on character identity.
   I expect this to be the failure that dominates the writeup.
4. A fixed brand protagonist (Cat the Curator) will produce more consistent output
   than a user-uploaded cat photo, because the reference is stable.

Being wrong on any of these is a useful result. Do not edit this section later.

## Success criteria
Concrete and checkable, decided up front.

- [ ] **C1 — Extraction.** Given a product URL and a journal URL from
      `themeowseum.pages.dev`, the source agent produces a structured record with
      title, Thai title, description, and at least one image URL, for both page
      types, with the host verified before fetch.
- [ ] **C2 — Grounding.** Every shot in a generated Reel carries a non-empty
      `source_basis` naming which extracted field it came from, or is explicitly
      marked `creative_addition`. Manual audit of one full 6-shot Reel finds zero
      shots that assert a source fact not present in the extracted record.
- [ ] **C3 — Commercial safety.** No generated narration or caption states a price,
      stock status, dimension, or shipping claim while `verified_for_marketing` is
      false. Tested with an adversarial prompt that asks for a price.
- [ ] **C4 — Playback.** The demo Reel (Mona Lisa / Cat the Curator / Thai / funny /
      6 shots) plays end to end full-screen at 9:16 with images and narration in
      the browser, in one run, without manual file shuffling.
- [ ] **C5 — Critic value.** For 3 outlines, the outline critic's revision is
      recorded alongside the original. At least one measurable improvement per the
      critic's own rubric is shown, or the critic is reported as low-value — either
      outcome counts as met, a null result is a result.
- [ ] **C6 — Cost.** One full Reel generation's API cost is measured and recorded,
      split text vs image.
- [ ] **C7 — Consistency comparison.** The same 6-shot Reel is generated twice —
      once with Cat the Curator, once with an uploaded cat photo as image reference.
      Both are graded 1–5 for cross-shot visual identity drift by a fixed rubric,
      and the two scores are reported. This is the direct test of hypothesis 4.

Out of scope for this experiment: video export/encoding, audio mixing, publishing
to any platform, user accounts, persistence beyond local files.

## Technology stack
| Component | Choice | Version | Why |
|---|---|---|---|
| Language | Python 3 (stdlib) backend + vanilla JS/CSS frontend | | Lightest route: a 6-shot 9:16 slideshow is CSS; no framework earns its cost |
| Framework | None | | Deliberate — see D-scope below |
| Model / API | Claude (all text agents) | claude-opus-4-8 / claude-sonnet-5 | Agent chain, outline + shot critics |
| Model / API | OpenAI images (`gpt-image-1`) | | Image generation, and image-reference editing for the uploaded-cat path |
| Audio | Browser `speechSynthesis` | native | Thai narration, zero key, zero cost, zero deps |
| Source | Committed HTML snapshots | | Repeatable tests, no network dependency in test runs |

Dependencies added beyond the standard library, and why each was necessary:

- _None yet. HTTP calls to both providers go through `urllib.request`; no SDK
  needed for a handful of endpoints. Each addition must be justified here first._

## Resolved decisions
| # | Decision | Choice | Consequence |
|---|---|---|---|
| D1 | Image generation | OpenAI `gpt-image-1` | Real images from day one; needs `OPENAI_API_KEY`; per-run cost feeds C6 |
| D2 | Thai narration | Browser `speechSynthesis` | Free and dependency-free; Thai voice availability is OS-dependent and is itself a recorded finding |
| D3 | Source fetching | Committed HTML snapshot of the demo pages | Extraction logic stays real; tests do not break when the live site changes. Snapshot date recorded next to the file |
| D4 | MVP scope | Collection piece → Reel, **plus** the user-cat-upload protagonist path | Directly stresses hypothesis 3 and 4. Journal extraction is still tested under C1 but does not need to reach a playable Reel |

Consequence of D4 + D1 together: the uploaded cat is passed to `gpt-image-1` as a
reference image on every shot. Cat-consistency (C7) becomes a **measured
comparison** — uploaded cat vs Cat the Curator — not a side observation.

Assumption proceeded under: the Reel is a **slideshow of stills + narration**, not
an encoded video file. If a real `.mp4` is required for the class, scope changes.

## Setup instructions
Prerequisites:

```text
Python 3.11+
A modern browser with a Thai speechSynthesis voice installed
Anthropic API access; OpenAI API access with gpt-image-1 enabled
```

Steps:

```bash
# 1. no install step — stdlib only
# 2. configure — copy ../../.env.example to .env and fill in values
# 3. run  — python -m src.server, then open http://localhost:8000
```

Environment variables required (names only — never values):

- `ANTHROPIC_API_KEY` — text agent calls (source curator, character, location,
  concept, outline + critic, shot + critic)
- `OPENAI_API_KEY` — `gpt-image-1` shot image generation and reference editing

## Implementation summary
_Not started. Definition committed before any source file exists._

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | Product extraction | `/products/09-mona-lisa/` | Structured record, title + Thai title + image | | |
| 2 | Journal extraction | one `/journal/` article | Structured record with sections + tips | | |
| 3 | Host guard | a non-Meowseum URL | Refused before fetch | | |
| 4 | Price safety | prompt asking narration to mention price | No price in output | | |
| 5 | Full Reel | Mona Lisa demo settings, Cat the Curator | 6 shots, all `source_basis` tagged, plays 9:16 | | |
| 6 | Cat consistency — brand | test 5 output, shots 1–6 | Drift graded 1–5 by rubric | | |
| 7 | Cat consistency — uploaded | same settings, uploaded cat photo as reference | Drift graded 1–5, compared against test 6 | | |
| 8 | Thai voice absent | browser with no Thai `speechSynthesis` voice | Degrades to captions, does not crash or speak Thai in a wrong-language voice silently | | |

How tests were run:

```bash
<command>
```

## Results
_Pending._

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| | | | |

## Lessons learned
_Pending._

## Reusable outputs
| Output | Type | Destination |
|---|---|---|
| | pattern / prompt / snippet / tool note | `knowledge/.../<file>.md` |

## Security considerations
- Secrets used: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` — names only in `.env.example`
- Secrets committed: **No** (confirm before completing)
- Sensitive or personal data handled: an optional user-uploaded cat photo. It is
  **uploaded to OpenAI** as an image reference — that is an outward data flow and
  the UI must say so before accepting a file. Stored under the experiment's
  `artifacts/`, git-ignored, never committed.
- Artifacts redacted before saving: n/a so far
- Third-party services data was sent to: Anthropic (extracted page text +
  generated prompts), OpenAI (image prompts + any uploaded cat photo)
- Residual risk: The Meowseum product pages carry provisional prices and specs.
  Narrating them would publish unconfirmed commercial claims. Guarded by C3 and a
  `verified_for_marketing` flag defaulting to false.

## Cleanup decision
- Proposed: —
- Reasoning:
- Keep list:
- Delete list:
- Approved by: — on YYYY-MM-DD
- Executed on: —
- Checklist completed: `templates/cleanup-checklist.md` — no

## Final status
`Active`

Index updated in `archive/experiment-index.md`: yes
