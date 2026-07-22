# Pattern — Discover an Optional Binary, Don't Require It

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)

## Problem

A feature needs an external tool — ffmpeg, pandoc, graphviz, a headless browser.
The usual options are both bad for a small or disposable project:

- **Require it.** Now the whole app fails to start on a machine without it, for
  a feature that machine may never use. A README line saying "install ffmpeg
  first" is a wall in front of everything else.
- **Assume it.** The app starts, the feature explodes at the worst moment with a
  `FileNotFoundError` and no explanation of what to install.

## Pattern

Probe for it, cache the answer, and report it as a **capability** the app has or
lacks. Everything else keeps working either way.

```python
def find_binary() -> Path | None:
    override = os.environ.get("FFMPEG_BINARY", "").strip().strip('"')
    if override:                                  # 1. explicit wins
        candidate = Path(override)
        return candidate if candidate.exists() else None
    if (on_path := shutil.which("ffmpeg")):       # 2. normal install
        return Path(on_path)
    for raw in _KNOWN_LOCATIONS:                  # 3. bundled with something else
        if (candidate := Path(raw)).exists():
            return candidate
    return None
```

Then check it can do the *specific* job, not merely that it exists:

```python
@dataclass
class Capability:
    available: bool
    binary: str | None = None
    encoder: str | None = None
    reason: str = ""          # why not, in words a user can act on
```

Probe the feature set and prefer the best available implementation, falling back
rather than failing:

```python
found = _encoders(binary)                       # parse `ffmpeg -encoders`
encoder = next((e for e in ("libx264", "libopenh264") if e in found), None)
if encoder is None:
    return Capability(False, binary=str(binary),
                      reason=f"{binary} has no H.264 encoder; its output would "
                             "not play on the platforms this export targets.")
```

Surface it in the app's health/status output and in the UI, so the button is
disabled *with the reason attached* rather than mysteriously broken.

## Why it works

The dependency becomes information rather than an obstacle. On the machine where
this was built, ffmpeg was not on `PATH` and was never installed deliberately —
it was found inside an unrelated desktop application's install directory. Nothing
had to be installed at all.

That build also lacked the preferred `libx264` encoder but had `libopenh264`,
which produces the same container and codec the target platforms check for. A
naive `which ffmpeg` check plus a hardcoded `-c:v libx264` would have reported
success and then failed at encode time.

The three-step order matters: an explicit environment variable lets a user point
at a specific build, `PATH` covers the normal case, and known locations catch
the "you already have it and don't know" case.

## Checklist

- [ ] Env-var override, then `PATH`, then known locations.
- [ ] Verify the capability you need, not just that the binary exists.
- [ ] Cache the probe — it costs a subprocess launch and cannot change mid-run.
- [ ] Carry a human-readable `reason` for every negative answer.
- [ ] Expose it in health output; disable the UI affordance rather than hiding it.
- [ ] Document the env var name in `.env.example`.
- [ ] Never install it silently on the user's machine.

## Related

- `knowledge/code-snippets/stills-plus-audio-to-mp4.md` — the ffmpeg invocation
  this pattern was built around.
