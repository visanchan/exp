"""The Reel pipeline: source record in, shot list out.

Chain order, each stage seeing only what it needs:

    curate -> characters -> locations -> concepts -> outline -> outline critic
           -> shots -> shot critic -> images

Two things make the chain auditable rather than merely plausible:

*   Every stage is fed ``record.story_context()``, never the raw record, so the
    quarantined commercial fields are structurally out of reach.
*   Every shot must declare ``source_basis`` (field names it drew on) and
    ``creative_addition`` (what was invented). ``audit_shots`` checks the cited
    names against the record's ``allowed_basis`` and flags any that do not
    exist, which catches a shot asserting a fact the page never made.

Standard library only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import llm
from source_agent import SourceRecord

Progress = Callable[[str, str], None]


def _noop(stage: str, message: str) -> None:
    pass


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------


@dataclass
class ReelSettings:
    mode: str = "artifact-comes-alive"  # or "museum-story" / "journal-to-reel"
    protagonist: str = "curator"  # "curator" or "my-cat"
    protagonist_name: str = "Cat the Curator"
    language: str = "th"  # narration language
    tone: str = "funny"
    shots: int = 6
    seconds_per_shot: int = 5
    max_characters: int = 3
    max_locations: int = 2
    ending: str = "funny twist"

    def brief(self) -> str:
        who = (
            "the brand character"
            if self.protagonist == "curator"
            else "the user's own cat, from an uploaded photo"
        )
        return (
            f"Mode: {self.mode}\n"
            f"Protagonist: {self.protagonist_name} ({who})\n"
            f"Narration language: {'Thai' if self.language == 'th' else 'English'}\n"
            f"Tone: {self.tone}\n"
            f"Shots: {self.shots} at ~{self.seconds_per_shot}s each "
            f"({self.shots * self.seconds_per_shot}s total)\n"
            f"At most {self.max_characters} characters and "
            f"{self.max_locations} locations\n"
            f"Ending: {self.ending}"
        )


BRAND = (
    "The Meowseum is a small Thai brand that makes cat furniture and cat gear "
    "shaped like famous art and architecture, presented as a museum. Cat the "
    "Curator is its resident character: a cat who runs the museum and takes the "
    "job extremely seriously. The house voice is dry, warm and understated — it "
    "never oversells."
)

SAFETY = (
    "Hard rule: never state or imply a price, a currency amount, stock or "
    "availability, shipping terms, delivery time, weight, or physical "
    "dimensions. That information is deliberately withheld from you because it "
    "is not yet confirmed for marketing. Write about the story, the look, the "
    "idea and the cat instead. If you feel the need for a number, leave it out."
)


def _system(role: str) -> str:
    return f"{role}\n\n{BRAND}\n\n{SAFETY}"


def _context_block(record: SourceRecord) -> str:
    return json.dumps(record.story_context(), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# stage 1 — curate
# ---------------------------------------------------------------------------


def curate(record: SourceRecord, meter: llm.CostMeter) -> dict:
    """Rank the extracted material by what a 30-second Reel can actually use.

    Without this the later stages try to honour every field equally and the
    Reel turns into a spec sheet.
    """
    data, result = llm.generate_json(
        _system(
            "You are a source curator. You decide which parts of a page are "
            "worth putting on screen and which are dead weight."
        ),
        f"""Here is an extracted page from The Meowseum:

{_context_block(record)}

Pick the material worth using in a short vertical video. Return JSON:

{{
  "headline_fact": "the single most interesting true thing on this page",
  "visual_hooks": ["concrete things a viewer could SEE, max 4"],
  "story_seeds": ["situations or conflicts this piece suggests, max 4"],
  "cat_benefit": "what this actually does for a cat, in one plain sentence",
  "historical_hook": "the real art/architecture reference, or null",
  "avoid": ["material that would be boring or spec-sheet-ish on screen"]
}}""",
        max_tokens=1200,
    )
    meter.add_text(result)
    return data


# ---------------------------------------------------------------------------
# stage 2+3 — characters and locations
# ---------------------------------------------------------------------------


def cast_and_set(
    record: SourceRecord, curated: dict, settings: ReelSettings, meter: llm.CostMeter
) -> dict:
    """Characters and locations in one call — they constrain each other."""
    data, result = llm.generate_json(
        _system(
            "You are a casting and location director for very short vertical "
            "video. You are ruthless about count: every extra character or "
            "location costs screen time the story does not have."
        ),
        f"""Source material:

