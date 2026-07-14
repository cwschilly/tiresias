/* js/wit.js — one-liner flavor text for the step flow.
   logic (buckets and fit shapes) is the part under test. */

/* ── Alpha buckets: fabula weight in [0, 1], five bands ── */

const ALPHA_LINES = [
  [0.2, "Who needs a plot when you can have an incomprehsible narrative structure?"],
  [0.4, "I'll take a backwards-marching timeline over a sensible plot any day."],
  [0.6, "Perfectly balanced, as all things should be."],
  [0.8, "Did I follow the plot? Not at all. But did I care? Not at all."],
  [1.0, "I don't care how crazy the timeline is. For me, the action is the juice."],
];

export function alphaLine(alpha) {
  return ALPHA_LINES.find(([max]) => alpha <= max + 1e-9)[1];
}

/* ── Fit shapes: weak correlation wins, then degree + leading-coefficient sign ── */

export const WEAK_FIT_THRESHOLD = 0.30;

const FIT_LINES = {
  weak: "The fit's not great...he is blind, after all.",
  "1+": "A classic, positive linear fit. The crazier the better.",
  "1-": "A negative trend! You like Nolan most when he's restrained.",
  "2+": "A positive quadratic fit. Give me a straightforward movie, or give me Tenet. No half measures!",
  "2-": "A negative quadratic. Some craziness is good...but don't get carried away.",
  "3+": "A cubic fit, trending upwards. You're like the absurdity, but you're wary of its power.",
  "3-": "A descending cubit fit. You can't make up your mind.",
};

/** fit: {degree, coeffs (highest power first), r2InSample}. */
export function fitShapeLine(fit) {
  if (fit.r2InSample < WEAK_FIT_THRESHOLD) return FIT_LINES.weak;
  const sign = fit.coeffs[0] >= 0 ? "+" : "-";
  return FIT_LINES[`${fit.degree}${sign}`];
}
