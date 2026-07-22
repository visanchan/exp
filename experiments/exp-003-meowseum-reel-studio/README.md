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

> **Scope change, 2026-07-23.** MP4 export was requested after the fact and is
> now built (D6). The line above is left as written — it is what was agreed
> before the work, and the criteria list is not backdated. Export has no
> pre-registered criterion; it is reported as an addition, not as a success
> against a target set in advance. Publishing to a platform remains out of
> scope: the file is handed to the user, not uploaded anywhere.

## Technology stack
| Component | Choice | Version | Why |
|---|---|---|---|
| Language | Python 3 (stdlib) backend + vanilla JS/CSS frontend | | Lightest route: a 6-shot 9:16 slideshow is CSS; no framework earns its cost |
| Framework | None | | Deliberate — see D-scope below |
| Model / API | OpenAI (all text agents) | `gpt-5.6-sol` | Agent chain, outline + shot critics. Was `gpt-4o-mini`; see D7 |
| Model / API | OpenAI images (`gpt-image-2`) | at 864x1536 | Image generation, and image-reference editing for the uploaded-cat path. Was `gpt-image-1` at 1024x1536; see D8 |
| Audio | OpenAI `gpt-4o-mini-tts-2025-12-15` → MP3 per shot | pinned snapshot | Thai narration that works on any machine; browser `speechSynthesis` kept as fallback (see D5, D8) |
| Video export | ffmpeg, **discovered not installed** | n4.4.4 (bundled with Krita) | Only practical way to emit an H.264/AAC MP4 the platforms accept |
| Source | Committed HTML snapshots | | Repeatable tests, no network dependency in test runs |

Dependencies added beyond the standard library, and why each was necessary:

- _No packages. HTTP calls to both providers go through `urllib.request`; no SDK
  needed for a handful of endpoints. Each addition must be justified here first._
- **ffmpeg — an external binary, not a package (added 2026-07-23 for D6).**
  What it does: encodes the stills and narration MP3s into one H.264/AAC MP4.
  Why a built-in was insufficient: the standard library cannot encode H.264,
  and no pure-Python encoder produces a file Instagram or TikTok will accept.
  Weight: nothing is installed. The binary is *discovered* — `FFMPEG_BINARY`,
  then PATH, then a short list of places a Windows machine usually already has
  one. On this machine it was found inside Krita. If nothing is found, export
  reports itself unavailable in `/api/health`, the button is disabled with the
  reason shown, and every other part of the app is unaffected.

## Resolved decisions
| # | Decision | Choice | Consequence |
|---|---|---|---|
| D1 | Image generation | OpenAI `gpt-image-1` | Real images from day one; needs `OPENAI_API_KEY`; per-run cost feeds C6 |
| D2 | Thai narration | Browser `speechSynthesis` | Free and dependency-free; Thai voice availability is OS-dependent and is itself a recorded finding. **Superseded by D5** |
| D3 | Source fetching | Committed HTML snapshot of the demo pages | Extraction logic stays real; tests do not break when the live site changes. Snapshot date recorded next to the file |
| D4 | MVP scope | Collection piece → Reel, **plus** the user-cat-upload protagonist path | Directly stresses hypothesis 3 and 4. Journal extraction is still tested under C1 but does not need to reach a playable Reel |
| D5 | Narration, **revised 2026-07-22**, supersedes D2 | OpenAI `gpt-4o-mini-tts`, one MP3 per shot, written into the run folder | Narration stops depending on an OS Thai voice being installed, so the Reel sounds the same on any machine. Adds ~$0.004/Reel (1.5% of a low-quality run, 6% of the previous medium-quality run). Audio becomes an inspectable artifact that can be replayed and graded like the images. `speechSynthesis` is kept as the fallback when a line fails or the voice is set to "none" |

| D8 | Image + narration models, **decided 2026-07-23** | `gpt-image-2` at **864x1536**, a true 9:16 frame; narration pinned to `gpt-4o-mini-tts-2025-12-15` | The stills are now generated at the aspect they are played and exported at, so the centre-crop stops discarding ~16% of every frame. Model and size are coupled: `gpt-image-1` takes a fixed size list and 400s on 864x1536. **There is no newer TTS model** — `gpt-audio*` reject `/v1/audio/speech` entirely, `tts-1*` are older; pinning the dated snapshot is the only available move and buys reproducibility |
| D7 | Text model, **decided 2026-07-23** | `gpt-5.6-sol` for all seven text agents; single provider (OpenAI); the Anthropic branch deleted, not left dormant | One key runs the whole pipeline. Removes a code path that had never executed and would have 400'd on first use. Costs an unknown amount — see the C6 caveat below — and roughly doubles planning time |
| D6 | MP4 export, **added 2026-07-23** | ffmpeg discovered on the machine; per-shot segments encoded at 1080x1920, then stream-copied together | The Reel becomes a file that can be posted, which was the point of making it. Costs nothing per export and can be retried freely. Introduces the app's first non-Python dependency, and makes export machine-dependent — a clone without ffmpeg still runs everything else |