{_context_block(record)}

Curator's picks:
{json.dumps(curated, ensure_ascii=False, indent=2)}

Brief:
{settings.brief()}

The protagonist is fixed: {settings.protagonist_name}. Rank supporting
characters and locations, keeping only what earns its place. Return JSON:

{{
  "characters": [
    {{"name": "...", "role": "...", "look": "one visual line",
      "why": "what this character is FOR in the story"}}
  ],
  "locations": [
    {{"name": "...", "look": "one visual line",
      "why": "what happens here that could not happen elsewhere"}}
  ],
  "cut": ["candidates you rejected, and why, one line each"]
}}

Include the protagonist as the first character. At most
{settings.max_characters} characters and {settings.max_locations} locations
in total.""",
        max_tokens=1500,
    )
    meter.add_text(result)
    return data


# ---------------------------------------------------------------------------
# stage 4 — concepts
# ---------------------------------------------------------------------------


def concepts(
    record: SourceRecord,
    curated: dict,
    cast: dict,
    settings: ReelSettings,
    meter: llm.CostMeter,
) -> list[dict]:
    """Exactly three concepts, deliberately different from each other."""
    data, result = llm.generate_json(
        _system(
            "You are a short-form video concept writer. Three concepts, and "
            "they must differ in kind, not in wording."
        ),
        f"""Source material:

{_context_block(record)}

Curator's picks:
{json.dumps(curated, ensure_ascii=False, indent=2)}

Cast and locations:
{json.dumps(cast, ensure_ascii=False, indent=2)}

Brief:
{settings.brief()}

Write exactly three concepts:
1. "source-faithful" — closest to what the page actually says
2. "funny" — most shareable, willing to be silly
3. "cinematic" — most imaginative, atmospheric

Return JSON:

[
  {{
    "id": "source-faithful",
    "logline": "one sentence, the whole story",
    "hook": "what happens in the first 3 seconds",
    "turn": "the moment the story changes",
    "ending": "how it pays off",
    "from_source": ["facts taken from the page"],
    "invented": ["things you made up"]
  }}
]""",
        max_tokens=2000,
    )
    meter.add_text(result)
    return data if isinstance(data, list) else data.get("concepts", [])


# ---------------------------------------------------------------------------
# stage 5 — outline and its critic
# ---------------------------------------------------------------------------

OUTLINE_RUBRIC = [
    "hook lands within the first 3 seconds",
    "story is clear without narration",
    "the piece is visible but the film is not an advert",
    "nothing contradicts the source page",
    "the cat is the subject of every beat",
    "each beat is renderable as ONE still image",
    "character and location counts respect the brief",
    "narration fits the beat's duration when read aloud",
    "vertical 9:16 composition is possible",
    "the ending pays off the hook",
]


def outline(
    record: SourceRecord,
    concept: dict,
    cast: dict,
    settings: ReelSettings,
    meter: llm.CostMeter,
) -> dict:
    data, result = llm.generate_json(
        _system("You are a short-form video story editor."),
        f"""Source material:

{_context_block(record)}

Chosen concept:
{json.dumps(concept, ensure_ascii=False, indent=2)}

Cast and locations:
{json.dumps(cast, ensure_ascii=False, indent=2)}

Brief:
{settings.brief()}

Break the concept into exactly {settings.shots} beats. Each beat must be a
single still image — no beat may require motion to be understood.

Return JSON:

