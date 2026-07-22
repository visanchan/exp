/* Meowseum Reel Studio — front end.
 *
 * Plain DOM, no framework. Three jobs: pick a source, watch the agents work
 * over SSE, and play the result as a 9:16 slideshow with spoken narration.
 */

const $ = (id) => document.getElementById(id);

const state = {
  sources: [],
  type: "product",
  selected: null,
  reference: null,
  manifest: null,
  runId: null,
  canExport: false,
};

/* ---------------------------------------------------------------- sources */

async function boot() {
  try {
    const health = await (await fetch("/api/health")).json();
    $("provider").textContent =
      `text: ${health.text_model} · images: ${health.image_model}` +
      ` · voice: ${health.speech_model}`;
    // Export needs an ffmpeg on this machine. Say so up front rather than
    // failing after the Reel is generated.
    state.canExport = Boolean(health.export && health.export.available);
    state.exportReason = (health.export && health.export.reason) || "";
  } catch {
    $("provider").textContent = "provider check failed";
  }

  state.sources = await (await fetch("/api/sources")).json();
  renderSources();
}

function renderSources() {
  const grid = $("source-grid");
  const list = state.sources.filter((s) => s.type === state.type);
  if (!list.length) {
    grid.innerHTML = `<p class="muted">No snapshots of this type.</p>`;
    return;
  }
  grid.innerHTML = "";
  for (const source of list) {
    const card = document.createElement("button");
    card.className = "card" + (state.selected === source.url ? " is-on" : "");
    card.innerHTML = `
      ${source.image ? `<img src="${source.image}" alt="" loading="lazy">` : ""}
      <div class="body">
        <div class="t"></div>
        <div class="th"></div>
        <div class="meta"></div>
      </div>`;
    card.querySelector(".t").textContent = source.title;
    card.querySelector(".th").textContent = source.thai_title || "";
    card.querySelector(".meta").textContent = source.room || source.category || source.type;
    card.onclick = () => selectSource(source.url);
    grid.appendChild(card);
  }
}

$("source-tabs").onclick = (event) => {
  const tab = event.target.closest(".tab");
  if (!tab) return;
  state.type = tab.dataset.type;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("is-on", t === tab));
  renderSources();
};

/* ------------------------------------------------------------- extraction */

async function selectSource(url) {
  state.selected = url;
  renderSources();

  const record = await (await fetch(`/api/source?url=${encodeURIComponent(url)}`)).json();
  if (record.error) {
    $("extract-body").innerHTML = `<p class="audit-line audit-bad">${record.error}</p>`;
    $("panel-extract").classList.remove("is-hidden");
    return;
  }

  const rows = [];
  const add = (label, en, th) => {
    if (!en && !th) return;
    rows.push(`<div class="kv"><dt>${label}</dt><dd>${esc(en || "")}${
      th ? `<div class="th">${esc(th)}</div>` : ""
    }</dd></div>`);
  };

  add("Title", record.title, record.thai_title);
  add("Summary", record.summary?.en, record.summary?.th);
  for (const [key, value] of Object.entries(record.fields || {})) {
    if (key === "sections" || key === "tags") continue;
    if (value && typeof value === "object" && ("en" in value || "th" in value)) {
      add(key.replace(/_/g, " "), value.en, value.th);
    } else if (typeof value === "string") {
      add(key.replace(/_/g, " "), value, "");
    }
  }
  const sections = record.fields?.sections;
  if (Array.isArray(sections)) {
    add("Sections", sections.map((s) => s.heading).join(" · "), "");
  }

  const withheld = record.transactional?.withheld_fields || 0;
  $("extract-body").innerHTML = `
    <dl style="margin:0">${rows.join("")}</dl>
    <div class="quarantine">
      <strong>${withheld} commercial field${withheld === 1 ? "" : "s"} withheld</strong>
      — price, stock, shipping, weight and dimensions were extracted but are not
      passed to any story agent, because this page is marked
      <em>${record.verified_for_marketing ? "verified" : "pending owner confirmation"}</em>.
      The agents cannot narrate what they were never shown.
    </div>`;

  $("panel-extract").classList.remove("is-hidden");
  $("panel-settings").classList.remove("is-hidden");
  updateCostHint();
  $("panel-extract").scrollIntoView({ behavior: "smooth", block: "start" });
}

const esc = (s) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* --------------------------------------------------------------- settings */

$("protagonist").onchange = (event) => {
  $("upload-box").classList.toggle("is-hidden", event.target.value !== "my-cat");
};

$("cat-photo").onchange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  $("upload-state").textContent = "uploading…";
  const response = await fetch("/api/upload", { method: "POST", body: file });
  const data = await response.json();
  if (data.error) {
    $("upload-state").textContent = `upload failed: ${data.error}`;
    return;
  }
  state.reference = data.reference;
  $("upload-state").textContent =
    `stored as ${data.reference} (${Math.round(data.bytes / 1024)} KB) — used as the reference for every shot`;
};

