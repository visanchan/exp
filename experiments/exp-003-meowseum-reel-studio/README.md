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

Four modules, standard library only — no packages were installed.

| File | Role |
|---|---|
| `src/source_agent.py` | Host allowlist, snapshot loading, product/journal extraction into `SourceRecord` |
| `src/llm.py` | Text + image calls over `urllib`, provider selection, `CostMeter` |
| `src/pipeline.py` | The seven-stage agent chain, plus the deterministic `audit_shots` |
| `src/server.py` | `http.server` with five JSON routes and one SSE progress stream |
| `web/` | Source picker, progress terminal, shot review, 9:16 player |

**Divergence from the plan — text provider.** The definition assumed Claude for
the text agents. Only `OPENAI_API_KEY` was present in the environment, so
`llm.generate_text` selects a provider by which key exists: Anthropic when
available, OpenAI otherwise. All results below were produced on
`gpt-4o-mini`, and every run manifest records which provider served it. This
weakens nothing about C1–C4, but C5 (critic value) is a judgement about a
specific model and should be re-run on Claude before being generalised.

**The design decision that mattered most.** C3 is enforced by the shape of the
data, not by the prompt. `SourceRecord.transactional` holds price, stock,
shipping, weight and dimensions; `story_context()` omits that block entirely
while `verified_for_marketing` is false. No story agent is ever shown a number
it could narrate. The safety prompt in `pipeline.SAFETY` is a second layer, not
the mechanism. This is why the price cannot leak even if a model is talked into
trying: there is nothing in its context to leak.

## How to run

```bash
cd experiments/exp-003-meowseum-reel-studio
python src/server.py          # open http://localhost:8000
python -m unittest discover -s tests -t .
```

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | Product extraction | `/products/09-mona-lisa/` | Structured record, title + Thai title + image | Title, `โมนาลิซา`, room, No.013, material, care, museum label, 1 image | ✅ |
| 2 | Journal extraction | `/journal/05-why-cats-ignore-new-furniture/` | Record with sections + tips | 4 sections with headings and points, category, date, tags | ✅ |
| 3 | Host guard | 3 off-site URLs + a `file://` URL | Refused before any read | All refused; `extract()` raises on host, never reaches snapshot lookup | ✅ |
| 4 | Price quarantine | serialize entire story context, search it | No price, stock, weight or shipping string present | None of `890`, `฿`, `In stock`, `700 g`, `Free shipping` appear | ✅ |
| 5 | Full Reel | Mona Lisa / Curator / Thai / funny / 6 shots / medium | 6 images, audit clean, plays 9:16 | 6 PNGs at 1024×1536, audit clean, $0.2558, 3 min | ✅ |
| 6 | Cat consistency — brand | run `3b5e7e1d9135`, shots 1–6 | Drift graded 1–5 | **2/5** — see Results | ⚠️ |
| 7 | Cat consistency — uploaded | uploaded cat photo as reference | Drift graded, compared to test 6 | **NOT RUN** — no cat photo available to upload | ❌ |
| 8 | Thai voice absent | browser with no Thai voice | Falls back to captions | Code path written and reviewed; **not executed** in a voice-less browser | ⚠️ |
| 9 | Host guard, HTTP layer | `POST /api/reel` with `evil.test` | 400 before any work | `{"error": "refused: 'evil.test' is not 'themeowseum.pages.dev'"}` | ✅ |

How tests were run:

```bash
python -m unittest discover -s tests -t .     # 18 tests, all pass
python src/server.py                          # tests 5, 9 via the running app
```

## Results

Measured against the success criteria.

- **C1 — Extraction: met.** Both page types extract. 18 unit tests pass.
- **C2 — Grounding: met, but the criterion is weaker than it looked.** Every
  shot declared either a `source_basis` or a `creative_addition`, and the audit
  found no shot citing a field that does not exist. **However** — in the first
  planning run, shot 3 cited `fields.care` and narrated
  *"การข่วนเพิ่มสุขภาพอย่างมาก"* ("scratching greatly improves health"). The
  `care` field says only: mount within your cat's reach, brush off loose fibers.
  The shot cited a **real field name** while asserting a claim that field never
  makes. The audit passed it. Citing a field name is not the same as being
  supported by its contents, and only a value-level check catches the
  difference. This is the most useful finding in the experiment.
- **C3 — Commercial safety: met, structurally.** The adversarial test
  serializes the entire story context and asserts no price, stock string,
  weight or shipping claim survives. It does not, because the block is never
  passed. A regex sweep over narration, caption and image prompt is a second
  layer and found nothing in either run.
- **C4 — Playback: met.** One run produced six 1024×1536 PNGs, a manifest and a
  playable 9:16 slideshow with Thai narration, from one button, no manual file
  handling.
