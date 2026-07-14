/* Parity tests: js/aggregate.js must match src/nolan_index/aggregate.py. */
import { test } from "node:test";
import assert from "node:assert/strict";

import { aggregate, euclidean, weightedEuclidean } from "../../js/aggregate.js";

test("euclidean matches the Pythagorean distance", () => {
  assert.equal(euclidean(3, 4), 5);
  assert.equal(euclidean(0, 0), 0);
});

test("aggregate dispatches to the named method", () => {
  assert.equal(aggregate(6, 8, "euclidean"), 10);
});

test("aggregate defaults to euclidean", () => {
  assert.equal(aggregate(6, 8), 10);
});

test("weightedEuclidean at alpha 0.5 reduces to euclidean", () => {
  assert.ok(Math.abs(weightedEuclidean(3, 4, 0.5) - 5) < 1e-9);
});

test("weightedEuclidean extremes ignore one axis", () => {
  assert.ok(Math.abs(weightedEuclidean(3, 99, 1.0) - Math.sqrt(2) * 3) < 1e-9);
  assert.ok(Math.abs(weightedEuclidean(99, 4, 0.0) - Math.sqrt(2) * 4) < 1e-9);
});