{{
  "title": "...",
  "beats": [
    {{"beat": 1, "what_happens": "...", "why_it_matters": "...",
      "characters": ["..."], "location": "..."}}
  ]
}}""",
        max_tokens=2500,
    )
    meter.add_text(result)
    return data


def critique_outline(
    draft: dict, record: SourceRecord, settings: ReelSettings, meter: llm.CostMeter
) -> dict:
    """One critic pass. Returns the revision plus the scorecard that produced it.

    The scorecard is kept, not discarded, because criterion C5 asks whether the
    critic is worth its cost — which cannot be answered without the before, the
    after, and the reasoning between them.
    """
    data, result = llm.generate_json(
        _system(
            "You are a hostile story critic. You do not praise. You find the "
            "weakest beat and you fix it."
        ),
        f"""Source material:

{_context_block(record)}

Draft outline:
{json.dumps(draft, ensure_ascii=False, indent=2)}

Brief:
{settings.brief()}

Score the draft against each criterion, then return an improved outline with
the same number of beats. Criteria:
{json.dumps(OUTLINE_RUBRIC, ensure_ascii=False, indent=2)}

Return JSON:

{{
  "scores": [{{"criterion": "...", "pass": true, "note": "..."}}],
  "worst_problem": "the single biggest flaw",
  "changes": ["what you changed and why, one line each"],
  "revised": {{ "title": "...", "beats": [ ... same shape as the draft ... ] }}
}}""",
        max_tokens=3500,
    )
    meter.add_text(result)
    return data


# ---------------------------------------------------------------------------
# stage 6 — shots and their critic
# ---------------------------------------------------------------------------


def _protagonist_rule(settings: ReelSettings) -> str:
    if settings.protagonist == "my-cat":
        return (
            "The protagonist is the cat in the supplied reference photo. In "
            "every image prompt, describe that cat by the same fixed physical "
            "details every time (coat pattern, colour, face markings, eye "
            "colour) so the same animal is recognisable from shot to shot. "
            "Never change its markings for narrative convenience."
        )
    return (
        "The protagonist is Cat the Curator: describe the same cat in every "
        "prompt, with identical markings and the same small curatorial detail "
        "(a ribbon badge), so the animal is recognisable from shot to shot."
    )


def shots(
    record: SourceRecord,
    final_outline: dict,
    settings: ReelSettings,
    meter: llm.CostMeter,
) -> list[dict]:
    language = "Thai" if settings.language == "th" else "English"
    data, result = llm.generate_json(
        _system("You are a shot designer and narration writer."),
        f"""Source material:

{_context_block(record)}

Approved outline:
{json.dumps(final_outline, ensure_ascii=False, indent=2)}

Brief:
{settings.brief()}

{_protagonist_rule(settings)}

Write one shot per beat. Narration is in {language} and must be speakable in
about {settings.seconds_per_shot} seconds — roughly
{settings.seconds_per_shot * 3} words.

`source_basis` must list field names from this page's "allowed_basis" list:
{json.dumps(record.story_context()["allowed_basis"], ensure_ascii=False)}

If a shot invents something, say so in `creative_addition` and leave
`source_basis` as the fields it still leans on. Never cite a field name that is
not in the list above.

Return JSON:

[
  {{
    "shot_number": 1,
    "duration_seconds": {settings.seconds_per_shot},
    "source_basis": ["fields.museum_label"],
    "creative_addition": "what you invented here, or null",
    "image_prompt": "a full, self-contained image description, vertical 9:16",
    "narration": "the {language} line",
    "caption": "short on-screen text",
    "camera_motion": "slow push-in",
    "transition": "cut"
  }}
]""",
        max_tokens=4000,
    )
    meter.add_text(result)
    return data if isinstance(data, list) else data.get("shots", [])


def critique_shots(
    draft: list[dict],
    record: SourceRecord,
    settings: ReelSettings,
    meter: llm.CostMeter,
) -> dict:
    audit = audit_shots(draft, record)
    data, result = llm.generate_json(
        _system(
            "You are a shot critic. You care about visual consistency and "
            "about narration that can actually be read aloud in time."
        ),
        f"""Draft shots:
{json.dumps(draft, ensure_ascii=False, indent=2)}

