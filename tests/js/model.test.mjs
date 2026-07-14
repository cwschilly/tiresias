/* Tests for js/model.js — display math and prophecy tiers.
   Run with: node --test "tests/js/*.test.mjs" */
import { test } from "node:test";
import assert from "node:assert/strict";

import { starsString, prophecy, oscarCounts, oscarLine } from "../../js/model.js";

const approx = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} !== ${b}`);

test("starsString renders halves", () => {
  assert.equal(starsString(3.5), "★★★½☆");
  assert.equal(starsString(5), "★★★★★");
});

test("prophecy returns the tier line for the rating", () => {
  assert.match(prophecy(4.9)[0], /lotus/);
  assert.match(prophecy(4.2)[0], /Trojan Horse/);
  assert.match(prophecy(3.2)[0], /Polyphemus/);
  assert.match(prophecy(0.5)[0], /Charybdis/);
});

test("oscarCounts matches the Poisson formula (parity with Python)", () => {
  const coeffs = {
    method: "euclidean",
    noms: { intercept: 1.0, metric: 0.2 },
    wins: { intercept: 0.2, metric: 0.1 },
  };
  const { noms, wins } = oscarCounts(coeffs, 5, 7);  // (coeffs, fabula, syuzhet)
  const metric = Math.hypot(5, 7);
  approx(noms, Math.exp(1.0 + 0.2 * metric));
  approx(wins, Math.exp(0.2 + 0.1 * metric));
});

test("oscarCounts clamps wins to noms", () => {
  const coeffs = {
    method: "euclidean",
    noms: { intercept: 0, metric: 0 },  // exp(0) = 1
    wins: { intercept: 3, metric: 0 },  // exp(3) ≈ 20
  };
  const { noms, wins } = oscarCounts(coeffs, 5, 5);
  approx(wins, noms);
});

test("oscarLine tier boundaries", () => {
  assert.match(oscarLine({ noms: 9, wins: 5 }), /Kleos/);
  assert.match(oscarLine({ noms: 1.5, wins: 0.2 }), /win something/);
  assert.match(oscarLine({ noms: 0.5, wins: 0.1 }), /sound nom/);
  assert.match(oscarLine({ noms: 0.1, wins: 0 }), /blinder than Tiresias/);
});
