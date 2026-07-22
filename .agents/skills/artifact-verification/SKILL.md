---
name: artifact-verification
description: Verify a produced artifact by opening, rendering, playing or using it — not by reading the code that made it. Use before reporting that an image, audio file, video, HTML page, document, spreadsheet, chart or exported data file is done or working; when a build "succeeded" but nobody has looked at the output; or when about to say something works on the strength of having written it. Covers the valid-but-empty failure class, per-format checks, and what counts as evidence.
---

# Artifact Verification

Code that runs without error is not the same as output that is correct. A
pipeline can complete cleanly and produce a silent audio file, a black video, a
blank page, or a CSV containing only headers — every step "succeeded", and the
thing the person actually receives is broken.

The rule: **an output nobody has perceived is an output nobody has checked.**
If a human will see, hear, read or click it, then seeing, hearing, reading or
clicking it is part of finishing the work.

Treat `AGENTS.md` at the repository root as authoritative if it and this skill
ever disagree.

**Related but different:**

| Skill | Looks at |
|---|---|
| `scrutinize` | Should this change exist, and does the traced code path do what it claims? |
| `reviewing-ai-written-code` | The defects generated *code* specifically contains |
| **this skill** | The *output itself*, as the person will encounter it |

All three can apply to one change. This one is last and cannot be skipped
because the other two passed — they read code; this opens the result.

## The failure class to look for

Structural validity and correct content are independent. These all pass an
"it exists and parses" check:

| Artifact | Passes existence check | Actually |
|---|---|---|
| Audio | valid MP3, right duration | silence |
| Video | valid MP4, plays | black frames |
| Image | valid PNG, right dimensions | wrong subject, or garbled text |
| HTML | loads, no console error | button does nothing |
| PDF / doc | opens, right page count | blank pages, or overlapping text |
| CSV / JSON | parses, right schema | zero rows, or every value null |
| Chart | renders | unlabelled axes, or plotting the wrong column |

So the check is never "did it produce a file". It is always **"is there
something in it, and is it the right something"**.

## Verify in two layers

Do both. Each catches what the other misses.

**1. A deterministic measurement** — repeatable, cheap, and it catches
regressions later. It produces a number you can put in a report.

**2. A human look** — you, opening the thing. This catches "technically valid,
visually wrong", which no measurement anticipates.

A measurement alone will confidently pass a black video. A glance alone will not
notice that the file got 4% shorter after a refactor.

## By format

### Images

```bash
# dimensions straight from the PNG header, no dependency
python -c "b=open('shot.png','rb').read(); print(int.from_bytes(b[16:20],'big'),'x',int.from_bytes(b[20:24],'big'))"
```

Then **open it and look.** Specifically: is it the right subject, is any text in
the image garbled, and — across a set — is the recurring subject actually the
same between images? Consistency across a series is invisible in any single
file and invisible to every automated check.

### Audio

```bash
ffmpeg -hide_banner -i narration.mp3 -af volumedetect -f null -    # mean/max dB
```

`mean_volume: -91 dB` is silence. Normal speech lands near −20 dB. Also check
duration against what was intended — audio that runs 40% over its budget is a
defect that only exists in the output, never in the source.

### Video

```bash
ffprobe -v error -show_entries stream=codec_name,width,height \
        -show_entries format=duration -of json out.mp4
ffmpeg -hide_banner -y -ss 3 -i out.mp4 -frames:v 1 frame.png     # then look at it
```

Extract frames from **more than one timestamp**. A video can be correct at the
start and wrong later, which is exactly what a single thumbnail hides.

### HTML pages

Open it in a browser. Then, if it has behaviour worth trusting, **write a
self-test**: a copy of the page with a script that fills the inputs, calls the
real functions, and asserts on the output. It runs on load, needs no clicking,
and is re-runnable after every change.

Check specifically: does the primary control actually do its job (copy, submit,
download), does it work offline if it claims to, and does it degrade sensibly
when a browser API is unavailable.

### Documents, spreadsheets, slides

Open and page through. Check the last page as well as the first — truncation
lands at the end. Confirm the numbers in the document match the source data,
not merely that a table exists.

### Data files

Row count, column types, and **spot-check actual values**. A file with the right
schema and no rows passes every structural test and is useless.

### Anything with an interaction

Do the round trip yourself. Copy the thing that says it copies. Submit the form.
Download the export and open the download. The end-to-end path is where the
breakage lives.

## What counts as evidence

Report what you measured and what you observed. These are not the same claim:

- ❌ "Generated 6 images and the narration."
- ❌ "The export should work now."
- ❌ "Tests pass." *(the tests are not the artifact)*
- ✅ "6 PNGs at 864×1536, ratio 0.5625. Opened shots 1 and 5: same subject in
  both. Audio mean −22.3 dB, peak −6.1 dB — speech, not silence."

If you could not verify something, **say which part and why** rather than
rounding up to "done". "The MP4 encodes and the frames look right; I have not
played the audio track" is a useful, honest report. "Working" is not.

## When to skip it

Proportion the effort. Full verification for anything a person will receive,
anything shipped or shared, and anything a later step depends on. Skip it for
intermediate files consumed by the next stage and immediately discarded, and for
throwaway scratch output — but only when nothing downstream reads them.

## Do not

- Do not report an artifact as working on the strength of the code that made it.
- Do not treat "the pipeline completed" as verification. That is the weakest
  possible signal, because it is exactly what the failure class survives.
- Do not check one item from a batch and assume the rest. Consistency defects
  live *between* items.
- Do not verify only the first page, first frame, or first row.
- Do not delete the verification artifact — a self-test page, a probe script,
  an extracted frame. It is how the next person re-checks after a change.
- Do not claim you looked at something you did not.