Automated audit of these shots:
{json.dumps(audit, ensure_ascii=False, indent=2)}

Allowed source_basis field names:
{json.dumps(record.story_context()["allowed_basis"], ensure_ascii=False)}

{_protagonist_rule(settings)}

Fix, in this order:
1. any problem the automated audit found
2. any image prompt that describes the protagonist differently from the others
3. any narration too long to read in its duration
4. any prompt that is not self-contained (it must not rely on the previous shot)

Return JSON:

{{
  "changes": ["what you changed and why"],
  "revised": [ ... the full corrected shot list, same shape ... ]
}}""",
        max_tokens=5000,
    )
    meter.add_text(result)
    return data


# ---------------------------------------------------------------------------
# grounding + safety audit
# ---------------------------------------------------------------------------

#: Anything that looks like a commercial claim in narration or caption.
_FORBIDDEN = [
    (re.compile(r"[฿$]\s*\d"), "currency amount"),
    (re.compile(r"\b\d+\s*(?:บาท|baht|thb)\b", re.I), "price"),
    (re.compile(r"\b\d+(?:\.\d+)?\s*(?:cm|มม|ซม|kg|g|กรัม|กก)\b", re.I), "dimension or weight"),
    (re.compile(r"\b(?:in stock|พร้อมส่ง|free shipping|ส่งฟรี|จัดส่ง)\b", re.I), "stock or shipping claim"),
]


def audit_shots(shot_list: list[dict], record: SourceRecord) -> dict:
    """Check grounding (C2) and commercial safety (C3) without a model.

    A deterministic audit is the point: it is the thing that would still catch
    the problem if every agent in the chain were persuaded to misbehave.
    """
    allowed = set(record.story_context()["allowed_basis"])
    problems: list[dict] = []
    ungrounded = 0

    for shot in shot_list:
        number = shot.get("shot_number", "?")
        basis = shot.get("source_basis") or []
        if isinstance(basis, str):
            basis = [basis]
        invented = shot.get("creative_addition")

        if not basis and not invented:
            ungrounded += 1
            problems.append(
                {
                    "shot": number,
                    "kind": "ungrounded",
                    "detail": "declares neither source_basis nor creative_addition",
                }
            )
        for name in basis:
            if name not in allowed:
                problems.append(
                    {
                        "shot": number,
                        "kind": "unknown_basis",
                        "detail": f"cites {name!r}, which is not a field of this page",
                    }
                )

        text = " ".join(
            str(shot.get(key, "")) for key in ("narration", "caption", "image_prompt")
        )
        for pattern, label in _FORBIDDEN:
            match = pattern.search(text)
            if match:
                problems.append(
                    {
                        "shot": number,
                        "kind": "commercial_claim",
                        "detail": f"{label}: {match.group(0)!r}",
                    }
                )

    return {
        "shots": len(shot_list),
        "ungrounded_shots": ungrounded,
        "problems": problems,
        "clean": not problems,
    }


# ---------------------------------------------------------------------------
# stage 7 — images
# ---------------------------------------------------------------------------

STYLE = (
    "Editorial product-story photography for a small design museum. Warm "
    "gallery light, soft shadows, muted cream and walnut palette, shallow "
    "depth of field. Vertical 9:16 composition with headroom for a caption at "
    "the top. No text, no logos, no watermarks in the image."
)


def render_images(
    shot_list: list[dict],
    out_dir: Path,
    meter: llm.CostMeter,
    *,
    reference: Path | None = None,
    quality: str = "medium",
    progress: Progress = _noop,
) -> list[dict]:
    """Generate one image per shot. A failed shot does not abort the run."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for shot in shot_list:
        number = shot.get("shot_number", len(rendered) + 1)
        prompt = f"{shot.get('image_prompt', '')}\n\n{STYLE}"
        progress("image", f"shot {number}/{len(shot_list)} rendering")
        entry = dict(shot)
        try:
            data = llm.generate_image(prompt, reference=reference, quality=quality)
            path = out_dir / f"shot-{int(number):02d}.png"
            path.write_bytes(data)
            meter.add_image(quality)
            entry["image_file"] = path.name
            entry["image_error"] = None
        except llm.LLMError as error:
            entry["image_file"] = None
            entry["image_error"] = str(error)[:300]
            progress("image", f"shot {number} FAILED: {entry['image_error']}")
        rendered.append(entry)
    return rendered


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------


