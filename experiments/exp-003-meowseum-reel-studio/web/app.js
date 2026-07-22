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
};

/* ---------------------------------------------------------------- sources */

async function boot() {
  try {
    const health = await (await fetch("/api/health")).json();
    const text = health.providers.anthropic ? "Anthropic" : "OpenAI";
    $("provider").textContent =
      `text: ${text} (${health.text_model}) · images: ${health.image_model}`;
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
  $("cost-hint").textContent =
    `≈ $${images} of images plus about $0.01 of text — ${shots} shots at ${quality} quality.`;
}
["shots", "quality"].forEach((id) => ($(id).onchange = updateCostHint));

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

  $("audit").innerHTML = audit.clean
    ? `<div class="audit-line audit-ok">
         Audit clean — ${audit.shots} shots, every one declaring a source basis
         or an explicit invention, no price, stock, shipping, weight or size
         claim anywhere. Cost this run: <strong>$${cost.total_usd}</strong>
         (${cost.text_calls} text calls, ${cost.images} images).
       </div>`
    : `<div class="audit-line audit-bad">
         ${audit.problems.length} problem(s) survived the critic:
         <ul>${audit.problems
           .map((p) => `<li>shot ${esc(p.shot)} — ${esc(p.kind)}: ${esc(p.detail)}</li>`)
           .join("")}</ul>
         Cost this run: $${cost.total_usd}.
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
      return `<div class="shot">
        <div>${image}</div>
        <div>
          <h3>Shot ${esc(shot.shot_number)} · ${esc(shot.duration_seconds)}s</h3>
          <p class="narration">${esc(shot.narration || "")}</p>
          <div>${basis}${invented}</div>
          <p class="prompt">${esc(shot.image_prompt || "")}</p>
        </div>
      </div>`;
    })
    .join("");

  $("panel-review").classList.remove("is-hidden");
  $("panel-review").scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ----------------------------------------------------------------- player */

let timer = null;

$("play").onclick = () => playReel();
$("close-player").onclick = () => stopReel();
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") stopReel();
});

function thaiVoice() {
  const voices = speechSynthesis.getVoices();
  return voices.find((v) => v.lang && v.lang.toLowerCase().startsWith("th")) || null;
}

function playReel() {
  const manifest = state.manifest;
  if (!manifest) return;
  const shots = manifest.shots;
  const wantsThai = manifest.settings.language === "th";
  const voice = wantsThai ? thaiVoice() : null;
  // No Thai voice installed is a real, common case. Falling back to captions
  // beats speaking Thai text in an English voice, which is unintelligible.
  const speak = !wantsThai || Boolean(voice);

  $("player").classList.remove("is-hidden");
  let index = 0;

  const show = () => {
    if (index >= shots.length) return stopReel();
    const shot = shots[index];
    const image = $("reel-img");
    image.src = shot.image_file ? `${manifest.image_base}/${shot.image_file}` : "";
    image.style.visibility = shot.image_file ? "visible" : "hidden";
    $("reel-caption").textContent = shot.narration || shot.caption || "";

    const ms = (shot.duration_seconds || 5) * 1000;
    const bar = $("reel-progress");
    bar.style.transition = "none";
    bar.style.width = "0%";
    requestAnimationFrame(() => {
      bar.style.transition = `width ${ms}ms linear`;
      bar.style.width = "100%";
    });

    if (speak && shot.narration) {
      const utterance = new SpeechSynthesisUtterance(shot.narration);
      if (voice) utterance.voice = voice;
      utterance.lang = wantsThai ? "th-TH" : "en-US";
      utterance.rate = 0.98;
      speechSynthesis.cancel();
      speechSynthesis.speak(utterance);
    }

    index += 1;
    timer = setTimeout(show, ms);
  };
  show();
}

function stopReel() {
  clearTimeout(timer);
  speechSynthesis.cancel();
  $("player").classList.add("is-hidden");
}

speechSynthesis.onvoiceschanged = () => {};
boot();
