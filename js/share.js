/* js/share.js — the shareable Wrapped-style results card.
   computeOptimal is pure math (tested); the rest draws to a canvas and
   hands PNGs to whichever share primitives this browser supports. */

import { predictAt } from "./personalize.js";
import { predictFromFit } from "./curveFit.js";
import { starsString } from "./model.js";

/* Palette — mirrors css/theme.css + src/plotting/style.py */
const CREAM = "#f7f4ec";
const GREEN_DARK = "#1d6d47";
const GREEN_MID = "#2a8f5e";
const GREEN_LIGHT = "#89dd9d";
const RUST = "#c4694d";
const RUST_DARK = "#a3502e";
const GOLD = "#d4a017";
const INK = "#1a1a1a";
const MUTED = "#8a8578";

export const SITE_URL = "willtheodysseybegood.com";

/**
 * The (fabula, syuzhet) in [0, max]² that maximizes the person's predicted
 * rating. The rating depends only on the aggregated metric, so a whole arc
 * of points is (near-)optimal; among everything within an imperceptible
 * 0.02 stars of the maximum, ties resolve to the most balanced point
 * (min |fabula − syuzhet|, then least extreme) so the card reads naturally.
 */
export function computeOptimal(personal, step = 0.1, max = 10) {
  const TOL = 0.02;
  const n = Math.round(max / step);
  const at = (i, j) => predictAt(personal, i * step, j * step);

  let maxRating = -Infinity;
  for (let i = 0; i <= n; i++) {
    for (let j = 0; j <= n; j++) maxRating = Math.max(maxRating, at(i, j));
  }

  let best = null;
  for (let i = 0; i <= n; i++) {
    for (let j = 0; j <= n; j++) {
      const rating = at(i, j);
      if (rating < maxRating - TOL) continue;
      const fabula = i * step, syuzhet = j * step;
      const diff = Math.abs(fabula - syuzhet), sum = fabula + syuzhet;
      if (!best || diff < best.diff - 1e-9 ||
          (diff < best.diff + 1e-9 && (rating > best.rating + 1e-9 ||
            (rating > best.rating - 1e-9 && sum < best.sum - 1e-9)))) {
        best = { fabula, syuzhet, rating, diff, sum };
      }
    }
  }
  return { fabula: best.fabula, syuzhet: best.syuzhet, rating: best.rating };
}

/* ── Card rendering ── */

const W = 1080, H = 1920;

function text(ctx, str, x, y, { size, color = INK, weight = "", style = "",
                                align = "center", spacing = "0px" } = {}) {
  ctx.font = `${style} ${weight} ${size}px Georgia, serif`.trim();
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.letterSpacing = spacing;
  ctx.fillText(str, x, y);
  ctx.letterSpacing = "0px";
}

function drawCurve(ctx, personal, optimal, box) {
  const metric = (f, s) => Math.sqrt(2 * personal.alpha * f ** 2 + 2 * (1 - personal.alpha) * s ** 2);
  const optMetric = metric(optimal.fabula, optimal.syuzhet);
  const lo = Math.min(...personal.metricValues, optMetric) - 1;
  const hi = Math.max(...personal.metricValues, optMetric) + 1;

  const samples = Array.from({ length: 121 }, (_, i) => {
    const m = lo + (i / 120) * (hi - lo);
    return { m, r: predictFromFit(personal.fit, m) };
  });
  // Fill the box vertically: scale y to the curve's own range, not 0.5-5
  const rLo = Math.min(...samples.map((s) => s.r)) - 0.2;
  const rHi = Math.max(...samples.map((s) => s.r)) + 0.2;

  const px = (m) => box.x + ((m - lo) / (hi - lo)) * box.w;
  const py = (r) => box.y + box.h - ((r - rLo) / (rHi - rLo)) * box.h;

  const path = () => {
    ctx.beginPath();
    samples.forEach((s, i) => i ? ctx.lineTo(px(s.m), py(s.r)) : ctx.moveTo(px(s.m), py(s.r)));
  };
  ctx.lineCap = "round";
  path(); ctx.strokeStyle = "rgba(196,105,77,0.18)"; ctx.lineWidth = 22; ctx.stroke();
  path(); ctx.strokeStyle = RUST; ctx.lineWidth = 7; ctx.stroke();

  // Gold dot at the optimum
  ctx.beginPath();
  ctx.arc(px(optMetric), py(optimal.rating), 17, 0, Math.PI * 2);
  ctx.fillStyle = GOLD;
  ctx.fill();
  ctx.lineWidth = 5;
  ctx.strokeStyle = "#8a6a0e";
  ctx.stroke();
}

