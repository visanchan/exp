# Prompt — Character Sheet for Cross-Image Consistency

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)
**Task:** keeping one character recognisably the same across N independently
generated images (storyboard, comic, explainer, ad sequence)

## The prompt that fails

```text
The protagonist is <NAME>: describe the same character in every prompt, with
identical markings and the same small distinguishing detail, so they are
recognisable from shot to shot.
```

Read it closely: it instructs the model *to be specific* without ever supplying
the specifics. A weaker model satisfied it literally and uselessly — it repeated
the phrase **"distinct markings"** in each image prompt. The phrase recurred; the
markings did not. Shot 1 rendered a brown-and-white long-haired cat with a gold
badge; shot 4 rendered a cream-orange cat with no badge. A second run reproduced
the failure with a different symptom: shot 1 a four-legged tabby, shot 5 an
anthropomorphic tabby standing upright in a tweed jacket.

Graded 2/5 for cross-shot identity, twice.

## What actually fixes it

Generate the description **once**, then substitute it as a literal string into
every prompt:

```text
CHARACTER SHEET (use this exact wording in every image prompt, verbatim):
"a white short-haired cat with a black patch above the left ear, a black-tipped
tail, amber eyes, and a dark red ribbon badge"

Every image prompt must contain the character sheet text word for word before
describing the action. Do not paraphrase it, shorten it, or replace it with a
summary.
```

Then check it in code, because a critic's claim to have done this was false in
practice:

```python
missing = [s["shot_number"] for s in shots
           if CHARACTER_SHEET not in s.get("image_prompt", "")]
```

## The finding worth remembering

A stronger model, given the *unchanged failing prompt above*, produced a
character sheet on its own — all six image prompts opened with an identical
clause naming coat, ear patch, tail, eye colour and badge. Cross-shot identity
went from 2/5 to 4/5 with no prompt change at all.

So: **"be consistent" is not a specification, but a capable enough model will
supply the missing specification itself.** Two practical consequences —

- When output is inconsistent, check whether the prompt actually specifies the
  thing, or merely asks for specificity. This class of prompt bug is easy to
  read straight past, because it *sounds* precise.
- A model upgrade can close a gap that needs knowledge. It will not close a gap
  that needs measurement. In the same comparison, narration lines that had to
  fit a five-second budget overran on *both* models — no model grades its own
  output against a stopwatch.

## If you have an image of the character, use the image

The same experiment ran the same shots with the character supplied as a
**reference image** to the image-edit endpoint instead of as text. On identical
settings it scored **4/5** for cross-shot identity against the text path's
**2/5** — better than the character sheet achieved, and achieved without any
prompt engineering at all.

The mechanism: a reference image is a fixed artefact, while a text description is
re-interpreted on every call, and whatever the text leaves unsaid is re-invented
each time. A character sheet narrows the gap by leaving less unsaid; it does not
close it.

So the order of preference is: **reference image first; character sheet only
when no image exists** (a character being invented for the first time, or a
model or endpoint that takes no image input). Generate one canonical image early,
then use it as the reference for the rest.

## Does not transfer to

Object and product identity, at least not for free. The same runs kept the
character stable while the *product* drifted — rendering a famous artwork
instead of the physical object parodying it — because the character description
was repeated in every prompt and the product noun phrase was not. Give every
entity that must stay stable its own literal phrase, and check for each one.
