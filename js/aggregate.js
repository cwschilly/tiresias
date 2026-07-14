/* js/aggregate.js — mirrors src/nolan_index/aggregate.py exactly.
   Change both or neither. */

export function euclidean(fabula, syuzhet) {
  return Math.hypot(fabula, syuzhet);
}

/**
 * Euclidean distance with alpha = fabula weight, beta = syuzhet weight.
 * alpha + beta always sum to 1, so alpha is the only free parameter; beta is
 * just its complement, named for clarity in the formula below.
 * alpha = 0.5 reduces exactly to euclidean(); alpha = 1.0 ignores syuzhet
 * entirely, alpha = 0.0 ignores fabula.
 */
export function weightedEuclidean(fabula, syuzhet, alpha = 0.5) {
  const beta = 1 - alpha;
  return Math.sqrt(2 * alpha * fabula ** 2 + 2 * beta * syuzhet ** 2);
}

export const AGGREGATORS = { euclidean };
export const DEFAULT_METHOD = "euclidean";

export function aggregate(fabula, syuzhet, method = DEFAULT_METHOD) {
  return AGGREGATORS[method](fabula, syuzhet);
}