/**
 * Draws the full 1080×1920 story card.
 * data: {alpha, optimal: {fabula, syuzhet, rating}, noms, wins, personal}
 */
export function renderCard(canvas, { alpha, optimal, noms, wins, personal }) {
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = CREAM;
  ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = GREEN_DARK;
  ctx.lineWidth = 6;
  ctx.strokeRect(36, 36, W - 72, H - 72);

  text(ctx, "TIRESIAS", W / 2, 210, { size: 108, weight: "bold", spacing: "14px" });
  text(ctx, "has seen your fate", W / 2, 280, { size: 40, style: "italic", color: GREEN_DARK });

  /* α / β */
  text(ctx, alpha.toFixed(2), W / 2 - 170, 480, { size: 120, weight: "bold", color: RUST });
  text(ctx, "α · fabula", W / 2 - 170, 540, { size: 34, style: "italic", color: MUTED });
  text(ctx, (1 - alpha).toFixed(2), W / 2 + 170, 480, { size: 120, weight: "bold", color: GREEN_MID });
  text(ctx, "β · syuzhet", W / 2 + 170, 540, { size: 34, style: "italic", color: MUTED });

  /* Their curve */
  drawCurve(ctx, personal, optimal, { x: 150, y: 620, w: W - 300, h: 320 });
  text(ctx, "your nolan curve", W / 2, 990, { size: 30, style: "italic", color: GREEN_DARK });

  /* Peak Nolan */
  text(ctx, "Your perfect Odyssey", W / 2, 1120, { size: 52, weight: "bold", color: GREEN_DARK });
  text(ctx, `fabula ${optimal.fabula.toFixed(1)}   ·   syuzhet ${optimal.syuzhet.toFixed(1)}`,
       W / 2, 1195, { size: 44, color: INK });

  text(ctx, optimal.rating.toFixed(1), W / 2, 1360, { size: 150, weight: "bold", color: RUST });
  text(ctx, starsString(optimal.rating), W / 2, 1440, { size: 64, color: GREEN_LIGHT });

  /* Oscars */
  text(ctx, "and the Academy shall bestow", W / 2, 1560, { size: 36, style: "italic", color: MUTED });
  text(ctx, `${noms.toFixed(1)} nominations  ·  ${wins.toFixed(1)} wins`,
       W / 2, 1630, { size: 48, weight: "bold", color: "#8a6a0e" });

  /* Footer */
  text(ctx, "will you like The Odyssey (2026)?", W / 2, 1770, { size: 34, style: "italic", color: GREEN_DARK });
  text(ctx, SITE_URL, W / 2, 1826, { size: 40, weight: "bold", color: RUST_DARK });
}

/* ── Export & share primitives ── */

export function cardBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error("toBlob failed")), "image/png");
  });
}

export function cardFile(blob) {
  return new File([blob], "tiresias-prophecy.png", { type: "image/png" });
}

export function canNativeShare(blob) {
  return typeof navigator.canShare === "function" &&
         navigator.canShare({ files: [cardFile(blob)] });
}

export function canCopyImage() {
  return typeof ClipboardItem !== "undefined" && !!navigator.clipboard?.write;
}

export function nativeShare(blob) {
  return navigator.share({
    files: [cardFile(blob)],
    title: "My Tiresias prophecy",
    text: `Tiresias has foreseen my Odyssey rating — ${SITE_URL}`,
  });
}

export function copyImage(blob) {
  return navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
}

export function downloadImage(blob) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "tiresias-prophecy.png";
  a.click();
  URL.revokeObjectURL(a.href);
}
