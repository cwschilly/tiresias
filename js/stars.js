/* js/stars.js — accessible half-star rating widget. */

/**
 * Build a 5-star (half-step) selector inside `container`.
 * Returns {get, set, clear}. Calls onChange(value|null) on commit.
 */
export function createStarRow(container, { onChange }) {
  let value = null;

  const row = document.createElement("div");
  row.className = "star-row";
  row.tabIndex = 0;
  row.setAttribute("role", "slider");
  row.setAttribute("aria-valuemin", "0.5");
  row.setAttribute("aria-valuemax", "5");
  row.setAttribute("aria-label", "rating, arrow keys to adjust, delete to clear");

  const stars = [];
  for (let i = 1; i <= 5; i++) {
    const star = document.createElement("span");
    star.className = "star";
    star.innerHTML = `<span class="star-base">★</span><span class="star-fill">★</span>`;

    // Left/right invisible hit zones commit half or full star values
    for (const [cls, v] of [["hit-left", i - 0.5], ["hit-right", i]]) {
      const hit = document.createElement("span");
      hit.className = `hit ${cls}`;
      hit.addEventListener("mouseenter", () => paint(v));
      hit.addEventListener("click", () => commit(v));
      star.appendChild(hit);
    }
    row.appendChild(star);
    stars.push(star);
  }

  row.addEventListener("mouseleave", () => paint(value ?? 0));
  row.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowUp") commit(Math.min(5, (value ?? 0) + 0.5));
    else if (e.key === "ArrowLeft" || e.key === "ArrowDown") commit(Math.max(0.5, (value ?? 1) - 0.5));
    else if (e.key === "Delete" || e.key === "Backspace") clear();
    else return;
    e.preventDefault();
  });

  container.appendChild(row);

  function paint(v) {
    stars.forEach((star, idx) => {
      const fill = v - idx; // >=1 full, 0.5 half, <=0 empty
      star.querySelector(".star-fill").style.width =
        fill >= 1 ? "100%" : fill >= 0.5 ? "50%" : "0%";
    });
  }

  function commit(v) {
    value = v;
    row.setAttribute("aria-valuenow", String(v));
    paint(v);
    onChange(v);
  }

  function clear() {
    value = null;
    row.removeAttribute("aria-valuenow");
    paint(0);
    onChange(null);
  }

  return { get: () => value, set: commit, clear };
}
