/* Parity tests: js/curveFit.js must match src/personalization/curve_fit.py. */
import { test } from "node:test";
import assert from "node:assert/strict";

import { fitBestCurve, predictFromFit } from "../../js/curveFit.js";

const approx = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) < eps, `${a} !== ${b}`);

test("throws with fewer than three points", () => {
  assert.throws(() => fitBestCurve([1, 2], [3, 4]));
});

test("exact line gets a linear fit", () => {
  const x = [1, 2, 3, 4, 5];
  const y = x.map((v) => 1.0 + 0.5 * v);
  const fit = fitBestCurve(x, y);
  assert.equal(fit.degree, 1);
  approx(fit.r2InSample, 1.0);
  approx(predictFromFit(fit, 3), 2.5);
});

test("cubic isn't offered without enough points", () => {
  const x = [-2, -1.2, -0.4, 0.4, 1.2, 2];
  const y = x.map((v) => 0.5 * v ** 3 - v + 3);
  const fit = fitBestCurve(x, y);
  assert.ok(fit.degree === 1 || fit.degree === 2);
});

test("cubic is chosen once there are enough clearly-cubic points", () => {
  const n = 9;
  const x = Array.from({ length: n }, (_, i) => -3 + (i * 6) / (n - 1));
  const y = x.map((v) => {
    const raw = 0.4 * v ** 3 - 0.3 * v ** 2 + v + 2.5;
    return Math.min(5, Math.max(0.5, raw));
  });
  const fit = fitBestCurve(x, y);
  assert.equal(fit.degree, 3);
  assert.ok(fit.r2Loo > 0.9);
});

test("predictions are clamped to the rating bounds", () => {
  const fit = fitBestCurve([0, 1, 2, 3], [5, 5, 5, 5]);
  assert.ok(predictFromFit(fit, 100) <= 5);
  assert.ok(predictFromFit(fit, -100) >= 0.5);
});

test("isolated leverage point does not force a flat linear fit", () => {
  // Parity with test_curve_fit.py::test_isolated_leverage_point_...
  const x = [2, 3, 4, 5, 6, 7, 8, 9, 20];
  const y = x.map((v) => Math.max(0.5, Math.min(5, 5 - 0.08 * (v - 6) ** 2)));
  const fit = fitBestCurve(x, y);
  assert.ok(fit.degree >= 2, `degree ${fit.degree}`);
  assert.ok(fit.r2Loo > 0.9, `LOO R² ${fit.r2Loo}`);
  assert.ok(Math.abs(predictFromFit(fit, 20) - 0.5) < 1e-6);
});
