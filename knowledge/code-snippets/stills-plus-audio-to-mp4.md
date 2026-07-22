# Snippet — Still Images + Per-Shot Audio → One MP4

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)

Turns N generated stills and N narration clips into a single H.264/AAC MP4 that
Instagram, TikTok and YouTube accept. Standard library plus an `ffmpeg` binary;
no Python packages.

Worth keeping because two of the three steps have non-obvious failure modes that
cost real debugging time.

## Step 1 — measure each audio clip

Needed to decide how long each still is held. Uses `ffmpeg` itself, so no
separate `ffprobe` dependency (it ships beside ffmpeg on most builds, but not
all).

```python
_DURATION = re.compile(r"Duration:\s*(\d+):(\d\d):(\d\d(?:\.\d+)?)")

def media_seconds(ffmpeg: str, path: Path) -> float | None:
    completed = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace",
    )
    # `ffmpeg -i` with no output file exits non-zero by design;
    # the header lands on stderr either way.
    if not (m := _DURATION.search(completed.stderr or "")):
        return None
    hours, minutes, seconds = m.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
```

## Step 2 — one segment per shot

```python
seconds = round(max(planned_seconds, spoken_seconds + 0.4), 3)

command = [
    ffmpeg, "-y",
    "-loop", "1", "-i", str(image),
    "-i", str(audio),
    "-filter_complex",
    f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
    f"crop={W}:{H},setsar=1,fps=30,format=yuv420p[v];"
    f"[1:a]aresample=44100,apad=whole_dur={seconds}[a]",
    "-map", "[v]", "-map", "[a]",
    "-t", str(seconds),                 # ← see trap 1
    "-c:v", encoder, "-b:v", "5M",      # libx264: use -preset/-crf instead
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
    "-movflags", "+faststart",
    str(segment),
]
```

**Trap 1 — `-shortest` does not terminate a looped still when a
`filter_complex` is present.** The intuitive form is `-loop 1` plus `-shortest`
so the video ends with the audio. With a filter graph in play it does not: the
still loops forever and the encode never finishes. It does not error — it hangs
until something kills it. Measure the audio and pass an explicit `-t`.

`apad=whole_dur=N` pads the audio out to the full segment length so the audio
track does not end early and leave the muxer interleaving a gap.

For a shot with no narration, substitute a silent source:

```python
"-f", "lavfi", "-t", str(seconds), "-i", "anullsrc=r=44100:cl=stereo",
```

## Step 3 — concatenate without re-encoding

Because every segment was encoded with identical parameters, the join is a
stream copy.

```python
listing = work / "segments.txt"
listing.write_text(
    "\n".join(f"file '{segment.name}'" for segment in segments) + "\n",
    encoding="utf-8",
)
subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0",
                "-i", str(listing), "-c", "copy",
                "-movflags", "+faststart", str(output)], check=True)
```

**Trap 2 — the concat demuxer resolves each entry relative to the list file's
own directory**, not the process working directory. Writing the paths you used
to create the files produces a doubled path and
`Impossible to open '.../export/.../export/seg-01.mp4'`. Use bare filenames and
keep the list beside the segments.

## Framing note

`scale=...:force_original_aspect_ratio=increase` + `crop` reproduces CSS
`object-fit: cover`, so an exported video matches what a browser preview showed.
If the source images are already the target aspect it is a harmless no-op —
worth keeping anyway so older assets at a different aspect still export
correctly.

## Verifying the result

Do not trust a zero exit code. Cheap checks that catch real breakage:

```bash
ffprobe -v error -show_entries stream=codec_name,width,height -of json out.mp4
ffmpeg -hide_banner -i out.mp4 -af volumedetect -f null -   # mean/max dB
```

A silent track shows up as `mean_volume: -91 dB`; normal speech lands near
−20 dB. Extracting a frame (`-ss 3 -frames:v 1`) and looking at it catches the
case where the video is technically valid and visually empty.

## Timeouts

Encoding a handful of stills takes seconds. Set a short per-command timeout
(3 minutes was ample) so a hang surfaces immediately instead of after ten.
