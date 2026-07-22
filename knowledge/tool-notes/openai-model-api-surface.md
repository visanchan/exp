# Tool Notes — OpenAI Model API Surface Differs by Model Family

**Source:** `exp-003-meowseum-reel-studio` (2026-07-23)
**Applies to:** the OpenAI REST API accessed directly over HTTP

The headline: **swapping a model string is not a safe edit.** Within one
provider, model families disagree about parameter *names*, accepted *value
ranges*, which *endpoint* they belong to, and how they are *priced*. Each of the
following cost a 400 or a wrong number, and each was found by probing rather
than by reading.

## Verify the model ID exists before writing code against it

Model names heard secondhand are often not the API string. List what the key can
actually see:

```python
request = urllib.request.Request("https://api.openai.com/v1/models")
request.add_header("Authorization", f"Bearer {key}")
ids = sorted(m["id"] for m in json.load(urllib.request.urlopen(request))["data"])
```

A wrong ID 404s every call, and the error will not suggest the right one.

## Enumerate valid enum values for free

A deliberately invalid value returns an error **listing the accepted ones**, and
for image models this happens before anything is generated — so it costs
nothing:

```python
{"model": "<image-model>", "prompt": "a cat", "quality": "__probe__"}
# 400 Invalid value: '__probe__'. Supported values are: 'low', 'medium',
#     'high', and 'auto'.
```

Cheaper and more current than searching documentation. Use it for `quality`,
`size`, `response_format`, `voice`.

## Text: newer families rename and restrict parameters

Confirmed against a GPT-5-family model, contrasted with the `gpt-4o` family:

| Parameter | `gpt-4o` family | GPT-5 family |
|---|---|---|
| output budget | `max_tokens` | **`max_completion_tokens`** — `max_tokens` is a 400 |
| `temperature` | 0.0–2.0 | **default only** — 0.8, 0.2, 0.0 all 400; 1.0 or omitted is fine |
| `reasoning_effort` | not accepted | accepted (`low` / `medium` / …) |
| `response_format` | `json_object` | `json_object` |

```
400 Unsupported parameter: 'max_tokens' is not supported with this model.
    Use 'max_completion_tokens' instead.
400 Unsupported value: 'temperature' does not support 0.8 with this model.
    Only the default (1) value is supported.
```

Two consequences beyond the rename:

- **Per-stage temperature control disappears.** Any design that turns the
  temperature down for a retry, or up for a "creative" stage, needs another
  lever. `reasoning_effort` is the closest replacement.
- **The budget now covers reasoning *plus* visible output.** A budget that was
  generous for `gpt-4o` can be consumed entirely by reasoning, returning an
  empty string with `finish_reason: "length"`. Raise budgets substantially and
  fail loudly:

```python
if not text:
    raise LLMError(
        f"model returned no text (finish_reason={choice.get('finish_reason')!r}); "
        "raise max_tokens or lower effort"
    )
```

Usage reporting also gains detail worth capturing —
`completion_tokens_details.reasoning_tokens` (billed as output, invisible in the
text) and `prompt_tokens_details.cached_tokens`.

## Images: size constraints are model-specific and couple to the model

| | older image model | newer image model |
|---|---|---|
| `size` | fixed list: `1024x1024`, `1024x1536`, `1536x1024`, `auto` | any size with **both sides divisible by 16** |
| `quality` | `low` / `medium` / `high` / `auto` | same |

The newer model accepting arbitrary 16-divisible sizes means a true 9:16 frame
becomes available — `864x1536` is exact 9:16 and the largest such size that
satisfies the rule. That removes a centre-crop that had been discarding ~16% of
every frame.

**The model and the size are one change, not two.** Reverting the model without
reverting the size gives
`400 Invalid size '864x1536'. Supported sizes are 1024x1024, 1024x1536, ...`.
Pin them together and assert it in a test.

## Speech: "newest model" and "newest speech model" are different questions

`/v1/audio/speech` accepts a *specific* family. Models with newer-sounding names
may belong to a different endpoint entirely:

| Model | On `/v1/audio/speech` |
|---|---|
| `gpt-4o-mini-tts` (+ dated snapshots) | ✅ works — the current TTS family |
| `tts-1`, `tts-1-hd` | ✅ works — previous generation |
| `gpt-audio`, `gpt-audio-1.5`, `gpt-audio-mini` | ❌ `Invalid URL (POST /v1/audio/speech)` |

The `gpt-audio*` family is chat-with-audio, not speech synthesis. Do not assume
a higher version number means an upgrade for your endpoint — probe it.

Pinning a dated snapshot (`...-2025-12-15`) rather than the floating alias buys
reproducibility, which matters when written results reference specific outputs.

## Pricing does not follow the provider

A cost meter keyed by *provider* silently reprices when the *model* changes, and
the resulting figure looks exactly as authoritative as a correct one. Key rates
to the model, and when a rate is unknown, report it as unknown:

```python
TEXT_PRICE_USD = {"input": None, "output": None}   # set from the pricing page
...
"text_usd": round(text_usd, 4) if priced else None,
"text_priced": priced,
"total_is_complete": priced,     # total is a floor, not the bill
```

The API does not expose pricing; it has to come from the pricing page or an env
var. A wrong number in a cost metric is worse than an absent one.

## Checklist for any model swap

- [ ] Confirm the model ID exists on the key (`/v1/models`).
- [ ] Probe the request shape with one cheap call before editing code.
- [ ] Enumerate enums with a deliberate 400.
- [ ] Check parameter *names* (`max_tokens` vs `max_completion_tokens`).
- [ ] Check accepted *ranges* (`temperature` may be fixed).
- [ ] Re-check token budgets if reasoning tokens now share them.
- [ ] Confirm the endpoint accepts the model at all.
- [ ] Update pricing, or mark it unpriced.
- [ ] Pin coupled parameters (model + size) together, with a test.
