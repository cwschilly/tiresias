/* js/tool.js — page orchestration for the step flow:
   rate -> alpha/beta -> scatter -> fit -> Odyssey sliders. */

import { starsString, prophecy, oscarCounts, oscarLine } from "./model.js";
import { fitUser, predictAt } from "./personalize.js";
import { predictFromFit } from "./curveFit.js";
import { alphaLine, fitShapeLine } from "./wit.js";
import { renderChart } from "./chart.js";
import { createSteps } from "./steps.js";
import { createStarRow } from "./stars.js";
import { computeOptimal, renderCard, cardBlob, canNativeShare, canCopyImage,
         nativeShare, copyImage, downloadImage } from "./share.js";

const STEP = { RATE: 0, ALPHA: 1, SCATTER: 2, FIT: 3, ODYSSEY: 4 };
const DEGREE_NAME = { 1: "linear", 2: "quadratic", 3: "cubic" };

const ratings = {};
let pipeline = null;
let filmsByKey = {};
let personal = null;   // {fit, alpha, films, metricValues} from personalize.js
let steps = null;

init().catch(showLoadError);

async function init() {
  pipeline = await fetch("model/pipeline.json").then((r) => {
    if (!r.ok) throw new Error(`pipeline.json: HTTP ${r.status}`);
    return r.json();
  });
  filmsByKey = Object.fromEntries(pipeline.films.map((f) => [f.key, f]));

  buildFilmCards();
  buildSliders();

  steps = createSteps(document.getElementById("steps"), { onEnter });
  steps.setGate(STEP.RATE, () => Object.keys(ratings).length >= pipeline.min_ratings);

  document.getElementById("askBtn").addEventListener("click", () => steps.next());
  document.getElementById("startOverBtn").addEventListener("click", () => steps.go(STEP.RATE));
  for (const btn of document.querySelectorAll("[data-nav]")) {
    btn.addEventListener("click", () => steps[btn.dataset.nav]());
  }
  initShare();
  refreshGate();
}

function showLoadError(err) {
  console.error("Failed to load pipeline.json:", err);
  const banner = document.getElementById("loadError");
  banner.style.display = "block";
  banner.textContent =
    "Tiresias cannot see: the pipeline failed to load. Refresh the page, or accept that some prophecies are not meant for you.";
}

/* ── Step transitions ── */
function onEnter(step) {
  if (step === STEP.ALPHA) refit();
  else if (step === STEP.SCATTER) renderScatter(false);
  else if (step === STEP.FIT) renderScatter(true);
  else if (step === STEP.ODYSSEY) updateOdyssey();
}

function refit() {
  personal = fitUser(ratings, filmsByKey);
  const alpha = personal.alpha, beta = 1 - alpha;
  document.getElementById("alphaValue").textContent = alpha.toFixed(2);
  document.getElementById("betaValue").textContent = beta.toFixed(2);
  document.getElementById("alphaBarFill").style.width = `${(alpha * 100).toFixed(0)}%`;
  document.getElementById("alphaWit").textContent = alphaLine(alpha);
}

function chartPoints() {
  return personal.films.map((key, i) => ({
    x: personal.metricValues[i],
    y: ratings[key],
    label: filmsByKey[key].label.replace(/\s*\(\d{4}\)/, ""),
  }));
}

function renderScatter(withFit) {
  if (!personal) refit();
  const svg = document.getElementById(withFit ? "fitChart" : "scatterChart");
  renderChart(svg, chartPoints(), withFit ? (x) => predictFromFit(personal.fit, x) : null);

  if (withFit) {
    const fit = personal.fit;
    document.getElementById("fitSummary").innerHTML =
      `A <strong>${DEGREE_NAME[fit.degree]}</strong> fit, ` +
      `R² = <strong>${fit.r2InSample.toFixed(2)}</strong>.`;
    document.getElementById("fitWit").textContent = fitShapeLine(fit);
  }
}

/* ── Step 1: film cards ── */
function buildFilmCards() {
  const grid = document.getElementById("filmGrid");
  for (const film of pipeline.films) {
    const card = document.createElement("div");
    card.className = "film-card";
    card.innerHTML = `<label>${film.label}</label>`;
    grid.appendChild(card);

    const widget = createStarRow(card, {
      onChange: (value) => setRating(film.key, value, card, display),
    });

    const clr = document.createElement("button");
    clr.className = "unseen-btn";
    clr.textContent = "clear";
    clr.addEventListener("click", widget.clear);
    card.querySelector(".star-row").appendChild(clr);

    const display = document.createElement("div");
    display.className = "rating-display";
    display.textContent = "not rated";
    card.appendChild(display);
  }
}

