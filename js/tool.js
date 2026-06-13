/* js/tool.js — rating UI and ONNX inference for Tiresias */

const FILMS = [
  { key: "following",             label: "Following (1998)",        features: [0.2,  0.006,  70, 1, 10,  0] },
  { key: "memento",               label: "Memento (2000)",          features: [0.8,  0.009, 113, 1, 30,  1] },
  { key: "insomnia",              label: "Insomnia (2002)",         features: [0.1,  0.046, 118, 0, 60,  1] },
  { key: "batman_begins",         label: "Batman Begins (2005)",    features: [0.1,  0.150, 140, 0, 85,  0] },
  { key: "the_prestige",          label: "The Prestige (2006)",     features: [0.6,  0.040, 130, 0, 90,  0] },
  { key: "the_dark_knight",       label: "The Dark Knight (2008)",  features: [0.2,  0.185, 152, 0, 95,  0] },
  { key: "inception",             label: "Inception (2010)",        features: [0.7,  0.160, 148, 1, 88,  0] },
  { key: "the_dark_knight_rises", label: "The Dark Knight Rises (2012)", features: [0.1, 0.250, 164, 0, 90, 0] },
  { key: "interstellar",          label: "Interstellar (2014)",     features: [0.7,  0.165, 169, 1, 85,  0] },
  { key: "dunkirk",               label: "Dunkirk (2017)",          features: [0.5,  0.100, 106, 0, 80,  0] },
  { key: "tenet",                 label: "Tenet (2020)",            features: [2.1,  0.205, 150, 1, 80,  0] },
  { key: "oppenheimer",           label: "Oppenheimer (2023)",      features: [0.4,  0.100, 180, 0, 92,  0] },
];

const ODYSSEY_FEATURES = [0.3, 0.165, 170, 0, 90, 0];
const MIN_RATINGS      = 3;

const ratings  = {};
let pipeline   = null;
let ortSession = null;

// ── Star UI ───────────────────────────────────────────────────────────────────
function buildFilmCards() {
  const grid = document.getElementById("filmGrid");
  FILMS.forEach(film => {
    const card = document.createElement("div");
    card.className = "film-card";
    card.id = `card-${film.key}`;
    card.innerHTML = `
      <label>${film.label}</label>
      <div class="star-row" id="stars-${film.key}"></div>
      <div class="rating-display" id="disp-${film.key}">not rated</div>`;
    grid.appendChild(card);

    const row = card.querySelector(".star-row");
    for (let i = 1; i <= 10; i++) {
      const s = document.createElement("span");
      s.className   = "half-star";
      s.dataset.value = (i * 0.5).toFixed(1);
      s.textContent = i % 2 === 1 ? "½" : "★";
      s.addEventListener("click", () => setRating(film.key, parseFloat(s.dataset.value)));
      row.appendChild(s);
    }

    const clr = document.createElement("button");
    clr.className   = "unseen-btn";
    clr.textContent = "clear";
    clr.addEventListener("click", () => clearRating(film.key));
    row.appendChild(clr);
  });
}

function setRating(key, value) {
  ratings[key] = value;
  document.getElementById(`stars-${key}`)
    .querySelectorAll(".half-star")
    .forEach(s => s.classList.toggle("active", parseFloat(s.dataset.value) <= value));
  document.getElementById(`disp-${key}`).textContent = `${value.toFixed(1)} / 5.0`;
  document.getElementById(`card-${key}`).classList.add("rated");
  refreshUI();
}

function clearRating(key) {
  delete ratings[key];
  document.getElementById(`stars-${key}`)
    .querySelectorAll(".half-star").forEach(s => s.classList.remove("active"));
  document.getElementById(`disp-${key}`).textContent = "not rated";
  document.getElementById(`card-${key}`).classList.remove("rated");
  refreshUI();
}

function refreshUI() {
  const n         = Object.keys(ratings).length;
  const remaining = Math.max(0, MIN_RATINGS - n);
  document.getElementById("remaining").textContent  = remaining;
  document.getElementById("predictBtn").disabled    = n < MIN_RATINGS;
  document.getElementById("minNotice").style.display = n >= MIN_RATINGS ? "none" : "block";
}

// ── PCA helpers ───────────────────────────────────────────────────────────────
function dot(a, b)   { return a.reduce((s, v, i) => s + v * b[i], 0); }
function matVec(M, v) { return M.map(row => dot(row, v)); }

function getTasteVector() {
  const { film_cols, scaler_mean, scaler_std, pca_mean, pca_components } = pipeline;
  const ratingVec = film_cols.map(k => ratings[k] ?? 0);
  const maskVec   = film_cols.map(k => ratings[k] != null ? 1 : 0);
  const raw       = [...ratingVec, ...maskVec];
  const scaled    = raw.map((v, i) => (v - scaler_mean[i]) / scaler_std[i]);
  const centered  = scaled.map((v, i) => v - pca_mean[i]);
  return matVec(pca_components, centered);
}

// ── ONNX inference ────────────────────────────────────────────────────────────
async function predict() {
  const taste    = getTasteVector();
  const inputVec = new Float32Array([...taste, ...ODYSSEY_FEATURES]);
  const tensor   = new ort.Tensor("float32", inputVec, [1, inputVec.length]);
  const output   = await ortSession.run({ input: tensor });
  const raw      = Object.values(output)[0].data[0];
  return Math.min(5.0, Math.max(0.5, Math.round(raw * 2) / 2));
}

function starsString(rating) {
  let s = "";
  for (let i = 1; i <= 5; i++) {
    if (rating >= i)           s += "★";
    else if (rating >= i - 0.5) s += "½";
    else                        s += "☆";
  }
  return s;
}

// ── Boot ──────────────────────────────────────────────────────────────────────
buildFilmCards();
refreshUI();

Promise.all([
  fetch("output/pipeline.json").then(r => r.json()),
  ort.InferenceSession.create("output/model.onnx"),
]).then(([p, s]) => {
  pipeline   = p;
  ortSession = s;
}).catch(err => console.error("Failed to load model assets:", err));

document.getElementById("predictBtn").addEventListener("click", async () => {
  if (!pipeline || !ortSession) {
    alert("Model still loading — please try again in a moment.");
    return;
  }

  const rating = await predict();
  const n      = Object.keys(ratings).length;

  document.getElementById("bigRating").textContent    = rating.toFixed(1);
  document.getElementById("starsDisplay").textContent = starsString(rating);
  document.getElementById("confidenceNote").textContent =
    `Based on ${n} of 12 ratings. ` +
    (n < 6 ? "Rate more films for a sharper prediction." : "Good basis for a prediction.");

  const result = document.getElementById("result");
  result.style.display = "block";
  result.scrollIntoView({ behavior: "smooth", block: "nearest" });
});