Consequence of D4 + D1 together: the uploaded cat is passed to `gpt-image-1` as a
reference image on every shot. Cat-consistency (C7) becomes a **measured
comparison** — uploaded cat vs Cat the Curator — not a side observation.

Assumption proceeded under: the Reel is a **slideshow of stills + narration**, not
an encoded video file. If a real `.mp4` is required for the class, scope changes.

## Setup instructions
Prerequisites:

```text
Python 3.11+
A modern browser
OpenAI API access with gpt-5.6-sol, gpt-image-1 and gpt-4o-mini-tts enabled
```

A Thai `speechSynthesis` voice is no longer required — narration is generated
server-side as MP3 (D5). It is still used as a fallback, so a machine that has
one degrades better than one that does not.

Steps:

```bash
# 1. no install step — stdlib only
# 2. configure — copy ../../.env.example to .env and fill in values
# 3. run  — python -m src.server, then open http://localhost:8000
```

Environment variables required (names only — never values):

- `OPENAI_API_KEY` — **the only key required.** Serves the seven text agents
  (`gpt-5.6-sol`), image generation and reference editing (`gpt-image-1`), and
  narration (`gpt-4o-mini-tts`)
- `OPENAI_TEXT_PRICE_INPUT` / `OPENAI_TEXT_PRICE_OUTPUT` — optional, USD per
  million tokens. Cost reporting only; unset means a run reports text tokens
  but withholds the dollar figure rather than guessing (see C6)
- `FFMPEG_BINARY` — optional, path to an existing `ffmpeg.exe` for MP4 export

`ANTHROPIC_API_KEY` is no longer read by this experiment (D7).

## Implementation summary

Four modules, standard library only — no packages were installed.

| File | Role |
|---|---|
| `src/source_agent.py` | Host allowlist, snapshot loading, product/journal extraction into `SourceRecord` |
| `src/llm.py` | Text, image and speech calls over `urllib`, provider selection, `CostMeter` |
| `src/pipeline.py` | The seven-stage agent chain, the narration render, plus the deterministic `audit_shots` |
| `src/export.py` | ffmpeg discovery, capability probe, per-shot segments, concat to `reel.mp4` |
| `src/server.py` | `http.server` with six JSON routes and one SSE progress stream |
| `web/` | Source picker, progress terminal, shot review, 9:16 player, export button |

**Divergence from the plan — text provider.** The definition assumed Claude for
the text agents. That never happened. Only `OPENAI_API_KEY` was ever present, so
every result below `gpt-4o-mini` — and on 2026-07-23 the experiment moved to a
single provider deliberately (D7), settling on `gpt-5.6-sol`. C5's original
"re-run on Claude before generalising" caveat is therefore closed as
**won't-do**; it was re-run on a stronger OpenAI model instead, and the answer
is in the D7 amendment below.

Deleting the Anthropic branch also removed a latent bug. It had never executed,
so nothing had ever checked it: it sent `temperature` and a `max_tokens` field
name that the current Claude models reject, and its entry in the pricing table
carried Sonnet rates while the code defaulted to a different model. Untested
fallback code is not a fallback — it is a second, unverified way to fail.

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

The startup banner reports which providers and which ffmpeg were found. After a
Reel finishes, **⬇ Export MP4** writes `artifacts/<run>/reel.mp4` (1080x1920,
H.264/AAC) and offers it as a download — that is the file to post. If ffmpeg is
not found the button is disabled and says why; point `FFMPEG_BINARY` at an
existing `ffmpeg.exe` to enable it:

```bash
FFMPEG_BINARY="C:/Program Files/Krita (x64)/bin/ffmpeg.exe" python src/server.py
```

Export re-runs are free — it reads the run folder, calls no API, and overwrites
`reel.mp4` in place. A run generated by an earlier server session can still be
exported, because the manifest is read from disk rather than memory.