@dataclass
class ReelRun:
    record: SourceRecord
    settings: ReelSettings
    curated: dict = field(default_factory=dict)
    cast: dict = field(default_factory=dict)
    concepts: list = field(default_factory=list)
    chosen_concept: dict = field(default_factory=dict)
    outline_draft: dict = field(default_factory=dict)
    outline_critique: dict = field(default_factory=dict)
    outline_final: dict = field(default_factory=dict)
    shots_draft: list = field(default_factory=list)
    shots_critique: dict = field(default_factory=dict)
    shots_final: list = field(default_factory=list)
    audit_before: dict = field(default_factory=dict)
    audit_after: dict = field(default_factory=dict)
    cost: dict = field(default_factory=dict)

    def manifest(self) -> dict:
        return {
            "source": self.record.story_context(),
            "settings": vars(self.settings),
            "curated": self.curated,
            "cast": self.cast,
            "concepts": self.concepts,
            "chosen_concept": self.chosen_concept,
            "outline_draft": self.outline_draft,
            "outline_critique": self.outline_critique,
            "outline_final": self.outline_final,
            "shots_draft": self.shots_draft,
            "shots_critique": self.shots_critique,
            "shots": self.shots_final,
            "audit_before_critic": self.audit_before,
            "audit_after_critic": self.audit_after,
            "cost": self.cost,
        }


def plan_reel(
    record: SourceRecord,
    settings: ReelSettings,
    *,
    concept_id: str | None = None,
    progress: Progress = _noop,
) -> tuple[ReelRun, llm.CostMeter]:
    """Everything up to (not including) image generation.

    Returns the run and the meter, so the caller can keep accumulating cost
    through image rendering and report one total.
    """
    meter = llm.CostMeter()
    run = ReelRun(record=record, settings=settings)

    progress("curate", "ranking source material")
    run.curated = curate(record, meter)

    progress("cast", "choosing characters and locations")
    run.cast = cast_and_set(record, run.curated, settings, meter)

    progress("concept", "writing three concepts")
    run.concepts = concepts(record, run.curated, run.cast, settings, meter)
    run.chosen_concept = _pick(run.concepts, concept_id)

    progress("outline", f"outlining {settings.shots} beats")
    run.outline_draft = outline(
        record, run.chosen_concept, run.cast, settings, meter
    )

    progress("outline-critic", "critiquing the outline")
    run.outline_critique = critique_outline(run.outline_draft, record, settings, meter)
    run.outline_final = run.outline_critique.get("revised") or run.outline_draft

    progress("shots", "writing shots and narration")
    run.shots_draft = shots(record, run.outline_final, settings, meter)
    run.audit_before = audit_shots(run.shots_draft, record)

    progress("shot-critic", "critiquing the shots")
    run.shots_critique = critique_shots(run.shots_draft, record, settings, meter)
    run.shots_final = run.shots_critique.get("revised") or run.shots_draft
    run.audit_after = audit_shots(run.shots_final, record)

    run.cost = meter.summary()
    progress("plan", f"planned — {run.cost['text_calls']} model calls")
    return run, meter


def _pick(concept_list: list[dict], concept_id: str | None) -> dict:
    if not concept_list:
        raise llm.LLMError("no concepts were generated")
    if concept_id:
        for concept in concept_list:
            if concept.get("id") == concept_id:
                return concept
    return concept_list[0]