- **C5 — Critic value: met as a recorded null-ish result.** The outline critic
  produced generic scorecards ("the hook does not engage quickly enough") and
  vague changes ("revised the introduction to be snappier"). The shot critic was
  more useful: it shortened an over-long Thai narration line to fit five
  seconds, and claimed to have made prompts self-contained. Neither critic
  caught the two real defects — the invented health claim and the character
  drift. On `gpt-4o-mini` the critics are worth their small cost but are not
  load-bearing. Re-run on Claude before generalising.
- **C6 — Cost: met.** One 6-shot Reel at medium quality:
  **$0.2558** — $0.0038 text (7 calls, 8,519 in / 4,199 out) and $0.252 images.
  Images are 98.5% of the cost. Planning takes ~52s, images ~2min.
- **C7 — Consistency comparison: not met, half-run.** The brand-protagonist half
  ran; the uploaded-cat half did not, for want of a cat photo. See below.

### Hypothesis check

1. **Grounding makes critics cheap and effective — partly wrong.** Grounding
   made *auditing* cheap and effective; the deterministic audit is where the
   value showed up, not the critics.
2. **`source_basis` / `creative_addition` exposes hallucination — wrong as
   stated.** It exposes *unattributed* hallucination. It does not expose a
   hallucination wearing a valid citation, which is exactly what happened.
3. **Visual consistency will be the dominant failure — right, and worse than
   predicted.** Graded 2/5. Shot 1 shows a brown-and-white long-haired cat with
   a gold ribbon badge, scratching the corrugated *product*. Shot 4 shows a
   cream-orange cat with no badge, clawing a *real oil painting*. Both the
   character and the product identity drifted inside one Reel.

   The cause is visible in the prompts. Shot 1: *"a fluffy cat with distinct
   markings and a ribbon badge"*. Shot 3: *"a fluffy cat with playful eyes"*.
   "Distinct markings" is a placeholder **for** specificity rather than
   specificity itself, so each render invents its own. Shot 4 also drops the
   word *scratch* from "scratch painting", and the generator reverts to the
   famous artwork. The instruction in `_protagonist_rule` to "describe the same
   cat with identical markings" was followed in letter and missed in substance.
4. **Brand protagonist beats uploaded photo — untested.** Cannot be answered
   with only one arm of the comparison run.

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| Related-piece images leaked into the record | Mona Lisa's record listed Venus and Starry Night | A bare `<img>` sweep also caught the "more from this room" carousel | Fixed — restricted to `data-gallery-*` images; regression test added |
| Character drift across shots | Different cat in shots 1 and 4 | Prompts say "distinct markings" instead of naming them | **Open** — needs a literal character sheet, see next improvement |
| Product identity drift | Shot 4 shows a real oil painting, not the cardboard scratcher | "scratch painting" shortened to "painting" in one prompt | **Open** — same fix |
| Cited field, invented claim | Health claim attributed to `fields.care` | Audit checks that the field name exists, not that the value supports the sentence | **Open** — needs a value-level entailment check |
| `unittest discover` refused to run | `Start directory is not importable` | `tests/` had no `__init__.py` | Fixed |
| Console crash on Thai output | `UnicodeEncodeError: 'charmap'` | Windows console defaults to cp1252 | Worked around with `PYTHONIOENCODING=utf-8`; `server.py` is unaffected |

## Lessons learned

- **A citation is not evidence.** Requiring an agent to name its source field
  produces confident, well-formed, checkable-looking citations that can still
  sit on top of an invented claim. Name-level auditing catches sloppiness;
  it does not catch confabulation.
- **Withholding beats instructing.** The commercial-safety rule held because
  the data was absent, not because the prompt said no. Where a rule matters,
  delete the input rather than forbidding the output.
- **"Be consistent" is not a specification.** An instruction to describe the
  same cat every time was satisfied by repeating the phrase "distinct markings"
  — which specifies nothing. Consistency requires a literal shared string, not
  an instruction to be consistent.
- **Cost sits almost entirely in images.** 98.5% here. Optimising prompt tokens
  in a pipeline like this is effort spent on 1.5% of the bill.

## Reusable outputs
| Output | Type | Destination |
|---|---|---|
| Quarantine unverified data structurally instead of forbidding it in the prompt | pattern | `knowledge/reusable-patterns/` — to write |
| Field-name citation is not entailment | lesson | `knowledge/lessons-learned/` — to write |
| Character-sheet string for cross-shot image consistency | pattern | `knowledge/reusable-patterns/` — to write |
| Bilingual `data-bi` span extraction from an Astro site | snippet | `knowledge/code-snippets/` — to write |

## Next improvement (single best)

Replace the "describe the same cat" instruction with a **character sheet**: one
literal sentence generated once ("a long-haired brown-and-white cat with a white
chest blaze, amber eyes, and a small gold ribbon badge"), then string-substituted
verbatim into every image prompt, with the shot critic rejecting any prompt that
does not contain it word for word. The same treatment for the product noun
phrase ("the corrugated cardboard Mona Lisa scratch panel"). This targets both
open drift defects with one mechanism, and makes C7 worth running.

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
