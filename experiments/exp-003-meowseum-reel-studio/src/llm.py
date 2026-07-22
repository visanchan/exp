"""Model clients — text agents, image generation and narration.

Standard library only; every endpoint is plain JSON over HTTPS, and a handful of
them does not justify an SDK.

**One provider: OpenAI.** The earlier build also had an Anthropic branch that
took priority when `ANTHROPIC_API_KEY` was set. It was never executed — no key
was ever present — and it was removed under D7 rather than left as untested code
that looks like a working fallback. A run's actual model is still recorded in
``LAST_TEXT_MODEL`` and written into the manifest, because "which model wrote
this outline" is part of the result.

`gpt-5.6-sol` is not parameter-compatible with the `gpt-4o` family. Two
differences are load-bearing and were confirmed against the live API, not
assumed:

*   ``max_tokens`` is rejected — the field is ``max_completion_tokens``.
*   ``temperature`` accepts only its default of 1; 0.8, 0.2 and 0 all return
    400. Per-stage temperature control is therefore gone, and the JSON-retry
    path can no longer "turn the temperature down" to get a cleaner parse. It
    asks for a JSON object at the API level instead, which is stronger.

Every call returns usage counts so criterion C6 (cost) can be measured rather
than estimated.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
OPENAI_IMAGE_EDIT_URL = "https://api.openai.com/v1/images/edits"
OPENAI_SPEECH_URL = "https://api.openai.com/v1/audio/speech"
OPENAI_TEXT_MODEL = "gpt-5.6-sol"
OPENAI_IMAGE_MODEL = "gpt-image-2"

#: 864x1536 is a true 9:16 frame — the aspect the Reel is actually played and
#: exported at — and the largest such size with both sides divisible by 16,
#: which is `gpt-image-2`'s only stated size constraint. `gpt-image-1` could not
#: do this: it takes a fixed list (1024x1024, 1024x1536, 1536x1024) and rejects
#: 864x1536 outright, so every frame was generated at 2:3 and then centre-
#: cropped, discarding about 16% of each image's width. The two changes are
#: therefore coupled — reverting the model without reverting the size is a 400.
OPENAI_IMAGE_SIZE = "864x1536"

#: Reasoning depth for the text agents. `gpt-5.6-sol` accepts this where the
#: `gpt-4o` family did not; it is the replacement lever for the temperature
#: control the model no longer takes.
OPENAI_REASONING_EFFORT = "medium"
#: The newest speech model this endpoint accepts. `gpt-audio`, `gpt-audio-1.5`
#: and `gpt-audio-mini` are *not* alternatives — they reject `/v1/audio/speech`
#: with "Invalid URL"; they are chat-with-audio models on a different endpoint.
#: `tts-1` / `tts-1-hd` are the previous generation. Pinned to the dated
#: snapshot rather than the floating alias so a re-run months from now produces
#: the same narration as the runs recorded in the README.
OPENAI_TTS_MODEL = "gpt-4o-mini-tts-2025-12-15"

#: Voices the speech endpoint accepts. Kept here so the UI and the server
#: validate against one list instead of two that can drift apart.
TTS_VOICES = (
    "alloy",
    "ash",
    "ballad",
    "coral",
    "echo",
    "fable",
    "nova",
    "onyx",
    "sage",
    "shimmer",
)

TIMEOUT = 180


class LLMError(Exception):
    """A model call failed or returned something unusable."""


@dataclass
class TextResult:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    #: Reasoning tokens are billed as output but never appear in `text`. Kept
    #: separately so a run can show how much of the bill was invisible.
    reasoning_tokens: int = 0
    cached_input_tokens: int = 0


# ---------------------------------------------------------------------------
# env
# ---------------------------------------------------------------------------


def load_dotenv(start: Path | None = None) -> None:
    """Read KEY=VALUE from the nearest .env, without overwriting real env vars.

    Walks up from the experiment folder to the repository root. Values already
    present in the environment win, so an exported key is never clobbered.
    """
    here = (start or Path(__file__).resolve().parent).resolve()
    for directory in [here, *here.parents]:
        candidate = directory / ".env"
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and value and key not in os.environ:
                os.environ[key] = value
        return


def _key(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def available_providers() -> dict[str, bool]:
    """One key runs the whole pipeline — text, images and narration (D7)."""
    load_dotenv()
    return {"openai": bool(_key("OPENAI_API_KEY"))}


# ---------------------------------------------------------------------------
# http
# ---------------------------------------------------------------------------


def _post_json(url: str, payload: dict, headers: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    for name, value in headers.items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:600]
        raise LLMError(f"{url} returned {error.code}: {detail}") from None
    except urllib.error.URLError as error:
        raise LLMError(f"{url} unreachable: {error.reason}") from None


def _post_binary(url: str, payload: dict, headers: dict) -> bytes:
    """Same as ``_post_json`` but the response body is not JSON.

    The speech endpoint returns raw audio bytes on success and a JSON error
    object on failure, so the error path still decodes as text.
    """
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    for name, value in headers.items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:600]
        raise LLMError(f"{url} returned {error.code}: {detail}") from None
    except urllib.error.URLError as error:
        raise LLMError(f"{url} unreachable: {error.reason}") from None


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------

LAST_TEXT_MODEL = ""


def generate_text(
    system: str,
    prompt: str,
    *,
    max_tokens: int = 4000,
    effort: str = OPENAI_REASONING_EFFORT,
    json_object: bool = False,
) -> TextResult:
    """One text-agent turn.

    ``max_tokens`` keeps its name at this boundary — every caller in the
    pipeline already speaks it — but goes out as ``max_completion_tokens``,
    which is what the model accepts. It is a ceiling on reasoning **plus**
    visible output, so a low value can be spent entirely on reasoning and
    return empty text.
    """
    global LAST_TEXT_MODEL
    load_dotenv()

    key = _key("OPENAI_API_KEY")
    if not key:
        raise LLMError("OPENAI_API_KEY is not set — no text provider available")

    payload: dict[str, object] = {
        "model": OPENAI_TEXT_MODEL,
        # Not `max_tokens`: rejected with a 400 by this model.
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    if effort:
        payload["reasoning_effort"] = effort
    if json_object:
        payload["response_format"] = {"type": "json_object"}
    # No `temperature`: this model accepts only its default, and sending any
    # other value is a 400.

    data = _post_json(OPENAI_CHAT_URL, payload, {"Authorization": f"Bearer {key}"})

    try:
        choice = data["choices"][0]
    except (KeyError, IndexError):
        raise LLMError(f"text response had no choices: {str(data)[:300]}") from None

    text = (choice.get("message", {}).get("content") or "").strip()
    if not text:
        # Almost always the budget being consumed by reasoning before any
        # visible token is produced — say so instead of failing further down
        # with an unhelpful JSON parse error.
        raise LLMError(
            f"model returned no text (finish_reason="
            f"{choice.get('finish_reason')!r}); raise max_tokens or lower effort"
        )

    usage = data.get("usage", {})
    completion_details = usage.get("completion_tokens_details") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    LAST_TEXT_MODEL = data.get("model", OPENAI_TEXT_MODEL)
    return TextResult(
        text=text,
        provider="openai",
        model=LAST_TEXT_MODEL,
        input_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("completion_tokens", 0),
        reasoning_tokens=completion_details.get("reasoning_tokens", 0),
        cached_input_tokens=prompt_details.get("cached_tokens", 0),
    )


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def generate_json(
    system: str,
    prompt: str,
    *,
    max_tokens: int = 4000,
    retries: int = 1,
) -> tuple[object, TextResult]:
    """Text turn that must return JSON.

    Deliberately **not** using ``response_format: json_object``: two stages of
    the pipeline (concepts, shots) return a top-level JSON *array*, which that
    mode forbids. So the instruction stays prompt-level and the parse stays
    forgiving — fences and leading prose are stripped before parsing, and a
    failure retries once with the parse error fed back.

    The retry used to also drop the temperature to 0.2. This model accepts only
    the default temperature, so the retry is now purely the error feedback.
    """
    instruction = (
        f"{system}\n\nReturn only valid JSON. No prose, no markdown fence, "
        "no commentary before or after."
    )
    attempt_prompt = prompt
    last_error = ""
    for attempt in range(retries + 1):
        result = generate_text(
            instruction,
            attempt_prompt,
            max_tokens=max_tokens,
        )
        raw = result.text
        fence = _FENCE.search(raw)
        if fence:
            raw = fence.group(1)
        start = min(
            (i for i in (raw.find("{"), raw.find("[")) if i != -1),
            default=-1,
        )
        if start > 0:
            raw = raw[start:]
        try:
            return json.loads(raw), result
        except json.JSONDecodeError as error:
            last_error = str(error)
            attempt_prompt = (
                f"{prompt}\n\nYour previous reply could not be parsed as JSON "
                f"({last_error}). Return only the JSON value."
            )
    raise LLMError(f"model did not return parseable JSON: {last_error}")


# ---------------------------------------------------------------------------
# images
# ---------------------------------------------------------------------------


def generate_image(
    prompt: str,
    *,
    size: str = OPENAI_IMAGE_SIZE,
    quality: str = "medium",
    reference: Path | None = None,
) -> bytes:
    """Render one shot, natively at 9:16.

    ``reference`` is the user's uploaded cat photo. When present the call goes
    to the edits endpoint so the same animal carries across shots — this is the
    mechanism hypothesis 4 is testing, not an incidental detail.
    """
    load_dotenv()
    key = _key("OPENAI_API_KEY")
    if not key:
        raise LLMError("OPENAI_API_KEY is not set — cannot generate images")

    if reference is not None:
        return _image_edit(prompt, reference, size, quality, key)

    data = _post_json(
        OPENAI_IMAGE_URL,
        {
            "model": OPENAI_IMAGE_MODEL,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1,
        },
        {"Authorization": f"Bearer {key}"},
    )
    return _decode_image(data)


def _decode_image(data: dict) -> bytes:
    import base64

    try:
        entry = data["data"][0]
    except (KeyError, IndexError):
        raise LLMError(f"image response had no data: {str(data)[:300]}") from None
    if "b64_json" in entry:
        return base64.b64decode(entry["b64_json"])
    if "url" in entry:
        with urllib.request.urlopen(entry["url"], timeout=TIMEOUT) as response:
            return response.read()
    raise LLMError("image response contained neither b64_json nor url")


def _image_edit(
    prompt: str, reference: Path, size: str, quality: str, key: str
) -> bytes:
    """multipart/form-data by hand — the one place stdlib-only costs us."""
    import mimetypes
    import uuid

    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(reference.name)[0] or "image/png"
    parts: list[bytes] = []

    def field(name: str, value: str) -> None:
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
            f"\r\n\r\n{value}\r\n".encode("utf-8")
        )

    field("model", OPENAI_IMAGE_MODEL)
    field("prompt", prompt)
    field("size", size)
    field("quality", quality)
    field("n", "1")
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="image"; '
        f'filename="{reference.name}"\r\nContent-Type: {mime}\r\n\r\n'.encode("utf-8")
    )
    parts.append(reference.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)

    request = urllib.request.Request(OPENAI_IMAGE_EDIT_URL, data=body, method="POST")
    request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    request.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return _decode_image(json.loads(response.read().decode("utf-8")))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:600]
        raise LLMError(f"image edit returned {error.code}: {detail}") from None


# ---------------------------------------------------------------------------
# speech
# ---------------------------------------------------------------------------


def generate_speech(
    text: str,
    *,
    voice: str = "alloy",
    instructions: str | None = None,
    model: str = OPENAI_TTS_MODEL,
) -> bytes:
    """Narrate one line. Returns MP3 bytes.

    This replaces the browser's ``speechSynthesis`` for narration. The browser
    path is kept as a fallback, but it depends on a Thai voice being installed
    in the operating system, which is not true on most machines — the narration
    was therefore silent or unintelligible for anyone but the author. A
    generated MP3 is also an artifact: it lands next to the shot images, is
    replayable without re-running the pipeline, and can be graded like them.

    ``instructions`` is a delivery note (tone, pace). It is supported by the
    ``gpt-4o-mini-tts`` family and ignored by the older ``tts-1`` models.
    """
    load_dotenv()
    key = _key("OPENAI_API_KEY")
    if not key:
        raise LLMError("OPENAI_API_KEY is not set — cannot generate narration")
    if not text.strip():
        raise LLMError("nothing to narrate")
    if voice not in TTS_VOICES:
        raise LLMError(f"unknown voice {voice!r}; expected one of {', '.join(TTS_VOICES)}")

    payload: dict[str, object] = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": "mp3",
    }
    if instructions:
        payload["instructions"] = instructions

    audio = _post_binary(OPENAI_SPEECH_URL, payload, {"Authorization": f"Bearer {key}"})
    if not audio:
        raise LLMError("speech response was empty")
    return audio


# ---------------------------------------------------------------------------
# cost accounting (criterion C6)
# ---------------------------------------------------------------------------

#: USD per million text tokens for `gpt-5.6-sol`.
#:
#: **Unset on purpose.** The previous values here were `gpt-4o-mini`'s
#: ($0.15/$0.60) and would silently under-report this model's cost by whatever
#: the real ratio turns out to be — a wrong number in a cost criterion is worse
#: than no number, because it looks measured. The API does not expose pricing,
#: so fill these in from the provider's pricing page (or set
#: `OPENAI_TEXT_PRICE_INPUT` / `OPENAI_TEXT_PRICE_OUTPUT` in `.env`). Until then
#: a run reports its text tokens and marks the dollar figure unpriced.
#:
#: Note reasoning tokens bill as output tokens and are already included in
#: `completion_tokens`; do not add them again.
TEXT_PRICE_USD: dict[str, float | None] = {"input": None, "output": None}

IMAGE_PRICE_USD = {"low": 0.011, "medium": 0.042, "high": 0.167}


def _text_rates() -> dict[str, float | None]:
    """Table value, overridden by env when present."""
    load_dotenv()
    rates = dict(TEXT_PRICE_USD)
    for field, name in (
        ("input", "OPENAI_TEXT_PRICE_INPUT"),
        ("output", "OPENAI_TEXT_PRICE_OUTPUT"),
    ):
        raw = _key(name)
        if raw:
            try:
                rates[field] = float(raw)
            except ValueError:
                raise LLMError(f"{name} is not a number: {raw!r}") from None
    return rates

#: USD per 1,000 characters of narrated text. `gpt-4o-mini-tts` is billed per
#: token rather than per character, so this is an ESTIMATE calibrated to the
#: provider's published "about $0.015 per minute of audio" figure at a normal
#: speaking rate. It is accurate enough to show that narration is a rounding
#: error next to images; do not quote it as a billed amount.
SPEECH_PRICE_USD_PER_1K_CHARS = 0.015


class CostMeter:
    """Accumulates what a single Reel run actually cost."""

    def __init__(self) -> None:
        self.text_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.images = 0
        self.image_quality = "medium"
        self.provider = ""
        self.model = ""
        self.reasoning_tokens = 0
        self.cached_input_tokens = 0
        self.speech_calls = 0
        self.speech_chars = 0

    def add_text(self, result: TextResult) -> None:
        self.text_calls += 1
        self.input_tokens += result.input_tokens
        self.output_tokens += result.output_tokens
        self.reasoning_tokens += result.reasoning_tokens
        self.cached_input_tokens += result.cached_input_tokens
        self.provider = result.provider
        self.model = result.model

    def add_image(self, quality: str = "medium") -> None:
        self.images += 1
        self.image_quality = quality

    def add_speech(self, characters: int) -> None:
        self.speech_calls += 1
        self.speech_chars += characters

    def summary(self) -> dict[str, object]:
        rates = _text_rates()
        priced = rates["input"] is not None and rates["output"] is not None
        text_usd = (
            self.input_tokens / 1_000_000 * rates["input"]
            + self.output_tokens / 1_000_000 * rates["output"]
            if priced
            else None
        )
        image_usd = self.images * IMAGE_PRICE_USD.get(self.image_quality, 0.042)
        speech_usd = self.speech_chars / 1000 * SPEECH_PRICE_USD_PER_1K_CHARS
        known_usd = image_usd + speech_usd + (text_usd or 0.0)
        return {
            "text_provider": self.provider,
            "text_model": self.model,
            "text_calls": self.text_calls,
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "images": self.images,
            "speech_calls": self.speech_calls,
            "speech_chars": self.speech_chars,
            "text_usd": round(text_usd, 4) if priced else None,
            # False means the text tokens above are real but their dollar value
            # is not known — the total is a floor, not the bill.
            "text_priced": priced,
            "image_usd": round(image_usd, 4),
            "speech_usd_estimated": round(speech_usd, 4),
            "total_usd": round(known_usd, 4),
            "total_is_complete": priced,
        }
