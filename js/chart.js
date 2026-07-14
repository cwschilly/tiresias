/* js/chart.js — responsive SVG scatter of ratings vs. personal wackiness,
   with an optional fit curve. Pure rendering; all math arrives as data. */

const NS = "http://www.w3.org/2000/svg";
const W = 520, H = 360;
const M = { left: 44, right: 16, top: 16, bottom: 44 };

const el = (tag, attrs = {}) => {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  return node;
};

/**
 * Renders into `svg` (cleared first).
 * points: [{x, y, label}]; fitFn: metric -> rating, drawn when provided.
 */
export function renderChart(svg, points, fitFn = null) {
  svg.innerHTML = "";
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);

  const xs = points.map((p) => p.x);
  const pad = (Math.max(...xs) - Math.min(...xs)) * 0.12 || 1;
  const xLo = Math.min(...xs) - pad, xHi = Math.max(...xs) + pad;

  const px = (x) => M.left + ((x - xLo) / (xHi - xLo)) * (W - M.left - M.right);
  const py = (y) => H - M.bottom - ((y - 0.25) / (5.25 - 0.25)) * (H - M.top - M.bottom);

  drawAxes(svg, px, py, xLo, xHi);

  if (fitFn) {
    const steps = 120;
    const d = Array.from({ length: steps + 1 }, (_, i) => {
      const x = xLo + (i / steps) * (xHi - xLo);
      return `${i ? "L" : "M"} ${px(x).toFixed(1)} ${py(fitFn(x)).toFixed(1)}`;
    }).join(" ");
    svg.appendChild(el("path", { d, class: "chart-fit-glow-lg" }));
    svg.appendChild(el("path", { d, class: "chart-fit-glow-md" }));
    svg.appendChild(el("path", { d, class: "chart-fit-glow-sm" }));
    svg.appendChild(el("path", { d, class: "chart-fit" }));
  }

  const placed = [];   // {x, y} of already-placed labels, for collision dodging
  for (const p of points) {
    svg.appendChild(el("circle", { cx: px(p.x), cy: py(p.y), r: 11, class: "chart-dot-ring" }));
    svg.appendChild(el("circle", { cx: px(p.x), cy: py(p.y), r: 4.5, class: "chart-dot-centre" }));
    if (!p.label) continue;

    const left = px(p.x) > W - M.right - 80;
    let lx = px(p.x) + (left ? -10 : 10);
    let ly = py(p.y) - 8;
    // If another label sits close by, drop this one below its dot instead
    if (placed.some((q) => Math.abs(q.y - ly) < 14 && Math.abs(q.x - lx) < 110)) {
      ly = py(p.y) + 18;
    }
    placed.push({ x: lx, y: ly });

    const text = el("text", {
      x: lx, y: ly, class: "chart-label", "text-anchor": left ? "end" : "start",
    });
    text.textContent = p.label;
    svg.appendChild(text);
  }
}

function drawAxes(svg, px, py, xLo, xHi) {
  svg.appendChild(el("line", { x1: px(xLo), y1: py(0.25), x2: px(xHi), y2: py(0.25), class: "chart-axis" }));
  svg.appendChild(el("line", { x1: px(xLo), y1: py(0.25), x2: px(xLo), y2: py(5.25), class: "chart-axis" }));

  for (let r = 1; r <= 5; r++) {
    svg.appendChild(el("line", { x1: px(xLo), y1: py(r), x2: px(xHi), y2: py(r), class: "chart-grid" }));
    const tick = el("text", { x: px(xLo) - 8, y: py(r) + 4, class: "chart-tick", "text-anchor": "end" });
    tick.textContent = r;
    svg.appendChild(tick);
  }

  const xl = el("text", { x: (px(xLo) + px(xHi)) / 2, y: H - 10, class: "chart-axis-label", "text-anchor": "middle" });
  xl.textContent = "wackiness (your Nolan index)";
  const yl = el("text", {
    x: 14, y: (py(0.25) + py(5.25)) / 2, class: "chart-axis-label", "text-anchor": "middle",
    transform: `rotate(-90 14 ${(py(0.25) + py(5.25)) / 2})`,
  });
  yl.textContent = "your rating";
  svg.append(xl, yl);
}
