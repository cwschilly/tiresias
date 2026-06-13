/* js/eye.js — SVG eye animation for the Tiresias landing page */

const EYE = {
  cx: 160,
  cy: 60,
  rx: 140,
  openness: 0,

  HOVER_OPENNESS: 0.28,
  FULL_OPENNESS: 1.0,

  topLid: null,
  botLid: null,
  iris: null,
  pupil: null,
  shine: null,
  eyeWhite: null,
  clipPath: null,
  overlay: null,
  _rafId: null,

  init() {
    this.topLid = document.getElementById("lid-top");
    this.botLid = document.getElementById("lid-bottom");
    this.iris = document.getElementById("eye-iris");
    this.pupil = document.getElementById("eye-pupil");
    this.shine = document.getElementById("eye-shine");
    this.eyeWhite = document.getElementById("eye-white");
    this.clipPath = document.getElementById("eye-clip-path");
    this.overlay = document.getElementById("expand-overlay");

    this._render();
  },

  _lidPath(openness, isTop) {
    const { cx, cy, rx } = this;

    const maxRy = 52;
    const ry = openness * maxRy;

    const lx = cx - rx;
    const rx_ = cx + rx;

    const cp = ry * 1.1;

    if (isTop) {
      return `
        M ${lx} ${cy}
        C ${lx + rx * 0.45} ${cy - cp},
          ${rx_ - rx * 0.45} ${cy - cp},
          ${rx_} ${cy}
      `;
    }

    return `
      M ${rx_} ${cy}
      C ${rx_ - rx * 0.45} ${cy + cp},
        ${lx + rx * 0.45} ${cy + cp},
        ${lx} ${cy}
    `;
  },

  _clipPath(openness) {
    const { cx, cy, rx } = this;

    const maxRy = 52;
    const ry = openness * maxRy;

    const lx = cx - rx;
    const rx_ = cx + rx;

    const cp = ry * 1.1;

    return `
      M ${lx} ${cy}
      C ${lx + rx * 0.45} ${cy - cp},
        ${rx_ - rx * 0.45} ${cy - cp},
        ${rx_} ${cy}
      C ${rx_ - rx * 0.45} ${cy + cp},
        ${lx + rx * 0.45} ${cy + cp},
        ${lx} ${cy}
      Z
    `;
  },

  _render() {
    const o = this.openness;

    this.topLid.setAttribute("d", this._lidPath(o, true));
    this.botLid.setAttribute("d", this._lidPath(o, false));

    const clip = this._clipPath(o);

    this.clipPath.setAttribute("d", clip);
    this.eyeWhite.setAttribute("d", clip);

    const opacity = Math.min(1, o / 0.3);

    this.iris.style.opacity = opacity;
    this.pupil.style.opacity = opacity;
    this.shine.style.opacity = opacity;

    const scale = 0.5 + 0.5 * o;

    this.iris.setAttribute(
      "transform",
      `translate(${this.cx},${this.cy}) scale(${scale}) translate(-${this.cx},-${this.cy})`
    );
  },

  _animateTo(target, duration, easing, onDone) {
    if (this._rafId) cancelAnimationFrame(this._rafId);

    const start = this.openness;
    const delta = target - start;
    const t0 = performance.now();

    const step = (now) => {
      const p = Math.min((now - t0) / duration, 1);
      const ease = easing(p);

      this.openness = start + delta * ease;
      this._render();

      if (p < 1) {
        this._rafId = requestAnimationFrame(step);
      } else {
        this._rafId = null;
        if (onDone) onDone();
      }
    };

    this._rafId = requestAnimationFrame(step);
  },

  hover() {
    this._animateTo(this.HOVER_OPENNESS, 280, EYE._easeOut);
  },

  unhover() {
    this._animateTo(0, 280, EYE._easeOut);
  },

  openThenNavigate(href) {
    this._animateTo(1, 420, EYE._easeOut, () => {
      this._animateTo(0, 120, EYE._easeIn, () => {
        this._animateTo(1, 180, EYE._easeOut, () => {
          this._expandAndNavigate(href);
        });
      });
    });
  },

  _expandAndNavigate(href) {
    const overlay = this.overlay;

    const svg = document.getElementById("eye-svg");
    const rect = svg.getBoundingClientRect();

    const irisPx = {
      x: rect.left + (this.cx / 320) * rect.width,
      y: rect.top + (this.cy / 120) * rect.height,
    };

    const maxDim =
      Math.sqrt(window.innerWidth ** 2 + window.innerHeight ** 2) * 2;

    overlay.style.cssText = `
      position: fixed;
      border-radius: 50%;
      background: var(--green-dark);
      pointer-events: all;
      z-index: 200;
      width:0;
      height:0;
      left:${irisPx.x}px;
      top:${irisPx.y}px;
      transform:translate(-50%,-50%);
      transition:
        width .55s cubic-bezier(.4,0,.2,1),
        height .55s cubic-bezier(.4,0,.2,1);
    `;

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        overlay.style.width = `${maxDim}px`;
        overlay.style.height = `${maxDim}px`;

        setTimeout(() => {
          window.location.href = href;
        }, 580);
      });
    });
  },

  _easeOut: (p) => 1 - (1 - p) ** 3,
  _easeIn: (p) => p ** 2,
};

export default EYE;
