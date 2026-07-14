/* js/steps.js — Wrapped-style tap-through step controller.
   One .step visible at a time; navigation is buttons-only (scroll and
   swipe gestures must never change steps — steps have scrollable content).
   Progress dots reflect the current position. */

export function createSteps(container, { onEnter = () => {} } = {}) {
  const steps = [...container.querySelectorAll(".step")];
  const dots = buildDots(container, steps.length);
  let current = 0;
  const gates = new Map();   // step index -> () => boolean (may we leave it forward?)

  function show(index, direction) {
    if (index < 0 || index >= steps.length) return;
    if (index > current) {
      const gate = gates.get(current);
      if (gate && !gate()) return;
    }
    steps[current].classList.remove("active");
    current = index;
    const step = steps[current];
    step.classList.remove("from-above", "from-below");
    step.classList.add("active", direction > 0 ? "from-below" : "from-above");
    dots.forEach((dot, i) => dot.classList.toggle("active", i === current));
    container.scrollTop = 0;
    onEnter(current);
  }

  steps[0].classList.add("active");
  dots[0].classList.add("active");

  return {
    next: () => show(current + 1, 1),
    back: () => show(current - 1, -1),
    go: (i) => show(i, i > current ? 1 : -1),
    setGate: (index, predicate) => gates.set(index, predicate),
    current: () => current,
  };
}

function buildDots(container, n) {
  const wrap = document.createElement("div");
  wrap.className = "step-dots";
  const dots = Array.from({ length: n }, () => {
    const dot = document.createElement("span");
    dot.className = "step-dot";
    wrap.appendChild(dot);
    return dot;
  });
  container.appendChild(wrap);
  return dots;
}