const IMAGE_PRICE = { low: 0.011, medium: 0.042, high: 0.167 };

function updateCostHint() {
  const shots = Number($("shots").value);
  const quality = $("quality").value;
  const images = (shots * IMAGE_PRICE[quality]).toFixed(2);
  const spoken = $("voice").value ? " and roughly $0.01 of narration" : "";
  $("cost-hint").textContent =
    `≈ $${images} of images plus about $0.01 of text${spoken} — ` +
    `${shots} shots at ${quality} quality.`;
}
["shots", "quality", "voice"].forEach((id) => ($(id).onchange = updateCostHint));

/* ------------------------------------------------------------- generation */

$("generate").onclick = async () => {
  if (!state.selected) return;
  const button = $("generate");
  button.disabled = true;
  $("terminal").innerHTML = "";
  $("panel-progress").classList.remove("is-hidden");
  $("panel-review").classList.add("is-hidden");
  $("panel-progress").scrollIntoView({ behavior: "smooth", block: "start" });

  const body = {
    url: state.selected,
    protagonist: $("protagonist").value,
    protagonist_name: $("protagonist").value === "my-cat" ? "your cat" : "Cat the Curator",
    concept_id: $("concept").value,
    language: $("language").value,
    shots: Number($("shots").value),
    seconds: Number($("seconds").value),
    quality: $("quality").value,
    // Empty voice = keep the old browser-speech path for this run.
    voice: $("voice").value || "alloy",
    narrate: Boolean($("voice").value),
    reference: $("protagonist").value === "my-cat" ? state.reference : null,
  };

  const response = await fetch("/api/reel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (data.error) {
    log("error", data.error);
    button.disabled = false;
    return;
  }
  listen(data.run_id, button);
};

function log(stage, message) {
  const line = document.createElement("div");
  const cls = stage === "error" ? "err" : stage === "done" ? "ok" : "stage";
  line.innerHTML = `<span class="${cls}">${esc(stage.padEnd(14))}</span> ${esc(message)}`;
  $("terminal").appendChild(line);
  $("terminal").scrollTop = $("terminal").scrollHeight;
}

function listen(runId, button) {
  const stream = new EventSource(`/api/stream/${runId}`);
  stream.onmessage = async (event) => {
    const { stage, message } = JSON.parse(event.data);
    log(stage, message);
    if (stage === "done") {
      stream.close();
      button.disabled = false;
      const result = await (await fetch(`/api/run/${runId}`)).json();
      state.runId = runId;
      showReview(result.manifest);
    }
    if (stage === "error") {
      stream.close();
      button.disabled = false;
    }
  };
  stream.onerror = () => {
    stream.close();
    button.disabled = false;
  };
}

/* ----------------------------------------------------------------- review */

function showReview(manifest) {
  state.manifest = manifest;
  const audit = manifest.audit_after_critic;
  const cost = manifest.cost;

  // When the text model has no configured price the total covers images and
  // narration only — say so rather than showing a short number as the bill.
  const costLabel = cost.total_is_complete
    ? `<strong>$${cost.total_usd}</strong>`
    : `<strong>$${cost.total_usd}+</strong> (images and narration only —
       ${cost.input_tokens + cost.output_tokens} text tokens are unpriced)`;

  $("audit").innerHTML = audit.clean
    ? `<div class="audit-line audit-ok">
         Audit clean — ${audit.shots} shots, every one declaring a source basis
         or an explicit invention, no price, stock, shipping, weight or size
         claim anywhere. Cost this run: ${costLabel}
         (${cost.text_calls} text calls, ${cost.images} images).
       </div>`
    : `<div class="audit-line audit-bad">
         ${audit.problems.length} problem(s) survived the critic:
         <ul>${audit.problems
           .map((p) => `<li>shot ${esc(p.shot)} — ${esc(p.kind)}: ${esc(p.detail)}</li>`)
           .join("")}</ul>
         Cost this run: ${costLabel}.
       </div>`;

  const base = manifest.image_base;
  $("shots").innerHTML = manifest.shots
    .map((shot) => {
      const image = shot.image_file
        ? `<img src="${base}/${shot.image_file}" alt="">`
        : `<div class="no-img">no image<br>${esc((shot.image_error || "").slice(0, 80))}</div>`;
      const basis = (shot.source_basis || [])
        .map((b) => `<span class="tag tag-src">${esc(b)}</span>`)
        .join("");
      const invented = shot.creative_addition
        ? `<span class="tag tag-new">invented: ${esc(shot.creative_addition)}</span>`
        : "";
      // The narration MP3 is an artifact like the image: audible here without
      // replaying the whole Reel.
      const audio = shot.audio_file
        ? `<audio controls preload="none" src="${base}/${shot.audio_file}"></audio>`
        : shot.audio_error
        ? `<p class="muted">narration failed: ${esc(shot.audio_error.slice(0, 80))}</p>`
        : "";
      return `<div class="shot">
        <div>${image}</div>
        <div>
          <h3>Shot ${esc(shot.shot_number)} · ${esc(shot.duration_seconds)}s</h3>
          <p class="narration">${esc(shot.narration || "")}</p>
          ${audio}
          <div>${basis}${invented}</div>
          <p class="prompt">${esc(shot.image_prompt || "")}</p>
        </div>
      </div>`;
    })
    .join("");

  $("export").disabled = !state.canExport;
  $("export-state").textContent = state.canExport
    ? ""
    : `MP4 export unavailable — ${state.exportReason}`;

  $("panel-review").classList.remove("is-hidden");
  $("panel-review").scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ----------------------------------------------------------------- export */

$("export").onclick = async () => {
  if (!state.runId) return;
  const button = $("export");
  button.disabled = true;
  $("export-state").textContent = "encoding — a few seconds…";

  try {
    const response = await fetch(`/api/export/${state.runId}`, { method: "POST" });
    const report = await response.json();
    if (report.error) {
      $("export-state").textContent = `export failed: ${report.error}`;
      button.disabled = false;
      return;
    }
    const mb = (report.bytes / 1048576).toFixed(1);
    // A shot dropped for want of an image shortens the Reel — say so rather
    // than handing over a quietly incomplete file.
    const dropped = report.shots_skipped.length
      ? ` ${report.shots_skipped.length} shot(s) left out: ` +
        report.shots_skipped.map((s) => `#${s.shot} (${s.why})`).join(", ") + "."
      : "";
    const silent = report.silent_shots
      ? ` ${report.silent_shots} shot(s) silent.`
      : "";
    $("export-state").innerHTML =
      `<a href="${report.url}" download>Download reel.mp4</a> — ` +
      `${report.shots_encoded} shots, ${report.resolution}, ${mb} MB, ` +
      `${report.video_encoder}, encoded in ${report.seconds_to_encode}s.` +
      esc(dropped + silent);
  } catch (error) {
    $("export-state").textContent = `export failed: ${error}`;
  }
  button.disabled = false;
};

/* ----------------------------------------------------------------- player */

let timer = null;
const narrator = new Audio();
narrator.preload = "auto";

$("play").onclick = () => playReel();
$("close-player").onclick = () => stopReel();
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") stopReel();
});

