/* js/curveFit.js — fits a visitor's own ratings against the aggregated Nolan
   Index metric. Mirrors src/personalization/curve_fit.py exactly — change
   both or neither. */

const MIN_POINTS_FOR_DEGREE = { 1: 3, 2: 4, 3: 5 };
const CUBIC_MIN_POINTS = 8;

/* ── Small linear-algebra helpers (matrices are at most 4x4 here) ── */

function transpose(A) {
  return A[0].map((_, j) => A.map((row) => row[j]));
}

function matMul(A, B) {
  return A.map((row) => B[0].map((_, j) => row.reduce((s, v, k) => s + v * B[k][j], 0)));
}

function matVec(A, v) {
  return A.map((row) => row.reduce((s, a, i) => s + a * v[i], 0));
}

/** Gaussian elimination with partial pivoting. */
function solve(A, b) {
  const n = b.length;
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let pivot = col;
    for (let r = col + 1; r < n; r++) {
      if (Math.abs(M[r][col]) > Math.abs(M[pivot][col])) pivot = r;
    }
    [M[col], M[pivot]] = [M[pivot], M[col]];
    for (let r = 0; r < n; r++) {
      if (r === col) continue;
      const factor = M[r][col] / M[col][col];
      for (let c = col; c <= n; c++) M[r][c] -= factor * M[col][c];
    }
  }
  return M.map((row, i) => row[n] / row[i]);
}

/** Least-squares polynomial fit via the normal equations. Highest power first. */
function polyfit(x, y, degree) {
  const n = degree + 1;
  const V = x.map((xi) => Array.from({ length: n }, (_, k) => xi ** (n - 1 - k)));
  const VT = transpose(V);
  return solve(matMul(VT, V), matVec(VT, y));
}

function evaluate(coeffs, x) {
  return coeffs.reduce((acc, c) => acc * x + c, 0);
}

function r2(yTrue, yPred) {
  const mean = yTrue.reduce((s, v) => s + v, 0) / yTrue.length;
  const ssRes = yTrue.reduce((s, v, i) => s + (v - yPred[i]) ** 2, 0);
  const ssTot = yTrue.reduce((s, v) => s + (v - mean) ** 2, 0);
  return ssTot > 1e-9 ? 1 - ssRes / ssTot : 0;
}

/* Leave-one-out R², scored only on held-out points the remaining points
   bracket. A film outside the training x-range (usually Tenet) can only be
   extrapolated, and no polynomial can be fairly validated on extrapolation —
   the catastrophic held-out error would force a flat linear fit on exactly
   the users whose taste is most curved. Extreme films still train every
   other fold. Predictions are clamped, as deployed. */
function looR2(x, y, degree) {
  const preds = [], trues = [];
  for (let i = 0; i < x.length; i++) {
    const xi = x.filter((_, j) => j !== i);
    const yi = y.filter((_, j) => j !== i);
    if (x[i] < Math.min(...xi) || x[i] > Math.max(...xi)) continue;
    preds.push(clampRating(evaluate(polyfit(xi, yi, degree), x[i])));
    trues.push(y[i]);
  }
  return r2(trues, preds);
}

function candidateDegrees(n) {
  let degrees = Object.entries(MIN_POINTS_FOR_DEGREE)
    .filter(([, min]) => n >= min)
    .map(([d]) => Number(d));
  if (n < CUBIC_MIN_POINTS) degrees = degrees.filter((d) => d !== 3);
  return degrees;
}

export function clampRating(raw) {
  return Math.min(5, Math.max(0.5, raw));
}

/** Fits the best-generalizing polynomial (by leave-one-out R²) through (x, y) pairs. */
export function fitBestCurve(x, y) {
  if (x.length < 3) throw new Error("Need at least 3 rated films to fit a curve.");

  let best = null;
  for (const degree of candidateDegrees(x.length)) {
    const r2Loo = looR2(x, y, degree);
    if (!best || r2Loo > best.r2Loo) best = { degree, r2Loo };
  }

  const coeffs = polyfit(x, y, best.degree);
  const r2InSample = r2(y, x.map((xi) => clampRating(evaluate(coeffs, xi))));
  return { degree: best.degree, coeffs, r2InSample, r2Loo: best.r2Loo };
}

export function predictFromFit(fit, x) {
  return clampRating(evaluate(fit.coeffs, x));
}