## Test cases
| # | Case | Input / setup | Expected | Actual | Pass |
|---|---|---|---|---|---|
| 1 | Product extraction | `/products/09-mona-lisa/` | Structured record, title + Thai title + image | Title, `โมนาลิซา`, room, No.013, material, care, museum label, 1 image | ✅ |
| 2 | Journal extraction | `/journal/05-why-cats-ignore-new-furniture/` | Record with sections + tips | 4 sections with headings and points, category, date, tags | ✅ |
| 3 | Host guard | 3 off-site URLs + a `file://` URL | Refused before any read | All refused; `extract()` raises on host, never reaches snapshot lookup | ✅ |
| 4 | Price quarantine | serialize entire story context, search it | No price, stock, weight or shipping string present | None of `890`, `฿`, `In stock`, `700 g`, `Free shipping` appear | ✅ |
| 5 | Full Reel | Mona Lisa / Curator / Thai / funny / 6 shots / medium | 6 images, audit clean, plays 9:16 | 6 PNGs at 1024×1536, audit clean, $0.2558, 3 min | ✅ |
| 6 | Cat consistency — brand | run `3b5e7e1d9135`, shots 1–6 | Drift graded 1–5 | **2/5** — see Results | ⚠️ |
| 6b | Cat consistency — repeat | run `3a9fef0f39b0`, same settings | Reproduce or refute test 6 | **2/5** — drift reproduced, different symptom | ⚠️ |
| 7 | Cat consistency — uploaded | uploaded cat photo as reference | Drift graded, compared to test 6 | **NOT RUN** — no cat photo available to upload | ❌ |
| 8 | Thai voice absent | browser with no Thai voice | Falls back to captions | Code path written and reviewed; **not executed** in a voice-less browser. Largely moot after D5 — it is now the fallback, not the primary path | ⚠️ |
| 9 | Host guard, HTTP layer | `POST /api/reel` with `evil.test` | 400 before any work | `{"error": "refused: 'evil.test' is not 'themeowseum.pages.dev'"}` | ✅ |
| 10 | Real TTS call | one Thai line, voice `alloy` | Valid MP3 back | 55,296 bytes, `FF F3` MPEG frame sync, Thai text round-tripped | ✅ |
| 11 | Bad voice rejected | `POST /api/reel` with `"voice": "darth-vader"` | 400 before any paid call | `{"error": "unknown voice 'darth-vader'"}` | ✅ |
| 12 | MP3 served | `GET /artifacts/<run>/narration-01.mp3` | 200, audio MIME | `200 audio/mpeg`, 55,296 bytes | ✅ |
| 13 | Narration failure isolated | stubbed provider error on shot 1 | Run continues, shot degrades | Shot 1 `audio_file=None` with the error recorded, shots 2+ still narrated | ✅ |
| 14 | Full Reel with audio | run `178ebb912ad7`, low quality | 6 images + 6 MP3s, audit clean | 6 PNGs, 6 MP3s, audit clean, $0.0743, 207s | ✅ |
| 15 | MP4 export | `POST /api/export/178ebb912ad7` | Playable H.264/AAC MP4 | 6 shots, 1080x1920, 40.2s, 1.51 MB, `libopenh264`, 20s to encode | ✅ |
| 16 | Export contents | `ffprobe` + `volumedetect` + two extracted frames | Real video and audible narration | `h264` 1080x1920 + `aac` 44100 Hz; mean −22.3 dB, peak −6.1 dB; frames show the shot images correctly cropped to 9:16 | ✅ |
| 17 | Export path traversal | `POST /api/export/..` and `..%2f..` | Refused | `404 {"error": "unknown run"}` for both | ✅ |
| 18 | No ffmpeg | `FFMPEG_BINARY` pointing nowhere | Reported, not crashed | `available: false` with a reason; button disabled, rest of the app unaffected | ✅ |
| 19 | Shot missing its image | stubbed encoder, shot 2 has no image | Left out and reported | `shots_encoded: 1`, `shots_skipped: [{shot: 2, why: "no image file"}]` | ✅ |
| 20 | Model ID is real | list `/v1/models` with the live key | `gpt-5.6-sol` exists | Present, alongside `gpt-5.6-luna` / `-terra`; 131 models visible | ✅ |
| 21 | `max_tokens` on `gpt-5.6-sol` | old payload shape | — | `400 Unsupported parameter: 'max_tokens' ... Use 'max_completion_tokens'` | ✅ |
| 22 | `temperature` on `gpt-5.6-sol` | 0.8 / 0.2 / 0.0 / 1.0 / omitted | — | 0.8, 0.2 and 0.0 all `400 ... Only the default (1) value is supported`; 1.0 and omitted OK | ✅ |
| 23 | Corrected request shape | stubbed transport, 21 assertions | No `max_tokens`, no `temperature` | Payload carries `max_completion_tokens` + `reasoning_effort`, neither banned field | ✅ |
| 24 | Empty completion | `content: ""`, `finish_reason: length` | Clear error, not a parse crash | `LLMError: model returned no text (finish_reason='length'); raise max_tokens or lower effort` | ✅ |
| 25 | Unpriced text model | no price env vars | Tokens reported, dollars withheld | `text_usd: null`, `text_priced: false`, `total_is_complete: false`; total still counts images + narration | ✅ |
| 26 | Full Reel on `gpt-5.6-sol` | run `fbe3581b6dd5`, settings identical to run 14 | 6 images + 6 MP3s, audit clean | 6 PNGs, 6 MP3s, audit clean, 397s | ✅ |
| 27 | Character consistency, `gpt-5.6-sol` | run `fbe3581b6dd5`, shots 1 and 5 | Drift graded 1–5 | **4/5** — same cat, same markings, same badge. Was 2/5 | ✅ |
| 28 | Narration budget, `gpt-5.6-sol` | measure all six MP3s | — | 6/6 still overrun (6.1–7.8s vs 5s), critic again claimed it had shortened them | ⚠️ |
| 29 | `gpt-image-2` parameter surface | deliberate 400s on `quality` / `size` | Enumerate valid values without paying to generate | quality `low\|medium\|high\|auto` (unchanged); size only "both sides divisible by 16" — no fixed list | ✅ |
| 30 | Newer TTS model exists? | `gpt-audio`, `gpt-audio-1.5`, `gpt-audio-mini`, `tts-1-hd` on `/v1/audio/speech` | — | All `gpt-audio*` → `Invalid URL (POST /v1/audio/speech)`; `tts-1-hd` works but is older. **`gpt-4o-mini-tts` is the newest** | ✅ |
| 31 | Native 9:16 generation | one `gpt-image-2` image at 864x1536 | Exact 9:16, no crop needed | Asked 864x1536, got 864x1536, ratio 0.5625 | ✅ |
| 32 | Size is coupled to model | 864x1536 on `gpt-image-1` edits | — | `400 Invalid size '864x1536'. Supported sizes are 1024x1024, 1024x1536, 1536x1024` | ✅ |
| 33 | Uploaded-cat path exercised | `/v1/images/edits` with `gpt-image-2` + a reference PNG | Works | 864x1536 returned. **First time this branch has ever run** — test 7 had left it unexecuted | ✅ |
| 34 | Full Reel on the new media stack | run `57e36f458255`, settings as run 26 | 6 images + 6 MP3s, audit clean | 6 PNGs **all 864x1536, ratio 0.5625**, 6 MP3s, audit clean, 454s | ✅ |
| 35 | Product identity after renderer upgrade | run `57e36f458255`, shots 1 and 5 | — | Still a real framed oil painting, not the cardboard scratch panel. Character sheet still holds. **Better renderer did not fix it** | ⚠️ |

