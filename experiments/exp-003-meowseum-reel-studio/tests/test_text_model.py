"""Tests for the gpt-5.6-sol text path.

The request shape is the point. `max_tokens` and a non-default `temperature`
both return 400 on this model, and both were in the previous build's payload —
these tests pin the corrected shape so a future edit cannot quietly put them
back.

The HTTP call is stubbed; what is under test is the payload we construct and
the usage we read back, not the provider.

Run from the experiment folder:

    python -m unittest discover -s tests -t .
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import llm  # noqa: E402


def response(text: str = '{"ok": true}', **usage_overrides) -> dict:
    usage = {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "completion_tokens_details": {"reasoning_tokens": 30},
        "prompt_tokens_details": {"cached_tokens": 20},
    }
    usage.update(usage_overrides)
    return {
        "model": "gpt-5.6-sol",
        "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
        "usage": usage,
    }


class TextPathTestCase(unittest.TestCase):
    """Captures the payload `generate_text` would have sent."""

    def setUp(self):
        self.sent: list[dict] = []
        self.reply = response()
        self.original = llm._post_json

        def fake_post(url, payload, headers):
            self.sent.append({"url": url, "payload": payload, "headers": headers})
            return self.reply

        llm._post_json = fake_post
        os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY") or "test-key"

    def tearDown(self):
        llm._post_json = self.original

    @property
    def payload(self) -> dict:
        return self.sent[-1]["payload"]


class TestRequestShape(TextPathTestCase):
    def test_uses_max_completion_tokens_not_max_tokens(self):
        llm.generate_text("system", "prompt", max_tokens=4321)
        self.assertEqual(self.payload["max_completion_tokens"], 4321)
        # The old field name is a 400 on this model.
        self.assertNotIn("max_tokens", self.payload)

    def test_never_sends_temperature(self):
        llm.generate_text("system", "prompt")
        self.assertNotIn("temperature", self.payload)

    def test_targets_the_configured_model(self):
        llm.generate_text("system", "prompt")
        self.assertEqual(self.payload["model"], "gpt-5.6-sol")
        self.assertEqual(llm.OPENAI_TEXT_MODEL, "gpt-5.6-sol")

    def test_sends_reasoning_effort(self):
        llm.generate_text("system", "prompt", effort="low")
        self.assertEqual(self.payload["reasoning_effort"], "low")

    def test_json_object_mode_is_opt_in(self):
        llm.generate_text("system", "prompt")
        self.assertNotIn("response_format", self.payload)
        llm.generate_text("system", "prompt", json_object=True)
        self.assertEqual(self.payload["response_format"], {"type": "json_object"})

    def test_system_and_user_are_separate_messages(self):
        llm.generate_text("SYS", "USER")
        self.assertEqual(
            self.payload["messages"],
            [
                {"role": "system", "content": "SYS"},
                {"role": "user", "content": "USER"},
            ],
        )


class TestUsageAccounting(TextPathTestCase):
    def test_reads_reasoning_and_cached_tokens(self):
        result = llm.generate_text("system", "prompt")
        self.assertEqual(result.input_tokens, 100)
        self.assertEqual(result.output_tokens, 50)
        self.assertEqual(result.reasoning_tokens, 30)
        self.assertEqual(result.cached_input_tokens, 20)

    def test_missing_usage_details_do_not_crash(self):
        self.reply = {
            "model": "gpt-5.6-sol",
            "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        }
        result = llm.generate_text("system", "prompt")
        self.assertEqual(result.reasoning_tokens, 0)
        self.assertEqual(result.cached_input_tokens, 0)


class TestEmptyOutput(TextPathTestCase):
    """The budget covers reasoning + output, so it can be spent before any text."""

    def test_empty_content_is_a_clear_error(self):
        self.reply = {
            "model": "gpt-5.6-sol",
            "choices": [{"message": {"content": ""}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4000},
        }
        with self.assertRaises(llm.LLMError) as caught:
            llm.generate_text("system", "prompt")
        message = str(caught.exception)
        self.assertIn("no text", message)
        self.assertIn("length", message)  # the finish_reason is surfaced

    def test_null_content_is_handled(self):
        self.reply = {
            "model": "gpt-5.6-sol",
            "choices": [{"message": {"content": None}, "finish_reason": "length"}],
            "usage": {},
        }
        with self.assertRaises(llm.LLMError):
            llm.generate_text("system", "prompt")


class TestJsonParsing(TextPathTestCase):
    def test_fenced_json_still_parses(self):
        self.reply = response('```json\n{"a": 1}\n```')
        data, _ = llm.generate_json("system", "prompt")
        self.assertEqual(data, {"a": 1})

    def test_top_level_array_parses(self):
        # concepts and shots return arrays — this is why json_object mode is off
        self.reply = response('[{"id": "funny"}]')
        data, _ = llm.generate_json("system", "prompt")
        self.assertEqual(data, [{"id": "funny"}])

    def test_unparseable_json_retries_then_raises(self):
        self.reply = response("not json at all")
        with self.assertRaises(llm.LLMError):
            llm.generate_json("system", "prompt", retries=1)
        self.assertEqual(len(self.sent), 2)  # original + one retry


class TestTextPricing(unittest.TestCase):
    """C6 must not report a made-up number for an unpriced model."""

    def setUp(self):
        self.saved = {
            name: os.environ.pop(name, None)
            for name in ("OPENAI_TEXT_PRICE_INPUT", "OPENAI_TEXT_PRICE_OUTPUT")
        }

    def tearDown(self):
        for name, value in self.saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def meter(self) -> llm.CostMeter:
        meter = llm.CostMeter()
        meter.add_text(
            llm.TextResult(
                text="x",
                provider="openai",
                model="gpt-5.6-sol",
                input_tokens=1_000_000,
                output_tokens=1_000_000,
                reasoning_tokens=500_000,
            )
        )
        return meter

    def test_unpriced_by_default(self):
        summary = self.meter().summary()
        self.assertIsNone(summary["text_usd"])
        self.assertFalse(summary["text_priced"])
        self.assertFalse(summary["total_is_complete"])
        # Tokens are still reported — only the dollar figure is withheld.
        self.assertEqual(summary["input_tokens"], 1_000_000)
        self.assertEqual(summary["reasoning_tokens"], 500_000)

    def test_env_supplies_the_rates(self):
        os.environ["OPENAI_TEXT_PRICE_INPUT"] = "1.25"
        os.environ["OPENAI_TEXT_PRICE_OUTPUT"] = "10"
        summary = self.meter().summary()
        self.assertTrue(summary["text_priced"])
        self.assertTrue(summary["total_is_complete"])
        self.assertAlmostEqual(summary["text_usd"], 11.25, places=4)

    def test_half_configured_is_treated_as_unpriced(self):
        os.environ["OPENAI_TEXT_PRICE_INPUT"] = "1.25"
        summary = self.meter().summary()
        self.assertFalse(summary["text_priced"])

    def test_non_numeric_rate_is_rejected(self):
        os.environ["OPENAI_TEXT_PRICE_INPUT"] = "cheap"
        os.environ["OPENAI_TEXT_PRICE_OUTPUT"] = "10"
        with self.assertRaises(llm.LLMError):
            self.meter().summary()

    def test_total_still_counts_images_and_speech(self):
        meter = self.meter()
        for _ in range(6):
            meter.add_image("low")
        meter.add_speech(1000)
        summary = meter.summary()
        self.assertFalse(summary["total_is_complete"])
        self.assertAlmostEqual(summary["total_usd"], 6 * 0.011 + 0.015, places=4)


class TestMediaModels(unittest.TestCase):
    """Image size and model are coupled — see the note on OPENAI_IMAGE_SIZE."""

    def test_image_model_and_size(self):
        self.assertEqual(llm.OPENAI_IMAGE_MODEL, "gpt-image-2")
        self.assertEqual(llm.OPENAI_IMAGE_SIZE, "864x1536")

    def test_image_size_is_true_9_16(self):
        width, height = (int(n) for n in llm.OPENAI_IMAGE_SIZE.split("x"))
        self.assertAlmostEqual(width / height, 9 / 16, places=6)

    def test_image_size_sides_divisible_by_16(self):
        # gpt-image-2's stated constraint; a violation is a 400 on every shot.
        for side in llm.OPENAI_IMAGE_SIZE.split("x"):
            self.assertEqual(int(side) % 16, 0, f"{side} is not divisible by 16")

    def test_generate_image_defaults_to_that_size(self):
        captured = {}
        original = llm._post_json

        def fake_post(url, payload, headers):
            captured.update(payload)
            return {"data": [{"b64_json": "aGk="}]}

        llm._post_json = fake_post
        try:
            llm.generate_image("a cat")
        finally:
            llm._post_json = original
        self.assertEqual(captured["size"], "864x1536")
        self.assertEqual(captured["model"], "gpt-image-2")

    def test_tts_model_is_a_speech_endpoint_model(self):
        # gpt-audio* are chat-with-audio models and 404 on /v1/audio/speech.
        self.assertTrue(llm.OPENAI_TTS_MODEL.startswith("gpt-4o-mini-tts"))
        self.assertFalse(llm.OPENAI_TTS_MODEL.startswith("gpt-audio"))


class TestProviderSurface(unittest.TestCase):
    def test_only_openai_is_reported(self):
        self.assertEqual(set(llm.available_providers()), {"openai"})

    def test_anthropic_path_is_gone(self):
        for attribute in ("ANTHROPIC_URL", "ANTHROPIC_MODEL", "LAST_TEXT_PROVIDER"):
            self.assertFalse(hasattr(llm, attribute), f"{attribute} still present")

    def test_missing_key_is_a_clear_error(self):
        saved = os.environ.pop("OPENAI_API_KEY", None)
        original = llm.load_dotenv
        llm.load_dotenv = lambda *a, **k: None  # don't repopulate from .env
        try:
            with self.assertRaises(llm.LLMError) as caught:
                llm.generate_text("system", "prompt")
            self.assertIn("OPENAI_API_KEY", str(caught.exception))
        finally:
            llm.load_dotenv = original
            if saved is not None:
                os.environ["OPENAI_API_KEY"] = saved


if __name__ == "__main__":
    unittest.main()
