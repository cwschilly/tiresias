/* Tests for the pure math in js/share.js — the card drawing is verified in a
   real browser, but the optimum search has exact expectations. */
import { test } from "node:test";
import assert from "node:assert/strict";

import { computeOptimal, SITE_URL } from "../../js/share.js";
import { predictAt } from "../../js/personalize.js";

// personal objects need only {fit: {coeffs}, alpha} for predictAt
const personal = (coeffs, alpha = 0.5) => ({ fit: { coeffs }, alpha });

test("rising taste peaks at maximum wackiness (10, 10)", () => {
  const p = personal([0.25, 0.5]);   // rating = 0.5 + 0.25·metric, always rising
  const opt = computeOptimal(p);
  assert.equal(opt.fabula, 10);
  assert.equal(opt.syuzhet, 10);
});

test("falling taste peaks at (0, 0)", () => {
  const p = personal([-0.25, 4.5]);
  const opt = computeOptimal(p);
  assert.equal(opt.fabula, 0);
  assert.equal(opt.syuzhet, 0);
});

test("peaked quadratic lands on the balanced diagonal at the peak metric", () => {
  // rating peaks at metric 6; at alpha 0.5 the diagonal hits it at f = s = 6/√2
  const p = personal([-0.1, 1.2, 1.0]);
  const opt = computeOptimal(p);
  assert.equal(opt.fabula, opt.syuzhet, "tie-break should pick the diagonal");
  assert.ok(Math.abs(Math.hypot(opt.fabula, opt.syuzhet) - 6) < 0.15,
            `metric ${Math.hypot(opt.fabula, opt.syuzhet)}`);
});

test("returned rating matches predictAt at the returned point", () => {
  const p = personal([-0.1, 1.2, 1.0]);
  const opt = computeOptimal(p);
  assert.equal(opt.rating, predictAt(p, opt.fabula, opt.syuzhet));
});

test("the optimum lands on the sliders' grid (0..10, step 0.1)", () => {
  // tool.js seeds the range inputs with these values, so they must be
  // in-range multiples of the 0.1 step or the browser would clamp/snap them
  for (const coeffs of [[0.25, 0.5], [-0.25, 4.5], [-0.1, 1.2, 1.0]]) {
    const opt = computeOptimal(personal(coeffs));
    for (const v of [opt.fabula, opt.syuzhet]) {
      assert.ok(v >= 0 && v <= 10, `${v} out of range`);
      assert.ok(Math.abs(v * 10 - Math.round(v * 10)) < 1e-9, `${v} off-grid`);
    }
  }
});

test("the card URL is the real domain", () => {
  assert.equal(SITE_URL, "willtheodysseybegood.com");
});