How tests were run:

```bash
python -m unittest discover -s tests -t .     # 68 tests, all pass
python src/server.py                          # tests 5, 9, 11, 12, 14, 15, 17, 26, 34 via the running app
```

Tests 29–33 are API-surface probes run directly against the live endpoints.
Two of them cost nothing: an invalid `quality` or `size` is rejected before any
image is generated, which is a cheap way to enumerate an unfamiliar model's
accepted values instead of guessing them.

Tests 10–14 were run after the D5 narration change, 15–19 after the D6 export
change. The stubbed cases (13, 19) replace the provider or the encoder, because
neither a forced API failure nor a forced encoder failure was worth the real
call; the encoder itself is covered by tests 15 and 16 on a real run.

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
- **C6 — Cost: met on `gpt-4o-mini`, now partially open.** The figures below
  stand for the runs that produced them. After D7 the text model's list price
  is not known to this repository, and the meter refuses to invent one: a run
  reports its text tokens in full and marks the dollar figure `text_priced:
  false`, with `total_usd` covering images and narration only and flagged
  `total_is_complete: false`. Set `OPENAI_TEXT_PRICE_INPUT` /
  `OPENAI_TEXT_PRICE_OUTPUT` in `.env` (USD per million tokens) to close this.
  A wrong number here would be worse than no number, because a cost criterion
  reporting a confident figure looks measured.