function thaiVoice() {
  const voices = speechSynthesis.getVoices();
  return voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("th")) || null;
}

function runBar(ms) {
  const bar = $("reel-progress");
  bar.style.transition = "none";
  bar.style.width = "0%";
  requestAnimationFrame(() => {
    bar.style.transition = `width ${ms}ms linear`;
    bar.style.width = "100%";
  });
}

function playReel() {
  const manifest = state.manifest;
  if (!manifest) return;
  const shots = manifest.shots;
  const wantsThai = manifest.settings.language === "th";
  const osVoice = wantsThai ? thaiVoice() : null;
  // Generated MP3s are the normal path. speechSynthesis is only reached when a
  // shot has no audio file — narration switched off, or the call failed — and
  // it can speak Thai only if the OS happens to have a Thai voice installed.
  const speak = !wantsThai || Boolean(osVoice);

  $("player").classList.remove("is-hidden");
  let index = 0;

  const show = () => {
    if (index >= shots.length) return stopReel();
    const shot = shots[index];
    index += 1;

    const image = $("reel-img");
    image.src = shot.image_file ? `${manifest.image_base}/${shot.image_file}` : "";
    image.style.visibility = shot.image_file ? "visible" : "hidden";
    $("reel-caption").textContent = shot.narration || shot.caption || "";

    const planned = (shot.duration_seconds || 5) * 1000;
    let started = Date.now();
    const hold = (ms) => {
      clearTimeout(timer);
      runBar(ms);
      started = Date.now();
      timer = setTimeout(show, ms);
    };

    speechSynthesis.cancel();
    narrator.pause();
    narrator.onloadedmetadata = null;

    if (shot.audio_file) {
      narrator.onloadedmetadata = () => {
        // A shot holds for at least its planned duration, and longer when the
        // spoken line runs over — otherwise narration is cut mid-sentence.
        if (!isFinite(narrator.duration)) return;
        const needed = narrator.duration * 1000 + 400;
        if (needed > planned) hold(needed - (Date.now() - started));
      };
      narrator.src = `${manifest.image_base}/${shot.audio_file}`;
      narrator.currentTime = 0;
      narrator.play().catch(() => {});
    } else if (speak && shot.narration) {
      const utterance = new SpeechSynthesisUtterance(shot.narration);
      if (osVoice) utterance.voice = osVoice;
      utterance.lang = wantsThai ? "th-TH" : "en-US";
      utterance.rate = 0.98;
      speechSynthesis.speak(utterance);
    }

    hold(planned);
  };
  show();
}

function stopReel() {
  clearTimeout(timer);
  speechSynthesis.cancel();
  narrator.onloadedmetadata = null;
  narrator.pause();
  $("player").classList.add("is-hidden");
}

speechSynthesis.onvoiceschanged = () => {};
boot();
