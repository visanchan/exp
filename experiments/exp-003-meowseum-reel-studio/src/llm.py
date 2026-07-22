"""Model clients — text agents and image generation.

Standard library only; both providers are plain JSON over HTTPS, and a handful
of endpoints does not justify two SDKs.

Text generation prefers Anthropic and falls back to OpenAI, chosen by which key
is present. The fallback exists because the experiment must be runnable with one
key rather than two — see the note in the experiment README. Which provider
actually served a run is recorded in ``LAST_TEXT_PROVIDER`` and written into the
run manifest, because "which model wrote this outline" is part of the result.

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

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
ANTHROPIC_MODEL = "claude-sonnet-5"

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
OPENAI_IMAGE_EDIT_URL = "https://api.openai.com/v1/images/edits"
OPENAI_TEXT_MODEL = "gpt-4o-mini"
OPENAI_IMAGE_MODEL = "gpt-image-1"

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
    load_dotenv()
    return {
        "anthropic": bool(_key("ANTHROPIC_API_KEY")),
        "openai": bool(_key("OPENAI_API_KEY")),
    }


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


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------

LAST_TEXT_PROVIDER = ""


def generate_text(
    system: str,
    prompt: str,
    *,
    max_tokens: int = 4000,
    temperature: float = 0.8,
) -> TextResult:
    """One text-agent turn, on whichever provider has a key."""
    global LAST_TEXT_PROVIDER
    load_dotenv()

    anthropic_key = _key("ANTHROPIC_API_KEY")
    if anthropic_key:
        data = _post_json(
            ANTHROPIC_URL,
            {
                "model": ANTHROPIC_MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
            {"x-api-key": anthropic_key, "anthropic-version": ANTHROPIC_VERSION},
        )
        blocks = [b.get("text", "") for b in data.get("content", [])]
        usage = data.get("usage", {})
        LAST_TEXT_PROVIDER = "anthropic"
        return TextResult(
            text="".join(blocks).strip(),
            provider="anthropic",
            model=data.get("model", ANTHROPIC_MODEL),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
        )

    openai_key = _key("OPENAI_API_KEY")
    if openai_key:
        data = _post_json(
            OPENAI_CHAT_URL,
            {
                "model": OPENAI_TEXT_MODEL,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
            {"Authorization": f"Bearer {openai_key}"},
        )
        usage = data.get("usage", {})
        LAST_TEXT_PROVIDER = "openai"
        return TextResult(
            text=data["choices"][0]["message"]["content"].strip(),
            provider="openai",
            model=data.get("model", OPENAI_TEXT_MODEL),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )

    raise LLMError(
        "no text provider key found — set ANTHROPIC_API_KEY or OPENAI_API_KEY"
    )


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def generate_json(
    system: str,
    prompt: str,
    *,
    max_tokens: int = 4000,
    temperature: float = 0.8,
    retries: int = 1,
) -> tuple[object, TextResult]:
    """Text turn that must return JSON.

    Models wrap JSON in prose or fences often enough that parsing needs to be
    forgiving; a hard failure retries once with the parse error fed back, which
    is cheaper and more reliable than tightening the prompt further.
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
            temperature=temperature if attempt == 0 else 0.2,
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
    size: str = "1024x1536",
    quality: str = "medium",
    reference: Path | None = None,
) -> bytes:
    """Render one shot. 1024x1536 is the portrait size closest to 9:16.

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
# cost accounting (criterion C6)
# ---------------------------------------------------------------------------

#: USD per million tokens, and USD per generated image. Published list prices,
#: recorded here so a run reports a number instead of a shrug. Update if the
#: provider changes pricing — the run manifest keeps whatever was used.
PRICING = {
    "anthropic": {"input": 3.00, "output": 15.00},
    "openai": {"input": 0.15, "output": 0.60},
}
IMAGE_PRICE_USD = {"low": 0.011, "medium": 0.042, "high": 0.167}


class CostMeter:
    """Accumulates what a single Reel run actually cost."""

    def __init__(self) -> None:
        self.text_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.images = 0
        self.image_quality = "medium"
        self.provider = ""

    def add_text(self, result: TextResult) -> None:
        self.text_calls += 1
        self.input_tokens += result.input_tokens
        self.output_tokens += result.output_tokens
        self.provider = result.provider

    def add_image(self, quality: str = "medium") -> None:
        self.images += 1
        self.image_quality = quality

    def summary(self) -> dict[str, object]:
        rates = PRICING.get(self.provider, PRICING["openai"])
        text_usd = (
            self.input_tokens / 1_000_000 * rates["input"]
            + self.output_tokens / 1_000_000 * rates["output"]
        )
        image_usd = self.images * IMAGE_PRICE_USD.get(self.image_quality, 0.042)
        return {
            "text_provider": self.provider,
            "text_calls": self.text_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "images": self.images,
            "text_usd": round(text_usd, 4),
            "image_usd": round(image_usd, 4),
            "total_usd": round(text_usd + image_usd, 4),
        }
