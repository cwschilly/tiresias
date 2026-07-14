/* js/personalize.js — the person's fabula weight alpha (syuzhet weight
   beta = 1 - alpha) read directly off their ratings, then a curve fit
   against the alpha-weighted wackiness metric.
   Mirrors src/personalization/predict.py exactly — change both or neither. */

import { weightedEuclidean } from "./aggregate.js";
import { fitBestCurve, predictFromFit } from "./curveFit.js";

const INDEX_SCALE = 10;

/**
 * The person's fabula weight, straight from their ratings: mean-center,
 * correlate against each axis, take fabula's share of the combined affinity
 * magnitude. Flat or axis-blind raters fall back to a balanced 0.5.
 * ratings: {filmKey: 0.5-5.0}, films: {filmKey: {fabula, syuzhet}} (0-10).
 */
export function deriveAlpha(ratings, films) {
  const keys = Object.keys(ratings).filter((k) => films[k] != null);
  const r = keys.map((k) => ratings[k]);
  const mean = r.reduce((s, v) => s + v, 0) / r.length;
  const w = r.map((v) => v - mean);
  const denom = w.reduce((s, v) => s + Math.abs(v), 0);
  if (denom < 1e-9) return 0.5;

  const affinity = (axis) => Math.abs(
    keys.reduce((s, k, i) => s + w[i] * (films[k][axis] / INDEX_SCALE), 0) / denom);
  const fabulaAff = affinity("fabula");
  const syuzhetAff = affinity("syuzhet");
  const total = fabulaAff + syuzhetAff;
  return total > 1e-9 ? fabulaAff / total : 0.5;
}

/** Returns {fit, alpha}: alpha derived first, then the LOO-best curve at that alpha. */
export function fitUser(ratings, films) {
  const keys = Object.keys(ratings).filter((k) => films[k] != null);
  const alpha = deriveAlpha(ratings, films);
  const x = keys.map((k) => weightedEuclidean(films[k].fabula, films[k].syuzhet, alpha));
  const y = keys.map((k) => ratings[k]);
  return { fit: fitBestCurve(x, y), alpha, films: keys, metricValues: x };
}

/** Predicted rating at an index position, using the derived alpha. */
export function predictAt({ fit, alpha }, fabula, syuzhet) {
  return predictFromFit(fit, weightedEuclidean(fabula, syuzhet, alpha));
}
