// <shoebox-crop>: turn a picture and draw, move and resize a crop rectangle on it, optionally at a fixed aspect
// ratio, with a live preview. Works in fractions of the picture as shown after the turn (what the
// shoebox/edit command takes). The turn happens here only; the caller saves it with the crop.
// Properties: src (picture URL), box ([left, top, right, bottom] or null), aspect (width / height in pixels,
// or null for free), turn (degrees clockwise, read-only; rotate(±90) changes it).
// Slot "controls": shown left of the preview, above the picture.
// Keyboard, on the focused picture: arrow keys move the rectangle, Shift with arrow keys resizes it
// (right and bottom edges); a rectangle over the whole picture appears with the first key.

const MIN = 0.02;
const STEP = 0.01; // per key press, of the picture's width or height

const STYLE = `
  :host { display: grid; grid-template-columns: 1fr 1fr; grid-template-areas: "controls side" "stage stage";
    gap: var(--ha-space-3, 12px) var(--ha-space-4, 16px); align-items: start; }
  .controls { grid-area: controls; min-width: 0; }
  .stage { grid-area: stage; justify-self: center; position: relative; display: inline-block; touch-action: none;
    user-select: none; cursor: crosshair; line-height: 0; margin: 12px; max-width: calc(100% - 24px); outline: none; }
  .stage:focus-visible .clip { outline: 2px solid var(--primary-color); outline-offset: 4px; }
  .clip { position: relative; overflow: hidden; border-radius: var(--ha-border-radius-sm, 4px); }
  img { display: block; max-width: min(100%, 900px); max-height: 50vh; pointer-events: none; }
  .box, .frame { position: absolute; box-sizing: border-box; }
  .box { border: 2px solid var(--primary-color); box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5); }
  .frame { cursor: move; }
  .box[hidden], .frame[hidden] { display: none; }
  .box::before, .box::after { content: ""; position: absolute; border: 0 solid rgba(255, 255, 255, 0.45); pointer-events: none; }
  .box::before { left: 33.33%; right: 33.33%; top: 0; bottom: 0; border-left-width: 1px; border-right-width: 1px; }
  .box::after { top: 33.33%; bottom: 33.33%; left: 0; right: 0; border-top-width: 1px; border-bottom-width: 1px; }
  .h { position: absolute; width: 22px; height: 22px; background: var(--primary-color);
    border: 2px solid var(--card-background-color); border-radius: 50%; box-sizing: border-box; z-index: 1; }
  .nw { left: -12px; top: -12px; cursor: nwse-resize; } .ne { right: -12px; top: -12px; cursor: nesw-resize; }
  .sw { left: -12px; bottom: -12px; cursor: nesw-resize; } .se { right: -12px; bottom: -12px; cursor: nwse-resize; }
  .side { grid-area: side; display: flex; flex-direction: column; gap: var(--ha-space-2, 8px); align-items: center;
    color: var(--secondary-text-color); font-size: var(--ha-font-size-s, 12px); }
  canvas { width: 100%; height: 160px; object-fit: contain; }
  @media (max-width: 600px) { canvas { height: 120px; } }
`;

