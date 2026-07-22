"""Local web server for Meowseum Reel Studio.

`http.server` with a handful of JSON endpoints and one Server-Sent Events
stream for the progress terminal. No framework: the whole surface is five
routes, and a dependency here would cost more than it saves.

    python src/server.py          # then open http://localhost:8000

Endpoints:

    GET  /                     the studio UI
    GET  /api/sources          pages that have a committed snapshot
    GET  /api/source?url=...   one extracted record (story view only)
    POST /api/upload           store a cat photo for this session
    POST /api/reel             start a run; returns a run id
    POST /api/export/<id>      encode that run into reel.mp4
    GET  /api/stream/<id>      SSE progress for a run
    GET  /api/run/<id>         the finished manifest
    GET  /artifacts/<...>      generated images and narration MP3s
"""

from __future__ import annotations

import json
import queue
import sys
import threading
import traceback
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import export  # noqa: E402
import llm  # noqa: E402
import pipeline  # noqa: E402
import source_agent as sa  # noqa: E402

WEB_DIR = ROOT / "web"
ARTIFACTS = ROOT / "artifacts"
PORT = 8000

#: Uploaded photos are capped — a reference image only needs to be legible.
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

RUNS: dict[str, dict] = {}
RUNS_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# run bookkeeping
# ---------------------------------------------------------------------------


def new_run() -> str:
    run_id = uuid.uuid4().hex[:12]
    with RUNS_LOCK:
        RUNS[run_id] = {
            "id": run_id,
            "status": "starting",
            "events": queue.Queue(),
            "manifest": None,
            "error": None,
        }
    return run_id


def emit(run_id: str, stage: str, message: str) -> None:
    with RUNS_LOCK:
        run = RUNS.get(run_id)
    if run:
        run["events"].put({"stage": stage, "message": message})


def execute(run_id: str, url: str, settings: pipeline.ReelSettings,
            concept_id: str | None, reference: Path | None,
            quality: str) -> None:
    """Run the whole pipeline on a worker thread."""

    def progress(stage: str, message: str) -> None:
        emit(run_id, stage, message)

    try:
        emit(run_id, "source", f"extracting {url}")
        record = sa.extract(url)
        emit(
            run_id,
            "source",
            f"{record.title} — {len(record.fields)} usable fields, "
            f"{'verified' if record.verified_for_marketing else 'unverified'} "
            "for marketing",
        )

        run, meter = pipeline.plan_reel(
            record, settings, concept_id=concept_id, progress=progress
        )

        out_dir = ARTIFACTS / run_id
        run.shots_final = pipeline.render_images(
            run.shots_final,
            out_dir,
            meter,
            reference=reference,
            quality=quality,
            progress=progress,
        )
        if settings.narrate:
            run.shots_final = pipeline.render_narration(
                run.shots_final, out_dir, meter, settings, progress=progress
            )
        run.cost = meter.summary()

        manifest = run.manifest()
        manifest["run_id"] = run_id
        manifest["image_base"] = f"/artifacts/{run_id}"
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        with RUNS_LOCK:
            RUNS[run_id]["manifest"] = manifest
            RUNS[run_id]["status"] = "done"
        cost = manifest["cost"]
        total = f"${cost['total_usd']}" + ("" if cost["total_is_complete"] else "+")
        emit(run_id, "done", f"reel ready — {total}")
    except Exception as error:  # noqa: BLE001 — surfaced to the UI verbatim
        detail = f"{type(error).__name__}: {error}"
        traceback.print_exc()
        with RUNS_LOCK:
            RUNS[run_id]["status"] = "error"
            RUNS[run_id]["error"] = detail
        emit(run_id, "error", detail)