- **C6 — original measurement.** One 6-shot Reel at medium quality:
  **$0.2558** — $0.0038 text (7 calls, 8,519 in / 4,199 out) and $0.252 images.
  Images are 98.5% of the cost. Planning takes ~52s, images ~2min.
- **C7 — Consistency comparison: not met, half-run.** The brand-protagonist half
  ran; the uploaded-cat half did not, for want of a cat photo. See below.

### Amendment — narration moved to OpenAI TTS (2026-07-22)

Recorded after the results above, which were produced on the browser-speech
build. Nothing above was rewritten.

Run `178ebb912ad7`: Mona Lisa / Curator / Thai / funny / 6 shots / **low**
image quality / voice `alloy`. Six images, six MP3s, audit clean, 207 seconds.

| | Old build (medium images) | This run (low images) |
|---|---|---|
| Text | $0.0038 | $0.0040 |
| Images | $0.2520 | $0.0660 |
| Narration | $0 (browser) | **$0.0044 estimated**, 6 calls, 291 characters |
| Total | $0.2558 | $0.0743 |

Narration is ~6% of a medium-quality Reel and ~6% of this low-quality one — it
does not change where the money goes. Images still dominate. The narration
figure is an estimate: `gpt-4o-mini-tts` bills per token, and the meter counts
characters against the provider's published per-minute figure. Treat it as an
order of magnitude, not an invoice.

**What the change exposed.** With browser speech the narration was inaudible on
this machine, so nobody could hear that the lines do not fit. The generated
MP3s have durations:

| Shot | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Approx. seconds | 7.2 | 5.0 | 5.2 | 6.1 | 5.4 | 8.8 |

Four of six lines overrun the 5-second budget the shot writer was given, and
shot 6 by 76%. The shot critic's explicit job includes "any narration too long
to read in its duration" — it passed all six. This is the same failure shape as
the character drift: the critic asserts a check it does not perform, and until
the output became observable, nothing contradicted it. The player now holds each
shot for `max(planned, audio length)` so lines are not cut mid-sentence, which
stretches a nominal 30-second Reel to about 38 seconds. That is a workaround at
playback time, not a fix at writing time.

### Amendment — MP4 export (2026-07-23)

Requested after the narration change; no criterion was set in advance, so this
is reported as an addition rather than a pass.

Run `178ebb912ad7` exports to **1080x1920 H.264/AAC, 40.2 seconds, 1.51 MB, in
20 seconds** on `libopenh264`. Verified by `ffprobe` (streams and duration),
`volumedetect` (mean −22.3 dB, peak −6.1 dB — the narration is present, not a
silent track), and two frames pulled from the finished file at 3s and 34s,
which show the shot images cropped to 9:16 the same way the player crops them.

Three things worth recording:

- **Nothing was installed.** ffmpeg was already on the machine inside Krita.
  Discovery beats installation for a disposable experiment: the export is a
  capability the app reports, not a requirement it imposes. A clone without
  ffmpeg loses the button and nothing else.
- **The bundled build has no `libx264`.** It has `libopenh264`, which is a
  weaker encoder but still emits H.264 in MP4 — what the platforms actually
  check. Preferring `libx264` when present and falling back is one line and
  avoids a "works on my machine" failure.
- **The 40.2-second duration is the narration overrun made concrete.** Six
  shots planned at 5 seconds should be 30. The export honours the same
  `max(planned, spoken)` rule as the player, so the too-long lines are now
  visible as a third of extra runtime in a file — which for a platform with a
  hard length limit would matter.

### Amendment — text model moved to `gpt-5.6-sol` (2026-07-23, D7)

Run `fbe3581b6dd5`: same source, settings and image quality as run
`178ebb912ad7`, changing only the text model. This is the closest thing the
experiment has to a controlled comparison, so it is reported as one.

| | `gpt-4o-mini` (`178ebb912ad7`) | `gpt-5.6-sol` (`fbe3581b6dd5`) |
|---|---|---|
| Planning + render time | 207 s | 397 s |
| Text calls | 7 | 7 |
| Input tokens | 8,604 | 11,626 |
| Output tokens | 4,448 | 13,105 (3,645 of them reasoning) |
| Audit | clean | clean |
| Cross-shot character consistency | **2/5** | **4/5** |
| Narration lines over budget | 6/6 | 6/6 |