function setRating(key, value, card, display) {
  if (value == null) delete ratings[key];
  else ratings[key] = value;
  card.classList.toggle("rated", value != null);
  display.textContent = value != null ? `${value.toFixed(1)} / 5.0` : "not rated";
  personal = null;   // stale — recomputed on next step entry
  refreshGate();
}

function refreshGate() {
  const n = Object.keys(ratings).length;
  const remaining = Math.max(0, pipeline.min_ratings - n);
  document.getElementById("remaining").textContent = remaining;
  document.getElementById("askBtn").disabled = n < pipeline.min_ratings;
  document.getElementById("minNotice").style.display = remaining > 0 ? "block" : "none";
}

/* ── Step 5: Odyssey sliders ── */
function buildSliders() {
  const fabula = document.getElementById("fabulaSlider");
  const syuzhet = document.getElementById("syuzhetSlider");
  fabula.value = pipeline.odyssey.fabula;
  syuzhet.value = pipeline.odyssey.syuzhet;
  fabula.addEventListener("input", updateOdyssey);
  syuzhet.addEventListener("input", updateOdyssey);
}

function updateOdyssey() {
  if (!personal) refit();
  const fabula = parseFloat(document.getElementById("fabulaSlider").value);
  const syuzhet = parseFloat(document.getElementById("syuzhetSlider").value);
  document.getElementById("fabulaValue").textContent = fabula.toFixed(1);
  document.getElementById("syuzhetValue").textContent = syuzhet.toFixed(1);

  const rating = predictAt(personal, fabula, syuzhet);
  document.getElementById("bigRating").textContent = rating.toFixed(1);
  document.getElementById("starsDisplay").textContent = starsString(rating);

  document.getElementById("prophecy").innerHTML =
    prophecy(rating).map((l) => `<p>${l}</p>`).join("");

  const counts = oscarCounts(pipeline.oscars.coeffs, fabula, syuzhet);
  document.getElementById("oscarProphecy").textContent = `And the Academy? ${oscarLine(counts)}`;
}

/* ── Share card ── */
let shareBlob = null;
let previewUrl = null;

function initShare() {
  document.getElementById("shareBtn").addEventListener("click", openShare);
  for (const el of document.querySelectorAll("[data-share-close]")) {
    el.addEventListener("click", closeShare);
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeShare();
  });

  document.getElementById("shareNativeBtn").addEventListener("click", () =>
    nativeShare(shareBlob).catch(() => {}));   // user cancelling the sheet is not an error
  document.getElementById("shareCopyBtn").addEventListener("click", async () => {
    try {
      await copyImage(shareBlob);
      setShareStatus("Copied.");
    } catch {
      setShareStatus(`Copy failed. ${saveHint()}`);
    }
  });
  document.getElementById("shareDownloadBtn").addEventListener("click", () =>
    downloadImage(shareBlob));
}

async function openShare() {
  if (!personal) refit();
  const optimal = computeOptimal(personal);
  const counts = oscarCounts(pipeline.oscars.coeffs, optimal.fabula, optimal.syuzhet);

  const canvas = document.createElement("canvas");
  renderCard(canvas, { alpha: personal.alpha, optimal, personal,
                       noms: counts.noms, wins: counts.wins });
  shareBlob = await cardBlob(canvas);

  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(shareBlob);
  document.getElementById("sharePreview").src = previewUrl;

  // The native sheet (mobile) already offers Save to Photos / Messages /
  // socials, so the raw Download is redundant — and on iOS it confusingly
  // lands in Files. Offer it only when native share is unavailable.
  // Desktop counts as unavailable: macOS drafts the share in Messages
  // without ever bringing the app forward, so copy/download serve better.
  const nativeOk = canNativeShare(shareBlob) &&
                   window.matchMedia("(pointer: coarse)").matches;
  document.getElementById("shareNativeBtn").hidden = !nativeOk;
  document.getElementById("shareCopyBtn").hidden = !canCopyImage();
  document.getElementById("shareDownloadBtn").hidden = nativeOk;
  setShareStatus(saveHint());
  document.getElementById("shareModal").hidden = false;
}

function saveHint() {
  // Long-press (touch) / right-click (mouse) on the image opens the
  // system menu — works even where the share/clipboard APIs don't
  return window.matchMedia("(pointer: coarse)").matches
    ? "Tip: press and hold the image to save or share it."
    : "Tip: right-click the image to copy or save it.";
}

function closeShare() {
  document.getElementById("shareModal").hidden = true;
}

function setShareStatus(message) {
  document.getElementById("shareStatus").textContent = message;
}
