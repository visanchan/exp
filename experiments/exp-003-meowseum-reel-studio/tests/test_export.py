"""Tests for MP4 export.

The encoder itself is not under test — ffmpeg works or it does not, and a real
encode is covered by a recorded manual run in the README. What is tested here
is everything around it: binary discovery, the refusal when no H.264 encoder
exists, which shots make it into the file, and the duration rule.

Run from the experiment folder:

    python -m unittest discover -s tests -t .
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import export  # noqa: E402

FFMPEG_HEADER = """
Input #0, mp3, from 'narration-01.mp3':
  Duration: 00:00:07.20, start: 0.025057, bitrate: 128 kb/s
    Stream #0:0: Audio: mp3, 44100 Hz, mono, fltp, 128 kb/s
"""


def manifest_with(shots):
    return {"shots": shots}


class TestDurationParsing(unittest.TestCase):
    """The segment length comes out of ffmpeg's own header dump."""

    def test_reads_hours_minutes_seconds(self):
        match = export._DURATION.search(FFMPEG_HEADER)
        self.assertIsNotNone(match)
        hours, minutes, seconds = match.groups()
        total = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        self.assertAlmostEqual(total, 7.20, places=2)

    def test_no_duration_line_is_not_a_crash(self):
        self.assertIsNone(export._DURATION.search("Output #0, mp4, to 'x.mp4':"))


class TestDiscovery(unittest.TestCase):
    def setUp(self):
        self.saved = os.environ.get("FFMPEG_BINARY")
        export._CAPABILITY = None

    def tearDown(self):
        if self.saved is None:
            os.environ.pop("FFMPEG_BINARY", None)
        else:
            os.environ["FFMPEG_BINARY"] = self.saved
        export._CAPABILITY = None

    def test_override_pointing_nowhere_finds_nothing(self):
        os.environ["FFMPEG_BINARY"] = r"C:\nope\ffmpeg.exe"
        self.assertIsNone(export.find_ffmpeg())

    def test_override_wins_over_path(self):
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as handle:
            fake = Path(handle.name)
        try:
            os.environ["FFMPEG_BINARY"] = str(fake)
            self.assertEqual(export.find_ffmpeg(), fake)
        finally:
            fake.unlink()

    def test_missing_ffmpeg_is_reported_not_raised(self):
        os.environ["FFMPEG_BINARY"] = r"C:\nope\ffmpeg.exe"
        caps = export.capability(refresh=True)
        self.assertFalse(caps.available)
        self.assertIn("FFMPEG_BINARY", caps.reason)


class ExportOrchestrationTest(unittest.TestCase):
    """The encode is stubbed; what runs is the shot selection and reporting."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.tmp.name)
        self.saved_capability = export._CAPABILITY
        self.saved_segment = export._segment
        self.saved_run = export._run
        export._CAPABILITY = export.Capability(
            True, binary="ffmpeg", video_encoder="libx264"
        )
        self.encoded: list[dict] = []

        def fake_segment(binary, encoder, image, audio, planned, target):
            seconds = round(max(planned, 0.0 + export.TAIL_SECONDS), 3)
            self.encoded.append(
                {"image": image.name, "audio": audio.name if audio else None}
            )
            target.write_bytes(b"fake segment")
            return seconds

        def fake_run(command, what):
            # The concat step: stand in for ffmpeg by creating the output file.
            Path(command[-1]).write_bytes(b"fake mp4")

        export._segment = fake_segment
        export._run = fake_run

    def tearDown(self):
        export._CAPABILITY = self.saved_capability
        export._segment = self.saved_segment
        export._run = self.saved_run
        self.tmp.cleanup()

    def make(self, name: str) -> str:
        (self.run_dir / name).write_bytes(b"x")
        return name


class TestWhatGetsEncoded(ExportOrchestrationTest):
    def test_every_shot_with_an_image_is_encoded(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": n,
                    "image_file": self.make(f"shot-0{n}.png"),
                    "audio_file": self.make(f"narration-0{n}.mp3"),
                    "duration_seconds": 5,
                }
                for n in (1, 2)
            ]
        )
        report = export.export_mp4(manifest, self.run_dir)
        self.assertEqual(report["shots_encoded"], 2)
        self.assertEqual(report["shots_skipped"], [])
        self.assertEqual(report["silent_shots"], 0)

    def test_a_shot_whose_image_failed_is_left_out_and_reported(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": 1,
                    "image_file": self.make("shot-01.png"),
                    "audio_file": self.make("narration-01.mp3"),
                    "duration_seconds": 5,
                },
                {"shot_number": 2, "image_file": None, "duration_seconds": 5},
            ]
        )
        report = export.export_mp4(manifest, self.run_dir)
        self.assertEqual(report["shots_encoded"], 1)
        self.assertEqual(report["shots_skipped"], [{"shot": 2, "why": "no image file"}])

    def test_a_shot_whose_narration_failed_is_still_shown_silently(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": 1,
                    "image_file": self.make("shot-01.png"),
                    "audio_file": None,
                    "duration_seconds": 5,
                }
            ]
        )
        report = export.export_mp4(manifest, self.run_dir)
        self.assertEqual(report["shots_encoded"], 1)
        self.assertEqual(report["silent_shots"], 1)
        self.assertIsNone(self.encoded[0]["audio"])

    def test_an_audio_file_named_but_missing_falls_back_to_silence(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": 1,
                    "image_file": self.make("shot-01.png"),
                    "audio_file": "narration-01.mp3",  # never written
                    "duration_seconds": 5,
                }
            ]
        )
        report = export.export_mp4(manifest, self.run_dir)
        self.assertEqual(report["silent_shots"], 1)

    def test_a_run_with_no_usable_shot_refuses(self):
        manifest = manifest_with([{"shot_number": 1, "image_file": None}])
        with self.assertRaises(export.ExportError):
            export.export_mp4(manifest, self.run_dir)

    def test_an_empty_run_refuses(self):
        with self.assertRaises(export.ExportError):
            export.export_mp4(manifest_with([]), self.run_dir)


class TestReport(ExportOrchestrationTest):
    def test_report_is_written_beside_the_video(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": 1,
                    "image_file": self.make("shot-01.png"),
                    "audio_file": self.make("narration-01.mp3"),
                    "duration_seconds": 5,
                }
            ]
        )
        report = export.export_mp4(manifest, self.run_dir)
        saved = json.loads((self.run_dir / "export.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["file"], "reel.mp4")
        self.assertEqual(saved["shots_encoded"], report["shots_encoded"])
        self.assertEqual(report["resolution"], "1080x1920")

    def test_working_files_are_cleaned_up(self):
        manifest = manifest_with(
            [
                {
                    "shot_number": 1,
                    "image_file": self.make("shot-01.png"),
                    "duration_seconds": 5,
                }
            ]
        )
        export.export_mp4(manifest, self.run_dir)
        self.assertFalse((self.run_dir / "export").exists())


class TestUnavailableExport(ExportOrchestrationTest):
    def test_no_encoder_means_a_clear_refusal(self):
        export._CAPABILITY = export.Capability(
            False, binary="ffmpeg", reason="no H.264 encoder"
        )
        with self.assertRaises(export.ExportError) as caught:
            export.export_mp4(manifest_with([{"shot_number": 1}]), self.run_dir)
        self.assertIn("no H.264 encoder", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