# ---------------------------------------------------------------------------
# http
# ---------------------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # quieter console
        if "/api/stream" not in (args[0] if args else ""):
            sys.stderr.write(f"  {fmt % args}\n")

    # -- helpers ---------------------------------------------------------

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: object, code: int = 200) -> None:
        self._send(
            code,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self._json({"error": "not found"}, 404)
            return
        types = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".png": "image/png",
            ".mp3": "audio/mpeg",
            ".mp4": "video/mp4",
            ".json": "application/json; charset=utf-8",
        }
        self._send(200, path.read_bytes(), types.get(path.suffix, "application/octet-stream"))

    def _body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    # -- GET -------------------------------------------------------------

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path
        params = parse_qs(parsed.query)

        if route in ("/", "/index.html"):
            self._file(WEB_DIR / "index.html")
        elif route in ("/app.js", "/styles.css"):
            self._file(WEB_DIR / route.lstrip("/"))
        elif route == "/api/health":
            self._json(
                {
                    "providers": llm.available_providers(),
                    "text_model": llm.OPENAI_TEXT_MODEL,
                    "image_model": llm.OPENAI_IMAGE_MODEL,
                    "image_size": llm.OPENAI_IMAGE_SIZE,
                    "speech_model": llm.OPENAI_TTS_MODEL,
                    "voices": list(llm.TTS_VOICES),
                    "export": export.capability().as_dict(),
                }
            )
        elif route == "/api/sources":
            self._json(self._sources())
        elif route == "/api/source":
            self._source(params)
        elif route.startswith("/api/stream/"):
            self._stream(route.rsplit("/", 1)[-1])
        elif route.startswith("/api/run/"):
            run_id = route.rsplit("/", 1)[-1]
            with RUNS_LOCK:
                run = RUNS.get(run_id)
            if not run:
                self._json({"error": "unknown run"}, 404)
            else:
                self._json(
                    {
                        "status": run["status"],
                        "error": run["error"],
                        "manifest": run["manifest"],
                    }
                )
        elif route.startswith("/artifacts/"):
            relative = route[len("/artifacts/") :]
            target = (ARTIFACTS / relative).resolve()
            if ARTIFACTS.resolve() not in target.parents:
                self._json({"error": "refused"}, 403)
            else:
                self._file(target)
        else:
            self._json({"error": "not found"}, 404)

    def _sources(self) -> list[dict]:
        out = []
        for url in sa.list_snapshots():
            try:
                record = sa.extract(url)
            except sa.SourceError:
                continue
            out.append(
                {
                    "url": url,
                    "type": record.source_type,
                    "title": record.title,
                    "thai_title": record.thai_title,
                    "room": (record.fields.get("room") or {}).get("en", ""),
                    "category": record.fields.get("category", ""),
                    "image": record.images[0] if record.images else None,
                    "verified_for_marketing": record.verified_for_marketing,
                }
            )
        return out

    def _source(self, params: dict) -> None:
        url = (params.get("url") or [""])[0]
        try:
            record = sa.extract(url)
        except sa.SourceError as error:
            self._json({"error": str(error)}, 400)
            return
        payload = asdict(record)
        # The UI shows the quarantine as a count, never the values, so the
        # browser cannot leak what the agents were not allowed to see.
        payload["transactional"] = {"withheld_fields": len(record.transactional)}
        payload["story_context"] = record.story_context()
        self._json(payload)

    def _stream(self, run_id: str) -> None:
        with RUNS_LOCK:
            run = RUNS.get(run_id)
        if not run:
            self._json({"error": "unknown run"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        events: queue.Queue = run["events"]
        while True:
            try:
                event = events.get(timeout=30)
            except queue.Empty:
                try:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
                continue
            try:
                payload = json.dumps(event, ensure_ascii=False)
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
            if event["stage"] in ("done", "error"):
                return

    # -- POST ------------------------------------------------------------

    def do_POST(self):  # noqa: N802
        route = urlparse(self.path).path
        if route == "/api/upload":
            self._upload()
        elif route == "/api/reel":
            self._reel()
        elif route.startswith("/api/export/"):
            self._export(route.rsplit("/", 1)[-1])
        else:
            self._json({"error": "not found"}, 404)

    def _export(self, run_id: str) -> None:
        """Encode a finished run to MP4. Synchronous — it takes seconds, not
        minutes, and unlike generation it costs nothing to retry."""
        run_dir = (ARTIFACTS / Path(run_id).name).resolve()
        if ARTIFACTS.resolve() not in run_dir.parents or not run_dir.is_dir():
            self._json({"error": "unknown run"}, 404)
            return

        # Read the manifest from disk rather than RUNS, so a run from an
        # earlier server session can still be exported.
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            self._json({"error": "this run has no manifest"}, 400)
            return

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            report = export.export_mp4(
                manifest, run_dir, progress=lambda s, m: emit(run_id, s, m)
            )
        except export.ExportError as error:
            self._json({"error": str(error)}, 400)
            return
        except (OSError, json.JSONDecodeError) as error:
            self._json({"error": f"{type(error).__name__}: {error}"}, 500)
            return

        report["url"] = f"/artifacts/{run_id}/{report['file']}"
        self._json(report)

    def _upload(self) -> None:
        """Store the reference photo. Kept in artifacts/, which is git-ignored."""
        raw = self._body()
        if not raw:
            self._json({"error": "empty upload"}, 400)
            return
        if len(raw) > MAX_UPLOAD_BYTES:
            self._json({"error": "file too large (max 8 MB)"}, 413)
            return
        suffix = ".png" if raw[:8].startswith(b"\x89PNG") else ".jpg"
        uploads = ARTIFACTS / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        target = uploads / f"cat-{uuid.uuid4().hex[:8]}{suffix}"
        target.write_bytes(raw)
        self._json({"reference": target.name, "bytes": len(raw)})

    def _reel(self) -> None:
        try:
            payload = json.loads(self._body() or b"{}")
        except json.JSONDecodeError as error:
            self._json({"error": f"bad JSON: {error}"}, 400)
            return

        url = payload.get("url", "")
        try:
            sa.verify_host(url)
        except sa.SourceError as error:
            self._json({"error": str(error)}, 400)
            return

        # An unknown voice would fail on every shot, six calls deep into a paid
        # run — reject it here instead.
        voice = payload.get("voice", "alloy")
        if voice not in llm.TTS_VOICES:
            self._json({"error": f"unknown voice {voice!r}"}, 400)
            return

        settings = pipeline.ReelSettings(
            mode=payload.get("mode", "artifact-comes-alive"),
            protagonist=payload.get("protagonist", "curator"),
            protagonist_name=payload.get("protagonist_name", "Cat the Curator"),
            language=payload.get("language", "th"),
            tone=payload.get("tone", "funny"),
            shots=max(3, min(int(payload.get("shots", 6)), 8)),
            seconds_per_shot=max(3, min(int(payload.get("seconds", 5)), 8)),
            ending=payload.get("ending", "funny twist"),
            narrate=bool(payload.get("narrate", True)),
            voice=voice,
        )

        reference = None
        name = payload.get("reference")
        if name:
            candidate = (ARTIFACTS / "uploads" / Path(name).name).resolve()
            if candidate.exists():
                reference = candidate

        run_id = new_run()
        threading.Thread(
            target=execute,
            args=(
                run_id,
                url,
                settings,
                payload.get("concept_id"),
                reference,
                payload.get("quality", "medium"),
            ),
            daemon=True,
        ).start()
        self._json({"run_id": run_id})


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    providers = llm.available_providers()
    key = "openai" if providers["openai"] else "MISSING OPENAI_API_KEY"
    print("Meowseum Reel Studio")
    print(f"  text          : {llm.OPENAI_TEXT_MODEL} ({key})")
    print(f"  images        : {llm.OPENAI_IMAGE_MODEL} at {llm.OPENAI_IMAGE_SIZE} ({key})")
    print(f"  narration     : {llm.OPENAI_TTS_MODEL} ({key})")
    if not providers["openai"]:
        print("                  no key — the player falls back to browser speech")
    rates = llm._text_rates()
    if rates["input"] is None or rates["output"] is None:
        print(
            "  text pricing  : UNSET — runs report tokens but no text $; set "
            "OPENAI_TEXT_PRICE_INPUT / _OUTPUT in .env"
        )
    caps = export.capability()
    print(
        "  mp4 export    : "
        + (f"{caps.video_encoder} via {caps.binary}" if caps.available else caps.reason)
    )
    print(f"  open          : http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
