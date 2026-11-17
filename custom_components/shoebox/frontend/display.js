// "Preview": every option of a rotation's device URL, tried on one picture.
// Knobs on the left (Home Assistant's own ha-form), the prepared picture on the right, and the
// parameters to put on the device URL below. The preview comes from the render view, which takes
// the same options, through a signed URL.

const RENDER_URL = "/api/shoebox/render";
const DEBOUNCE_MS = 300;

// Common displays: size and the palette their panel shows
const PRESETS = {
  lcd_800x480: { label: "LCD 800 × 480 (ESP32-S3/P4 7\")", width: 800, height: 480, colors: "full" },
  lcd_1024x600: { label: "LCD 1024 × 600", width: 1024, height: 600, colors: "full" },
  lcd_320x240: { label: "LCD 320 × 240 (ILI9341)", width: 320, height: 240, colors: "full" },
  epd_800x480_bw: { label: "E-paper 7.5\" 800 × 480, black and white", width: 800, height: 480, colors: "bw" },
  epd_800x480_spectra6: { label: "E-paper 7.3\" 800 × 480, Spectra 6", width: 800, height: 480, colors: "spectra6", saturation: 1.4, contrast: 1.1 },
  epd_600x448_acep7: { label: "E-paper 5.65\" 600 × 448, 7 colours", width: 600, height: 448, colors: "acep7", saturation: 1.3 },
  epd_400x300_gray4: { label: "E-paper 4.2\" 400 × 300, 4 greys", width: 400, height: 300, colors: "gray4" },
  epd_296x128_bw: { label: "E-paper 2.9\" 296 × 128, black and white", width: 296, height: 128, colors: "bw" },
};
const DEFAULTS = { fit: "cover", colors: "full", custom: "", dither: "floyd", format: "auto", contrast: 1, saturation: 1, brightness: 1 };

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const sizeText = (n) => (n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} kB` : `${(n / 1048576).toFixed(1)} MB`);

// The device URL parameters for the knobs, without the ones left at their defaults
function deviceParams(d) {
  const p = new URLSearchParams({ width: d.width, height: d.height, fit: d.fit });
  const colors = d.colors === "custom" ? d.custom.replace(/\s+/g, "") : d.colors;
  if (d.colors !== "full" && colors) {
    p.set("colors", colors);
    if (d.dither === "none") p.set("dither", "none");
  }
  if (d.format !== "auto") p.set("format", d.format);
  for (const k of ["contrast", "saturation", "brightness"]) if (Number(d[k]) !== 1) p.set(k, String(Number(d[k])));
  return p;
}

// Commas may stand in a query: own colours read better without %2C
const paramText = (p) => p.toString().replace(/%2C/gi, ",");

export function openDisplayPreview(panel, item) {
  const t = panel.t;
  let data = { preset: "lcd_800x480", ...DEFAULTS, ...presetValues("lcd_800x480") };
  let seq = 0;
  let timer;
  let objectUrl;

  function presetValues(key) {
    const { label, ...values } = PRESETS[key];
    return { ...DEFAULTS, ...values };
  }

  const option = (value, label) => ({ value, label });
  const schema = () => required([
    { name: "preset", selector: { select: { mode: "dropdown", options: [...Object.entries(PRESETS).map(([k, v]) => option(k, v.label)), option("custom", t("display_custom"))] } } },
    { name: "", type: "grid", column_min_width: "100px", schema: [
      { name: "width", selector: { number: { min: 1, max: 4096, mode: "box" } } },
      { name: "height", selector: { number: { min: 1, max: 4096, mode: "box" } } },
    ] },
    { name: "fit", selector: { select: { mode: "dropdown", options: [option("cover", t("display_fit_cover")), option("contain", t("display_fit_contain"))] } } },
    { name: "colors", selector: { select: { mode: "dropdown", options: [
      option("full", t("display_colors_full")),
      option("bw", t("display_colors_bw")),
      option("gray4", t("display_colors_gray", { count: 4 })),
      option("gray16", t("display_colors_gray", { count: 16 })),
      option("spectra6", t("display_colors_spectra6")),
      option("acep7", t("display_colors_acep7")),
      option("custom", t("display_colors_custom")),
    ] } } },
    ...(data.colors === "custom" ? [{ name: "custom", selector: { text: {} } }] : []),
    ...(data.colors !== "full" ? [{ name: "dither", selector: { select: { mode: "dropdown", options: [option("floyd", "Floyd–Steinberg"), option("none", t("display_dither_none"))] } } }] : []),
    { name: "format", selector: { select: { mode: "dropdown", options: [option("auto", t("display_format_auto")), option("jpeg", "JPEG"), option("png", "PNG"), option("bmp", "BMP")] } } },
    ...["contrast", "saturation", "brightness"].map((name) => ({ name, selector: { number: { min: 0, max: 3, step: 0.05, mode: "slider" } } })),
  ]);
  // every knob always has a value, so none offers to clear it (own colours may be empty while typing)
  const required = (items) => items.map((x) => (x.schema ? { ...x, schema: required(x.schema) } : { ...x, required: x.name !== "custom" }));

  const dlg = panel._dialog({
    title: t("display_title", { name: item.name }),
    width: "large",
    footer: false,
    body: `<div class="display">
        <div class="display-knobs"><p class="dlg-text">${esc(t("display_intro"))}</p><ha-form></ha-form></div>
        <div class="display-out">
          <div class="display-preview"><ha-spinner></ha-spinner></div>
          <div class="display-meta"></div>
          <div class="display-params-label">${esc(t("display_params"))}</div>
          <div class="display-params"><code></code>
            <ha-button appearance="plain" size="s" class="display-copy">${esc(t("copy"))}</ha-button></div>
        </div>
      </div>`,
    onClose: () => { clearTimeout(timer); seq++; if (objectUrl) URL.revokeObjectURL(objectUrl); },
  });
  const form = dlg.querySelector("ha-form");
  const preview = dlg.querySelector(".display-preview");
  const meta = dlg.querySelector(".display-meta");
  const code = dlg.querySelector(".display-params code");

  const render = () => {
    form.schema = schema();
    form.data = data;
    code.textContent = `/api/shoebox/image/image.<rotation>?${paramText(deviceParams(data))}`;
  };

  // The preview: the render view with the same options, through a signed URL; the latest change wins
  const update = async () => {
    const mine = ++seq;
    const params = deviceParams(data);
    // cache=0: every knob change is a new picture, which would only push useful ones out of the cache
    const query = new URLSearchParams({ path: item.path, size: `${params.get("width")}x${params.get("height")}`, fit: params.get("fit"), cache: "0" });
    for (const [k, v] of params) if (!["width", "height", "fit"].includes(k)) query.set(k, v);
    try {
      const signed = await panel._hass.callWS({ type: "auth/sign_path", path: `${RENDER_URL}?${query}`, expires: 300 });
      const response = await fetch(signed.path);
      if (mine !== seq) return;
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).message || response.statusText);
      const blob = await response.blob();
      if (mine !== seq) return;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(blob);
      preview.innerHTML = `<img alt="" src="${objectUrl}">`;
      meta.textContent = t("display_file", { type: blob.type || "?", size: sizeText(blob.size), width: params.get("width"), height: params.get("height") });
    } catch (err) {
      if (mine !== seq) return;
      preview.innerHTML = `<ha-alert alert-type="warning">${esc(err.message || err)}</ha-alert>`;
      meta.textContent = "";
    }
  };
  const schedule = () => { clearTimeout(timer); timer = setTimeout(update, DEBOUNCE_MS); };

  form.hass = panel._hass;
  form.computeLabel = (s) => t(s.name === "custom" ? "display_custom_label" : `display_${s.name}`);
  form.addEventListener("value-changed", (e) => {
    const next = { ...data, ...e.detail.value };
    if (next.preset !== data.preset && next.preset !== "custom") {
      data = { ...next, ...presetValues(next.preset) }; // a preset fills every knob
    } else {
      // a knob changed by hand: no longer the preset as it was
      const changed = Object.keys(next).some((k) => k !== "preset" && next[k] !== data[k]);
      data = changed ? { ...next, preset: "custom" } : next;
    }
    render();
    schedule();
  });
  dlg.querySelector(".display-copy").addEventListener("click", async () => {
    const text = `?${paramText(deviceParams(data))}`;
    try {
      await navigator.clipboard.writeText(text);
      panel._toast(t("copied"));
    } catch {
      // no clipboard (plain http): select the text for copying by hand
      const range = document.createRange();
      range.selectNodeContents(code);
      const sel = code.getRootNode().getSelection?.() || window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
  });
  render();
  update();
}