**Character consistency: substantially fixed, and by the mechanism the previous
writeup predicted.** The "next improvement" proposed a literal character-sheet
string substituted verbatim into every image prompt. `gpt-5.6-sol` did that on
its own, unprompted — all six image prompts open with the identical clause
naming a white short-haired cat with a black patch above the left ear, a black
tail, amber eyes and a dark red curator's ribbon. The rendered shots 1 and 5
show recognisably the same animal, against run 1's tabby-then-anthropomorphic-
tabby-in-tweed. Graded 4/5 rather than 5/5 because pose and framing still vary
more than a single shoot would.

The interesting part is that this was a **capability difference, not an
instruction difference** — `_protagonist_rule` is byte-identical between the two
runs. The weaker model satisfied "describe the same cat in every prompt" with
the placeholder phrase *"distinctive stripes"*; the stronger one produced an
actual sheet. So "be consistent" is still not a specification (the earlier
lesson holds), but a strong enough model will supply the missing specification
itself. That is worth knowing and is not something the earlier runs could show.

**Product identity: still drifts.** Shot 1 renders the corrugated cardboard
scratch panel correctly; shot 5 renders a real framed oil painting. Same defect
as run 1's shot 4, unfixed. The character sheet covers the cat; nothing pins the
product noun phrase.

**Narration length: no better, slightly worse.** All six lines overrun the
five-second budget (6.1–7.8 s, mean 7.1 s vs 6.3 s on `gpt-4o-mini`). And the
shot critic again reported in its own changes list that it had *"shortened some
narration lines so they can be spoken comfortably within five seconds"* — in
Thai this time, on a stronger model, and still false for all six lines.

That is the sharpest result of the whole experiment. **The critic's false
self-report survived a model upgrade.** Two models, two languages, the same
fabricated claim about the same check. It is not a weak-model artifact; it is
what asking a generator to audit itself produces. Only the deterministic
`audit_shots` ever caught anything, and it cannot see durations — a length check
against the narration string is a five-line function and would have caught all
twelve failures across both runs.

**Unexpected: the image prompts switched to Thai.** Narration language is Thai,
and `gpt-5.6-sol` carried that into the image prompts, which the previous model
kept in English. `gpt-image-1` rendered them correctly, so this is not currently
a defect — but it is undocumented behaviour drift that nothing in the pipeline
asked for or checks, and the English `STYLE` suffix is now appended to a Thai
prompt.

### Amendment — media models (2026-07-23, D8)

Run `57e36f458255`, identical settings to `fbe3581b6dd5`, changing only the
image model and size.

- **Every still is now natively 9:16** (864x1536, ratio 0.5625, all six
  verified from the PNG headers). The export's centre-crop, which previously
  threw away about 16% of each frame's width, is now a no-op. It is deliberately
  kept rather than removed — it is still what makes older 2:3 runs export
  correctly.
- **The uploaded-cat path ran for the first time.** `/v1/images/edits` with
  `gpt-image-2` and a reference image returned a correct 864x1536 frame. C7 has
  been "not met, half-run" since the beginning because that arm had never been
  executed; the mechanism is now known to work, and only a cat photo stands
  between this experiment and an actual C7 answer.
- **The renderer upgrade did not fix product drift.** Shots 1 and 5 both show a
  real framed oil painting instead of the corrugated cardboard scratch panel.
  The cat is consistent across both. Since the character sheet is in the prompt
  and the product noun phrase is not, and since a materially better renderer
  changed nothing here, this is now confirmed as a **prompt defect, not an image
  defect** — which is what makes it fixable by the audit change proposed below.
- **No newer narration model exists.** Recorded because "use the newest" is the
  obvious instinct and the answer was not obvious: the `gpt-audio*` family is
  not a speech-synthesis family at all and rejects the endpoint.

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

   **Reproduced in a second run** (`3a9fef0f39b0`, identical settings), with a
   different symptom and the same cause. Shot 1: a four-legged tabby wearing a
   white ribbon badge in front of the corrugated scratch panel. Shot 5: an
   *anthropomorphic* tabby standing upright in a tweed jacket and wire glasses,
   no badge, with the product gone from the frame entirely — replaced by a
   miniature chair and an abstract print. Prompts 1 and 3 carry "Cat the
   Curator, a sleek tabby cat with a ribbon badge"; prompt 5 is only "Cat the
   Curator feigns shock at the playful act of Playful Cat, then smirks". The
   shot critic had explicitly reported that it "made all prompts
   self-contained". It had not, and nothing checked the claim.

   Two runs, two grades of 2/5, one mechanism: the character description is
   present in some prompts and absent from others, and whatever is absent gets
   reinvented. Run 1 lost the coat; run 2 lost the body plan.

   **The audit called both runs clean.** It reads narration, caption and image
   prompt text, so visual drift is structurally invisible to it. A text-level
   grounding audit says nothing about whether the images tell one story — a real
   boundary on what this technique buys.
