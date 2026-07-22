"""MP4 export — turn a finished run's stills and narration into one video file.

The Reel is a slideshow of stills plus one narration MP3 per shot, which is
enough to watch in the browser but not enough to post anywhere. Instagram,
TikTok and YouTube want a single H.264/AAC MP4; this module produces one.

Why ffmpeg and not Python: encoding H.264 is not something the standard library
can do, and no pure-Python encoder produces a file those platforms accept. This
is an external *binary* dependency, not an installed package — nothing is added
to the environment. The binary is discovered, never installed:

    1. the ``FFMPEG_BINARY`` environment variable, if set
    2. ``ffmpeg`` on PATH
    3. a short list of places a Windows machine tends to already have one
       (Krita and OBS both ship a full build)

If none is found, export is reported as unavailable and the rest of the app is
unaffected — the browser player never needed it.

Encoding shape, matching what the player shows:

*   1080x1920, scale-to-cover then centre-crop — the same framing as the
    player's ``object-fit: cover`` in a 9:16 box, so the export is not a
    different composition from the one that was reviewed. Since the move to
    `gpt-image-2` the stills are generated at 864x1536, already 9:16, so this
    is now a pure upscale and the crop takes nothing off. It is kept rather
    than simplified to a `scale`: it costs nothing, and it is what keeps the
    export correct for runs whose images were generated at 2:3 (every run
    before 2026-07-23) and for any future change of source aspect.
*   Each shot lasts ``max(planned duration, narration length + 0.4s)``, which is
    the player's rule. The length is measured from the MP3 and passed as an
    explicit ``-t``: ``-shortest`` does not reliably end a looped still when a
    ``filter_complex`` is in play, and the encode runs forever instead.
*   Segments are encoded with identical parameters and then concatenated with
    ``-c copy``, so the join is a stream copy rather than a second encode.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

Progress = Callable[[str, str], None]


def _noop(stage: str, message: str) -> None:
    pass


class ExportError(Exception):
    """Export could not be produced."""


WIDTH, HEIGHT, FPS = 1080, 1920, 30
AUDIO_RATE = 44100
#: Silence appended after every narration line, matching the player's hold.
TAIL_SECONDS = 0.4

#: Preferred first. libx264 is the good one; libopenh264 is the one that tends
#: to be present in bundled builds. Both produce H.264 in an MP4 container.
H264_ENCODERS = ("libx264", "libopenh264")

_WINDOWS_CANDIDATES = (
    r"C:\Program Files\Krita (x64)\bin\ffmpeg.exe",
    r"C:\Program Files\obs-studio\bin\64bit\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
)


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------


def find_ffmpeg() -> Path | None:
    override = os.environ.get("FFMPEG_BINARY", "").strip().strip('"')
    if override:
        candidate = Path(override)
        return candidate if candidate.exists() else None

    on_path = shutil.which("ffmpeg")
    if on_path:
        return Path(on_path)

    for raw in _WINDOWS_CANDIDATES:
        candidate = Path(raw)
        if candidate.exists():
            return candidate
    return None


def _encoders(binary: Path) -> set[str]:
    try:
        completed = subprocess.run(
            [str(binary), "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    return {
        line.split()[1]
        for line in completed.stdout.splitlines()
        if line.startswith(" V") and len(line.split()) > 1
    }


@dataclass
class Capability:
    available: bool
    binary: str | None = None
    video_encoder: str | None = None
    reason: str = ""

    def as_dict(self) -> dict:
        return {
            "available": self.available,
            "binary": self.binary,
            "video_encoder": self.video_encoder,
            "reason": self.reason,
        }


_CAPABILITY: Capability | None = None


def capability(refresh: bool = False) -> Capability:
    """What this machine can export, decided once and cached.

    Probing ffmpeg costs a subprocess launch; the answer does not change while
    the server runs.
    """
    global _CAPABILITY
    if _CAPABILITY is not None and not refresh:
        return _CAPABILITY

    binary = find_ffmpeg()
    if binary is None:
        _CAPABILITY = Capability(
            False,
            reason=(
                "ffmpeg was not found. Install it, or point FFMPEG_BINARY at an "
                "existing ffmpeg.exe."
            ),
        )
        return _CAPABILITY

    found = _encoders(binary)
    encoder = next((name for name in H264_ENCODERS if name in found), None)
    if encoder is None:
        _CAPABILITY = Capability(
            False,
            binary=str(binary),
            reason=(
                f"{binary} has no H.264 encoder "
                f"({' or '.join(H264_ENCODERS)}); its MP4s would not play on "
                "the platforms this export is for."
            ),
        )
        return _CAPABILITY

    _CAPABILITY = Capability(True, binary=str(binary), video_encoder=encoder)
    return _CAPABILITY


# ---------------------------------------------------------------------------
# encoding
# ---------------------------------------------------------------------------


def _run(command: list[str], what: str) -> None:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        # Encoding a handful of stills takes seconds. Minutes means something
        # is looping, and a short timeout surfaces that instead of hanging the
        # request until the browser gives up.
        raise ExportError(f"{what} timed out after 3 minutes") from None
    except OSError as error:
        raise ExportError(f"{what} could not start: {error}") from None
    if completed.returncode != 0:
        tail = (completed.stderr or "").strip().splitlines()[-6:]
        raise ExportError(f"{what} failed: " + " | ".join(tail))


_DURATION = re.compile(r"Duration:\s*(\d+):(\d\d):(\d\d(?:\.\d+)?)")


def _media_seconds(binary: str, path: Path) -> float | None:
    """Length of a media file, read from ffmpeg's own header dump.

    Deliberately not ffprobe: ffprobe ships beside ffmpeg on most builds but
    not all, and this needs no second binary to be present.
    """
    try:
        completed = subprocess.run(
            [binary, "-hide_banner", "-i", str(path)],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # `ffmpeg -i` with no output exits non-zero by design; the header is on
    # stderr either way.
    match = _DURATION.search(completed.stderr or "")
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _video_options(encoder: str) -> list[str]:
    if encoder == "libx264":
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "20"]
    # libopenh264 has no CRF mode; a fixed bitrate is the only control it takes.
    return ["-c:v", "libopenh264", "-b:v", "5M"]


_FRAME = (
    f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
    f"crop={WIDTH}:{HEIGHT},setsar=1,fps={FPS},format=yuv420p"
)


def _segment(
    binary: str,
    encoder: str,
    image: Path,
    audio: Path | None,
    planned_seconds: float,
    target: Path,
) -> float:
    """One shot: a still held under its narration line. Returns its length."""
    spoken = _media_seconds(binary, audio) if audio is not None else None
    # The player's rule: hold for the planned time, or for the whole spoken
    # line plus a short tail when the line runs over.
    seconds = round(max(planned_seconds, (spoken or 0) + TAIL_SECONDS), 3)

    command = [binary, "-y", "-loop", "1", "-i", str(image)]

    if audio is not None:
        command += ["-i", str(audio)]
        # Pad the line out to the full segment length so the audio track does
        # not end early and leave the muxer interleaving a silent gap.
        audio_filter = f"aresample={AUDIO_RATE},apad=whole_dur={seconds}"
    else:
        command += [
            "-f", "lavfi",
            "-t", str(seconds),
            "-i", f"anullsrc=r={AUDIO_RATE}:cl=stereo",
        ]
        audio_filter = "anull"

    command += [
        "-filter_complex",
        f"[0:v]{_FRAME}[v];[1:a]{audio_filter}[a]",
        "-map", "[v]",
        "-map", "[a]",
        # An explicit duration, not -shortest: with a filter_complex in the
        # graph, -shortest does not stop the looping still and the encode never
        # terminates.
        "-t", str(seconds),
        *_video_options(encoder),
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", str(AUDIO_RATE),
        "-ac", "2",
        "-movflags", "+faststart",
        str(target),
    ]
    _run(command, f"encoding {target.name}")
    return seconds


def export_mp4(
    manifest: dict,
    run_dir: Path,
    *,
    progress: Progress = _noop,
) -> dict:
    """Encode a finished run into ``reel.mp4`` inside its own run folder.

    Returns a small report — path, size, how many shots made it in, and which
    were dropped and why — because a silently shortened Reel would be worse
    than a failed export.
    """
    caps = capability()
    if not caps.available:
        raise ExportError(caps.reason)

    shots = manifest.get("shots") or []
    if not shots:
        raise ExportError("this run has no shots")

    work = run_dir / "export"
    work.mkdir(parents=True, exist_ok=True)
    started = time.time()

    segments: list[Path] = []
    skipped: list[dict] = []
    silent = 0
    total_seconds = 0.0

    for index, shot in enumerate(shots, start=1):
        number = shot.get("shot_number", index)
        image_name = shot.get("image_file")
        if not image_name or not (run_dir / image_name).exists():
            # A shot with no still has nothing to show. Including it as black
            # would pad the Reel with a defect; leaving it out is visible in
            # the report.
            skipped.append({"shot": number, "why": "no image file"})
            continue

        audio_name = shot.get("audio_file")
        audio = run_dir / audio_name if audio_name else None
        if audio is not None and not audio.exists():
            audio = None
        if audio is None:
            silent += 1

        planned = float(shot.get("duration_seconds") or 5)
        target = work / f"seg-{int(number):02d}.mp4"
        progress("export", f"shot {number}/{len(shots)} encoding")
        total_seconds += _segment(
            caps.binary, caps.video_encoder, run_dir / image_name, audio,
            planned, target,
        )
        segments.append(target)

    if not segments:
        raise ExportError("no shot in this run had an image to encode")

    # The concat demuxer resolves each entry relative to the list file's own
    # directory, so these are bare names, not the paths used to write them.
    listing = work / "segments.txt"
    listing.write_text(
        "\n".join(f"file '{segment.name}'" for segment in segments) + "\n",
        encoding="utf-8",
    )

    output = run_dir / "reel.mp4"
    progress("export", f"joining {len(segments)} segments")
    _run(
        [
            caps.binary, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(listing),
            "-c", "copy",
            "-movflags", "+faststart",
            str(output),
        ],
        "joining segments",
    )

    for segment in segments:
        segment.unlink(missing_ok=True)
    listing.unlink(missing_ok=True)
    try:
        work.rmdir()
    except OSError:
        pass

    report = {
        "file": output.name,
        "bytes": output.stat().st_size,
        "shots_encoded": len(segments),
        "shots_skipped": skipped,
        "silent_shots": silent,
        "duration_seconds": round(total_seconds, 1),
        "video_encoder": caps.video_encoder,
        "resolution": f"{WIDTH}x{HEIGHT}",
        "seconds_to_encode": round(time.time() - started, 1),
    }
    (run_dir / "export.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    progress("export", f"reel.mp4 ready — {report['bytes'] // 1024} KB")
    return report
