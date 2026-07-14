/* Parity tests: js/personalize.js must match src/personalization/predict.py. */
import { test } from "node:test";
import assert from "node:assert/strict";

import { weightedEuclidean } from "../../js/aggregate.js";
import { deriveAlpha, fitUser, predictAt } from "../../js/personalize.js";

// Coordinates copied from constants.NOLAN_INDEX (subject to live tuning; these
// tests only rely on the films having distinct, spread-out positions)
const FILMS = {
  following: { fabula: 4, syuzhet: 4 },
  memento: { fabula: 2, syuzhet: 8 },
  batman_begins: { fabula: 3, syuzhet: 2 },
  the_prestige: { fabula: 4, syuzhet: 7 },
  inception: { fabula: 5, syuzhet: 5 },
  interstellar: { fabula: 6, syuzhet: 2 },
  dunkirk: { fabula: 1, syuzhet: 7 },
  tenet: { fabula: 10, syuzhet: 10 },
  oppenheimer: { fabula: 2, syuzhet: 3 },
};

const clamp = (v) => Math.min(5, Math.max(0.5, v));

function axisRater(axis, slope = 0.4, intercept = 1.0) {
  return Object.fromEntries(Object.entries(FILMS).map(([key, f]) => [
    key, clamp(intercept + slope * f[axis]),
  ]));
}

function balancedRater(slope = 0.2, intercept = 1.0) {
  return Object.fromEntries(Object.entries(FILMS).map(([key, f]) => [
    key, clamp(intercept + slope * weightedEuclidean(f.fabula, f.syuzhet)),
  ]));
}

test("deriveAlpha is 0.5 for flat ratings", () => {
  const flat = Object.fromEntries(Object.keys(FILMS).map((k) => [k, 3.0]));
  assert.equal(deriveAlpha(flat, FILMS), 0.5);
});

test("deriveAlpha leans toward the driving axis", () => {
  const alphaFabulaHead = deriveAlpha(axisRater("fabula"), FILMS);
  const alphaSyuzhetHead = deriveAlpha(axisRater("syuzhet"), FILMS);
  assert.ok(alphaFabulaHead > 0.6, `fabula-head alpha ${alphaFabulaHead}`);
  assert.ok(alphaSyuzhetHead < 0.4, `syuzhet-head alpha ${alphaSyuzhetHead}`);
  assert.ok(alphaFabulaHead > alphaSyuzhetHead);
});

test("deriveAlpha stays in the unit interval", () => {
  for (const ratings of [axisRater("fabula"), axisRater("syuzhet"), balancedRater()]) {
    const alpha = deriveAlpha(ratings, FILMS);
    assert.ok(alpha >= 0 && alpha <= 1);
  }
});

test("ratings for unknown films are ignored", () => {
  const withJunk = { ...balancedRater(), not_a_film: 2.0 };
  const personal = fitUser(withJunk, FILMS);
  assert.ok(!personal.films.includes("not_a_film"));
  assert.ok(personal.fit.r2Loo > 0.8);
});

test("fitUser uses the derived alpha for its metrics", () => {
  const ratings = balancedRater();
  const personal = fitUser(ratings, FILMS);
  assert.equal(personal.alpha, deriveAlpha(ratings, FILMS));
  const f = FILMS[personal.films[0]];
  const expected = weightedEuclidean(f.fabula, f.syuzhet, personal.alpha);
  assert.ok(Math.abs(personal.metricValues[0] - expected) < 1e-12);
});

test("predictAt recovers a held rating for the balanced rater", () => {
  const ratings = balancedRater();
  const personal = fitUser(ratings, FILMS);
  const f = FILMS.oppenheimer;
  assert.ok(Math.abs(predictAt(personal, f.fabula, f.syuzhet) - ratings.oppenheimer) < 0.25);
});