4. **Brand protagonist beats uploaded photo — untested.** Cannot be answered
   with only one arm of the comparison run.

## Problems encountered
| Problem | Symptom | Root cause | Resolution / status |
|---|---|---|---|
| Related-piece images leaked into the record | Mona Lisa's record listed Venus and Starry Night | A bare `<img>` sweep also caught the "more from this room" carousel | Fixed — restricted to `data-gallery-*` images; regression test added |
| Character drift across shots | Different cat in shots 1 and 4 | Prompts say "distinct markings" instead of naming them | **Open** — needs a literal character sheet, see next improvement |
| Product identity drift | Shot 4 shows a real oil painting, not the cardboard scratcher | "scratch painting" shortened to "painting" in one prompt | **Open** — same fix |
| Cited field, invented claim | Health claim attributed to `fields.care` | Audit checks that the field name exists, not that the value supports the sentence | **Open** — needs a value-level entailment check |
| Narration inaudible on the author's machine | Silent playback, Thai text on screen only | No Thai `speechSynthesis` voice installed in Windows | Fixed by D5 — narration generated server-side as MP3 |
| Narration overruns its shot | 4 of 6 lines longer than the planned 5s, worst 8.8s | The shot writer is told a word budget and does not honour it; the shot critic claims to check this and does not | **Open** — worked around in the player (`max(planned, audio)`); the real fix is a length check on the narration string before it is spoken |
| Every text call 400'd after the model swap | `Unsupported parameter: 'max_tokens'`, then `temperature does not support 0.8` | `gpt-5.6-sol` renamed the output-budget field and accepts only the default temperature; the payload was written for `gpt-4o` | Fixed — `max_completion_tokens`, no `temperature`, `reasoning_effort` as the replacement lever. Both confirmed against the live API before the rewrite, and pinned by tests 21–23 |
| Stage budgets became a truncation risk | — (caught before it bit) | `max_completion_tokens` covers reasoning **and** visible output; the smallest stage allowed 1,200 for both | Fixed — stage budgets raised to 8k–20k, and an empty completion now raises a clear error instead of a confusing JSON parse failure |
| Text cost no longer measurable | `text_usd` would have been computed at `gpt-4o-mini` rates | The pricing table was keyed by provider, not model, so a model swap silently kept the old rates | Fixed — rates default to unset; runs report tokens and flag the dollar total incomplete. **Open**: needs the real list price to close C6 |
| Image prompts switched language | Thai image prompts on the `gpt-5.6-sol` run | Narration language bled into the prompt-writing stage; nothing constrains prompt language | **Open** — harmless so far (`gpt-image-1` rendered them fine), but unrequested and unchecked |
| First export never finished | ffmpeg ran past a 10-minute timeout on shot 1 | `-shortest` does not end a `-loop 1` still when a `filter_complex` is in the graph, so the video stream looped forever | Fixed — measure the narration length from ffmpeg's own header dump and pass an explicit `-t`. Per-command timeout also cut to 3 minutes so a loop surfaces fast |
| Concat step could not find its segments | `Impossible to open 'artifacts\<run>\export\artifacts/<run>/export/seg-01.mp4'` | The concat demuxer resolves list entries relative to the list file's directory; the list held paths relative to the working directory instead | Fixed — the list holds bare filenames |
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
  in a pipeline like this is effort spent on 1.5% of the bill. Adding TTS
  narration did not move this: it is ~6% of a Reel.
- **An output nobody can perceive is an output nobody checks.** The narration
  lines were 40% over budget from the first run, and it took making them
  *audible* to notice, because the browser was silently not speaking them.
  Every unrendered output in a pipeline is an unaudited one.
- **Discover the binary, do not require it.** Adding ffmpeg as a hard
  prerequisite would have made the whole app un-runnable on a machine without
  it. Probing for it, reporting the answer through `/api/health`, and disabling
  one button costs a few lines and keeps everything else working. Optional
  capability beats mandatory dependency for anything a clone might not have.
