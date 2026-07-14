/* Selection-logic tests for js/wit.js — deliberately copy-agnostic so the
   one-liners can be rewritten freely; what's pinned is which bucket fires. */
import { test } from "node:test";
import assert from "node:assert/strict";

import { alphaLine, fitShapeLine, WEAK_FIT_THRESHOLD } from "../../js/wit.js";

test("alpha buckets are five distinct bands with inclusive upper bounds", () => {
  const bands = [0.1, 0.3, 0.5, 0.7, 0.9].map(alphaLine);
  assert.equal(new Set(bands).size, 5, "each band has its own line");

  // Upper boundaries belong to the band below them
  assert.equal(alphaLine(0.0), bands[0]);
  assert.equal(alphaLine(0.2), bands[0]);
  assert.equal(alphaLine(0.4), bands[1]);
  assert.equal(alphaLine(0.6), bands[2]);
  assert.equal(alphaLine(0.8), bands[3]);
  assert.equal(alphaLine(1.0), bands[4]);
});

const strong = (degree, lead) => ({ degree, coeffs: [lead, 0, 0, 0], r2InSample: 0.9 });

test("weak fits get the same line regardless of shape", () => {
  const weakR2 = WEAK_FIT_THRESHOLD - 0.01;
  const a = fitShapeLine({ degree: 2, coeffs: [1, 0, 0], r2InSample: weakR2 });
  const b = fitShapeLine({ degree: 1, coeffs: [-1, 0], r2InSample: weakR2 });
  assert.equal(a, b);
  assert.notEqual(a, fitShapeLine(strong(2, 1)), "weak line differs from strong lines");
});

test("strong fits pick by degree and leading-coefficient sign", () => {
  const shapes = [strong(1, 0.5), strong(1, -0.5), strong(2, 0.5),
                  strong(2, -0.5), strong(3, 0.5), strong(3, -0.5)];
  const lines = shapes.map(fitShapeLine);
  assert.equal(new Set(lines).size, 6, "all six shapes have distinct lines");
});
