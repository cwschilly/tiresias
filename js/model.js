/* js/model.js — pure display math and prophecy text (no DOM). */

import { aggregate } from "./aggregate.js";

export function starsString(rating) {
  const r = Math.round(rating * 2) / 2;
  let s = "";
  for (let i = 1; i <= 5; i++) {
    s += r >= i ? "★" : r >= i - 0.5 ? "½" : "☆";
  }
  return s;
}

/* ── Oscars ─────────────────────────────────────────────────────────────── */

/**
 * Expected Oscar counts at an index position, from the Poisson coefficients
 * in pipeline.json (mirrors src/oscars/predict.py::predict_counts).
 */
export function oscarCounts(coeffs, fabula, syuzhet) {
  const metric = aggregate(fabula, syuzhet, coeffs.method);
  const expected = (c) => Math.exp(c.intercept + c.metric * metric);
  const noms = expected(coeffs.noms);
  return { noms, wins: Math.min(expected(coeffs.wins), noms) };
}

const OSCAR_TIERS = [
  [6, (n, w) => `${n} nominations, ${w} wins. Kleos!`],
  [3, (n, w) => `${n} nominations, ${w} wins. Kleos!`],
  [1, (n, w) => `${n} nominations, ${w} wins. Surely it'll win something...right?`],
  [0.3, (n, w) => `${n} nominations, ${w} wins. Idk, maybe it'll get a sound nom.`],
  [0, () => `The Academy is blinder than Tiresias.`],
];

/** One-line Oscar prophecy from expected counts. */
export function oscarLine({ noms, wins }) {
  const n = noms.toFixed(1), w = wins.toFixed(1);
  return OSCAR_TIERS.find(([min]) => noms >= min)[1](n, w);
}

/* ── Prophecies ─────────────────────────────────────────────────────────── */

const TIERS = [
  [4.5,  "This movie is made for you. You'll be feasting on lotus all month."],
  [4.0,  "You'll be bursting with joy, like a Trojan Horse of excitement."],
  [3.5,  "It'll be a good movie, but why is everyone being so weird about it?"],
  [3.0,  "You'll be glad you watched it, but, like Polyphemus, you probably won't see it again."],
  [2.5,  "A lukewarm take on Christopher Nolan? Sorcery like this has not been witnessed since the days of Circe..."],
  [1.5,  "Tie yourself to the mast and plug your ears...outlook is not good."],
  [0,    "You'd sooner tongue-kiss Charybdis than watch this movie. I applaud you for even taking the time to make it this far."],
];

/** The tier line for a predicted rating. */
export function prophecy(rating) {
  return [TIERS.find(([min]) => rating >= min)[1]];
}