- **A defect you can only measure is a defect you argue about; a defect you can
  watch is a defect you fix.** The narration overrun was a table of durations
  after the TTS change, easy to note and defer. As 40 seconds of video where 30
  was planned, it is obvious.
- **A model upgrade fixed the defect that needed knowledge, not the one that
  needed a check.** The same prompt that got a placeholder ("distinctive
  stripes") from the weak model got a real character sheet from the strong one —
  capability closed that gap for free. The narration-length defect did not
  move, because no model grades its own output against a stopwatch. Upgrade to
  buy judgement; write a check to buy a guarantee.
- **Untested fallback code is not a fallback.** The Anthropic branch looked like
  resilience and would have failed on its first real call — wrong parameter
  names, wrong pricing. It survived because no key ever selected it, so no test
  ever ran it. A second path you cannot demonstrate is a liability.
- **Refuse to price what you cannot price.** The cost meter would happily have
  reported the new model's tokens at the old model's rates, and the number would
  have looked exactly as authoritative as a correct one. Reporting "unpriced"
  costs a line of UI and keeps C6 honest.
- **The same critic failed the same way twice.** It claimed prompts were
  self-contained when they were not, and claimed narration fit its duration
  when it did not. A critic's report of its own work is not evidence that the
  work happened; only a deterministic check outside the model is.

## Reusable outputs
| Output | Type | Destination |
|---|---|---|
| Quarantine unverified data structurally instead of forbidding it in the prompt | pattern | `knowledge/reusable-patterns/` — to write |
| Field-name citation is not entailment | lesson | `knowledge/lessons-learned/` — to write |
| Character-sheet string for cross-shot image consistency | pattern | `knowledge/reusable-patterns/` — to write |
| Bilingual `data-bi` span extraction from an Astro site | snippet | `knowledge/code-snippets/` — to write |
| An output nobody can perceive is an output nobody checks | lesson | `knowledge/lessons-learned/` — to write |
| Stills + per-shot audio → one MP4 with ffmpeg, no packages | snippet | `knowledge/code-snippets/` — to write |
| Discover an optional binary and report it as a capability | pattern | `knowledge/reusable-patterns/` — to write |

## Next improvement (single best)

**Superseded 2026-07-23.** The character-sheet half of the improvement below was
delivered for free by the D7 model upgrade — `gpt-5.6-sol` writes and repeats a
literal sheet without being asked (see the D7 amendment). What remains is the
half a model will not do for you.

**Extend `audit_shots` with two deterministic value-level checks**, both
sub-ten-line functions, both catching defects that have now survived two models
and four runs:

1. **Narration length.** Estimate speaking time from the narration string and
   flag any shot over its `duration_seconds`. 12 of 12 lines across both runs
   would have been caught; the shot critic claimed to have fixed them both
   times and had not.
2. **Product noun phrase.** Require every `image_prompt` to contain the piece's
   exact name, the way the cat's description now recurs. Catches the shot-5 oil
   painting and run 1's shot 4.

Both go in the audit, not the critic — the whole experiment's evidence is that
the deterministic audit is the only stage that has ever caught anything, and the
critic's report of its own work has never once been trustworthy.

Original text, kept because its prediction was tested: *replace the "describe
the same cat" instruction with a character sheet, string-substituted verbatim
into every image prompt, with the shot critic rejecting any prompt that does not
contain it word for word — plus the same treatment for the product noun phrase.*

## Security considerations
- Secrets used: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` — names only in `.env.example`
- Secrets committed: **No** (confirm before completing)
- Sensitive or personal data handled: an optional user-uploaded cat photo. It is
  **uploaded to OpenAI** as an image reference — that is an outward data flow and
  the UI must say so before accepting a file. Stored under the experiment's
  `artifacts/`, git-ignored, never committed.
- Artifacts redacted before saving: n/a so far
- Exported MP4s stay local. `artifacts/` is git-ignored, and the export route
  neither uploads nor calls any API — it reads the run folder and writes a file.
  A Reel built from an uploaded cat photo produces an MP4 of that cat; it is the
  user's to share or not.
- Third-party services data was sent to: **OpenAI only** (extracted page text,
  generated prompts, narration text, and any uploaded cat photo). Anthropic
  received nothing — the branch was never exercised and is now deleted (D7). Narration text is generated from the quarantined story context, so
  the commercial fields are not in it — the same withholding that protects C3
  protects this outward flow.
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