class ShoeboxCrop extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" }).innerHTML = `<style>${STYLE}</style>
      <div class="controls"><slot name="controls"></slot></div>
      <div class="stage" tabindex="0" role="application"><div class="clip"><img alt=""><div class="box" hidden></div></div><div class="frame" hidden>
        <span class="h nw" data-c="nw"></span><span class="h ne" data-c="ne"></span>
        <span class="h sw" data-c="sw"></span><span class="h se" data-c="se"></span></div></div>
      <div class="side"><span class="label"></span><canvas width="1" height="1"></canvas></div>`;
    this._img = this.shadowRoot.querySelector("img");
    this._box = this.shadowRoot.querySelector(".box");
    this._frame = this.shadowRoot.querySelector(".frame");
    this._canvas = this.shadowRoot.querySelector("canvas");
    this._stage = this.shadowRoot.querySelector(".stage");
    this._value = null;
    this._aspect = null;
    this._turn = 0;
    this._source = new Image(); // the picture as given; the stage shows it turned
    this._img.addEventListener("load", () => { this._applyAspect(); this._draw(); });
    this._stage.addEventListener("pointerdown", (e) => this._down(e));
    this._stage.addEventListener("pointermove", (e) => this._move(e));
    this._stage.addEventListener("pointerup", (e) => this._up(e));
    this._stage.addEventListener("pointercancel", (e) => this._up(e));
    this._stage.addEventListener("keydown", (e) => this._key(e));
  }

  // what a screen reader announces for the picture, with how to use the keys
  set keyLabel(text) { this._stage.setAttribute("aria-label", text); }

  _key(e) {
    const dx = { ArrowLeft: -1, ArrowRight: 1 }[e.key] || 0;
    const dy = { ArrowUp: -1, ArrowDown: 1 }[e.key] || 0;
    if (!dx && !dy) return;
    e.preventDefault();
    e.stopPropagation(); // not the viewer's previous and next
    if (!this._value) { this._value = [0, 0, 1, 1]; this._applyAspect(); }
    let [l, t, r, b] = this._value;
    if (e.shiftKey) {
      const k = this._k();
      let w = Math.min(Math.max(r - l + dx * STEP, MIN), 1 - l);
      let h = Math.min(Math.max(b - t + dy * STEP, MIN), 1 - t);
      if (k) { // keep the ratio: follow the side the key changed, then fit inside the picture
        if (dx) h = w / k; else w = h * k;
        if (l + w > 1) { w = 1 - l; h = w / k; }
        if (t + h > 1) { h = 1 - t; w = h * k; }
      }
      [r, b] = [l + w, t + h];
    } else {
      const w = r - l, h = b - t;
      l = Math.min(Math.max(l + dx * STEP, 0), 1 - w);
      t = Math.min(Math.max(t + dy * STEP, 0), 1 - h);
      [r, b] = [l + w, t + h];
    }
    this._value = [l, t, r, b];
    this._draw();
  }

  // the turned picture is an object URL: free it when the editor closes
  disconnectedCallback() {
    if (this._url) URL.revokeObjectURL(this._url);
    this._url = null;
  }

  set src(url) {
    this._turn = 0;
    this._source.src = url;
    this._img.src = url;
  }

  get turn() { return this._turn; }

  // Turn the picture shown by ±90 degrees; the crop rectangle turns with it.
  async rotate(degrees) {
    const v = this._value;
    if (v) {
      const [l, t, r, b] = v;
      this._value = degrees > 0 ? [1 - b, l, 1 - t, r] : [t, 1 - r, b, 1 - l];
    }
    this._turn = (this._turn + degrees + 360) % 360;
    if (!this._source.complete) await new Promise((ok) => this._source.addEventListener("load", ok, { once: true }));
    const { naturalWidth: w, naturalHeight: h } = this._source;
    const quarter = this._turn % 180 !== 0;
    const canvas = document.createElement("canvas");
    canvas.width = quarter ? h : w;
    canvas.height = quarter ? w : h;
    const ctx = canvas.getContext("2d");
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((this._turn * Math.PI) / 180);
    ctx.drawImage(this._source, -w / 2, -h / 2);
    const blob = await new Promise((ok) => canvas.toBlob(ok, "image/jpeg", 0.9));
    if (this._url) URL.revokeObjectURL(this._url);
    this._url = URL.createObjectURL(blob);
    this._img.src = this._url; // its load event re-applies the aspect and draws
  }
  set label(text) { this.shadowRoot.querySelector(".label").textContent = text; }
  get box() { return this._value ? [...this._value] : null; }
  set box(b) { this._value = b ? [...b] : null; this._draw(); }
  get natural() { return [this._img.naturalWidth || 1, this._img.naturalHeight || 1]; }
  set aspect(a) { this._aspect = a || null; this._applyAspect(); this._draw(); }

  // width / height in fractions for the pixel aspect ratio
  _k() {
    if (this._aspect === "original") return 1; // the picture's own shape, also after a turn
    const [w, h] = this.natural;
    return this._aspect ? (this._aspect * h) / w : null;
  }

  _applyAspect() {
    const k = this._k();
    if (!k || !this._img.naturalWidth) return;
    let [l, t, r, b] = this._value || [0, 0, 1, 1];
    const cx = (l + r) / 2, cy = (t + b) / 2;
    let w = r - l, h = b - t;
    if (w / h > k) w = h * k; else h = w / k;
    l = Math.min(Math.max(cx - w / 2, 0), 1 - w);
    t = Math.min(Math.max(cy - h / 2, 0), 1 - h);
    this._value = [l, t, l + w, t + h];
  }

  _point(e) {
    const r = this._img.getBoundingClientRect();
    return [Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1), Math.min(Math.max((e.clientY - r.top) / r.height, 0), 1)];
  }

  _down(e) {
    if (e.button > 0) return;
    const [x, y] = this._point(e);
    const corner = e.composedPath()[0]?.dataset?.c;
    const v = this._value;
    if (corner && v) {
      const ax = corner.includes("w") ? v[2] : v[0], ay = corner.includes("n") ? v[3] : v[1];
      this._drag = { mode: "resize", ax, ay };
    } else if (v && x > v[0] && x < v[2] && y > v[1] && y < v[3]) {
      this._drag = { mode: "move", dx: x - v[0], dy: y - v[1], w: v[2] - v[0], h: v[3] - v[1] };
    } else {
      this._drag = { mode: "resize", ax: x, ay: y, fresh: true };
    }
    this._stage.setPointerCapture(e.pointerId);
    e.preventDefault();
  }

  _move(e) {
    const d = this._drag;
    if (!d) return;
    const [x, y] = this._point(e);
    if (d.mode === "move") {
      const l = Math.min(Math.max(x - d.dx, 0), 1 - d.w), t = Math.min(Math.max(y - d.dy, 0), 1 - d.h);
      this._value = [l, t, l + d.w, t + d.h];
    } else {
      const sx = x >= d.ax ? 1 : -1, sy = y >= d.ay ? 1 : -1;
      let w = Math.abs(x - d.ax), h = Math.abs(y - d.ay);
      const k = this._k();
      if (k) {
        if (w / Math.max(h, 1e-9) > k) w = h * k; else h = w / k;
        const maxW = sx > 0 ? 1 - d.ax : d.ax, maxH = sy > 0 ? 1 - d.ay : d.ay;
        if (w > maxW) { w = maxW; h = w / k; }
        if (h > maxH) { h = maxH; w = h * k; }
      }
      if (d.fresh && w < MIN && h < MIN) return;
      const l = sx > 0 ? d.ax : d.ax - w, t = sy > 0 ? d.ay : d.ay - h;
      this._value = [l, t, l + w, t + h];
    }
    this._draw();
  }

  _up(e) {
    if (!this._drag) return;
    this._drag = null;
    const v = this._value;
    if (v && (v[2] - v[0] < MIN || v[3] - v[1] < MIN)) { this._value = null; this._draw(); }
  }

  _draw() {
    const v = this._value;
    for (const el of [this._box, this._frame]) {
      el.hidden = !v;
      if (v) {
        Object.assign(el.style, {
          left: `${v[0] * 100}%`, top: `${v[1] * 100}%`, width: `${(v[2] - v[0]) * 100}%`, height: `${(v[3] - v[1]) * 100}%`,
        });
      }
    }
    if (!this._img.complete || !this._img.naturalWidth) return;
    const [nw, nh] = this.natural;
    const [l, t, r, b] = v || [0, 0, 1, 1];
    const sw = (r - l) * nw, sh = (b - t) * nh;
    const scale = Math.min(480 / sw, 480 / sh, 1);
    this._canvas.width = Math.max(1, Math.round(sw * scale));
    this._canvas.height = Math.max(1, Math.round(sh * scale));
    this._canvas.getContext("2d").drawImage(this._img, l * nw, t * nh, sw, sh, 0, 0, this._canvas.width, this._canvas.height);
  }
}

if (!customElements.get("shoebox-crop")) customElements.define("shoebox-crop", ShoeboxCrop);
