"""Tests for generated narration audio (the TTS path).

No network: the speech call is replaced with a stub, because what needs
checking here is the pipeline's behaviour around the call — file naming,
cost accounting, and what happens when a line fails — not the provider.

Run from the experiment folder:

    python -m unittest discover -s tests -t .
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import llm  # noqa: E402
import pipeline  # noqa: E402

SHOTS = [
    {"shot_number": 1, "narration": "ภัณฑารักษ์แมวเปิดห้องจัดแสดง", "duration_seconds": 5},
    {"shot_number": 2, "narration": "เขาจ้องผลงานอย่างจริงจัง", "duration_seconds": 5},
    {"shot_number": 3, "narration": "", "duration_seconds": 5},
]


class StubSpeech:
    """Records what it was asked to say, returns plausible MP3 bytes."""

    def __init__(self, fail_on: int | None = None):
        self.calls: list[dict] = []
        self.fail_on = fail_on

    def __call__(self, text, *, voice="alloy", instructions=None, model=None):
        self.calls.append({"text": text, "voice": voice, "instructions": instructions})
        if self.fail_on is not None and len(self.calls) == self.fail_on:
            raise llm.LLMError("stubbed provider failure")
        return b"ID3" + b"\x00" * 64


class NarrationTestCase(unittest.TestCase):
    def setUp(self):
        self.original = llm.generate_speech
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        llm.generate_speech = self.original
        self.tmp.cleanup()


class TestVoiceValidation(unittest.TestCase):
    """An unknown voice must fail before any paid call is made."""

    def test_unknown_voice_refused(self):
        with self.assertRaises(llm.LLMError) as caught:
            llm.generate_speech("hello", voice="nonexistent-voice")
        self.assertIn("unknown voice", str(caught.exception))

    def test_empty_text_refused(self):
        with self.assertRaises(llm.LLMError):
            llm.generate_speech("   ", voice="alloy")

    def test_default_voice_is_a_known_voice(self):
        self.assertIn(pipeline.ReelSettings().voice, llm.TTS_VOICES)


class TestRenderNarration(NarrationTestCase):
    def test_one_mp3_per_spoken_shot(self):
        llm.generate_speech = StubSpeech()
        meter = llm.CostMeter()
        result = pipeline.render_narration(
            SHOTS, self.out, meter, pipeline.ReelSettings()
        )
        self.assertEqual(result[0]["audio_file"], "narration-01.mp3")
        self.assertEqual(result[1]["audio_file"], "narration-02.mp3")
        self.assertTrue((self.out / "narration-01.mp3").exists())

    def test_shot_without_narration_is_skipped_silently(self):
        stub = StubSpeech()
        llm.generate_speech = stub
        result = pipeline.render_narration(
            SHOTS, self.out, llm.CostMeter(), pipeline.ReelSettings()
        )
        self.assertEqual(len(stub.calls), 2)  # not 3 — shot 3 has no line
        self.assertIsNone(result[2]["audio_file"])
        self.assertIsNone(result[2]["audio_error"])

    def test_a_failed_line_does_not_abort_the_run(self):
        llm.generate_speech = StubSpeech(fail_on=1)
        result = pipeline.render_narration(
            SHOTS, self.out, llm.CostMeter(), pipeline.ReelSettings()
        )
        self.assertIsNone(result[0]["audio_file"])
        self.assertIn("stubbed provider failure", result[0]["audio_error"])
        # The rest of the Reel still gets audio.
        self.assertEqual(result[1]["audio_file"], "narration-02.mp3")

    def test_settings_reach_the_provider(self):
        stub = StubSpeech()
        llm.generate_speech = stub
        pipeline.render_narration(
            SHOTS,
            self.out,
            llm.CostMeter(),
            pipeline.ReelSettings(voice="sage", language="th", tone="funny"),
        )
        self.assertEqual(stub.calls[0]["voice"], "sage")
        self.assertIn("Thai", stub.calls[0]["instructions"])

    def test_original_shots_are_not_mutated(self):
        llm.generate_speech = StubSpeech()
        pipeline.render_narration(
            SHOTS, self.out, llm.CostMeter(), pipeline.ReelSettings()
        )
        self.assertNotIn("audio_file", SHOTS[0])


class TestSpeechCost(NarrationTestCase):
    """C6 — narration has to appear in the bill, not vanish into it."""

    def test_speech_is_metered_and_totalled(self):
        llm.generate_speech = StubSpeech()
        meter = llm.CostMeter()
        pipeline.render_narration(SHOTS, self.out, meter, pipeline.ReelSettings())
        summary = meter.summary()
        expected_chars = sum(len(s["narration"]) for s in SHOTS)
        self.assertEqual(summary["speech_calls"], 2)
        self.assertEqual(summary["speech_chars"], expected_chars)
        self.assertGreater(summary["speech_usd_estimated"], 0)
        self.assertEqual(summary["total_usd"], summary["speech_usd_estimated"])

    def test_narration_is_a_rounding_error_next_to_images(self):
        llm.generate_speech = StubSpeech()
        meter = llm.CostMeter()
        pipeline.render_narration(SHOTS, self.out, meter, pipeline.ReelSettings())
        for _ in range(6):
            meter.add_image("medium")
        summary = meter.summary()
        self.assertLess(summary["speech_usd_estimated"], summary["image_usd"] / 20)


if __name__ == "__main__":
    unittest.main()
