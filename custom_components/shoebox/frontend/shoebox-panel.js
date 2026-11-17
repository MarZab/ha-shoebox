// The admin sidebar panel "Shoebox" of the shoebox component: files and folders below /media
// (thumbnails, upload by drop or picker, rename, move, delete, rotate, crop) and rotations.
// Plain ES modules, no build step. Built from the HA frontend's own elements (ha-top-app-bar-fixed with
// ha-menu-button, ha-card, ha-icon, ha-icon-button, ha-dropdown, ha-dialog, ha-button, ha-input,
// ha-alert, ha-spinner) and HA theme variables only. Those elements are HA internals: check
// the panel after an HA update.
import { translator } from "./i18n.js";
import "./crop.js";

const DOMAIN = "shoebox";
const UPLOAD_URL = "/api/shoebox/upload";
const PARALLEL_UPLOADS = 3;
const NAME_RX = /^[a-z0-9_]+$/;
const ELEMENTS = [
  "ha-top-app-bar-fixed", "ha-menu-button", "ha-card", "ha-icon", "ha-icon-button", "ha-button", "ha-dialog",
  "ha-dialog-footer", "ha-input", "ha-dropdown", "ha-dropdown-item",
  "ha-alert", "ha-spinner",
];
const ASPECTS = [
  ["free", null], ["original", "original"], ["1:1", 1], ["4:3", 4 / 3], ["3:4", 3 / 4], ["16:9", 16 / 9],
  ["9:16", 9 / 16], ["640×800", 640 / 800],
];
const VIDEO = /\.(mp4|m4v|mov|webm|mkv)$/i;
const AUDIO = /\.(mp3|m4a|aac|flac|ogg|oga|opus|wav)$/i;

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const base = (p) => String(p).split("/").pop();
const parent = (p) => (String(p).includes("/") ? String(p).slice(0, String(p).lastIndexOf("/")) : "");
const icon = (name, slot = "") => `<ha-icon ${slot ? `slot="${slot}"` : ""} icon="${name}"></ha-icon>`;
const iconButton = (name, label, attrs = "") =>
  `<ha-icon-button label="${esc(label)}" ${attrs}>${icon(name)}</ha-icon-button>`;
const sizeText = (n) => (n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} kB` : `${(n / 1048576).toFixed(1)} MB`);

const STYLE = `
  :host { display: block; height: 100%; color: var(--primary-text-color); background: var(--primary-background-color);
    font-family: var(--ha-font-family-body, Roboto, sans-serif); -webkit-font-smoothing: var(--ha-font-smoothing, antialiased); }
  .page-title { font-size: inherit; margin: inherit; line-height: inherit; font-weight: inherit; }
  .content { padding: var(--ha-space-4, 16px); max-width: 1600px; margin: 0 auto; box-sizing: border-box; }
  :host([narrow]) .content { padding: var(--ha-space-2, 8px); }
  .crumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 2px; margin: 0 0 var(--ha-space-4, 16px);
    font-size: var(--ha-font-size-l, 16px); color: var(--secondary-text-color); }
  .crumbs a { color: var(--primary-color); text-decoration: none; cursor: pointer; padding: 4px 6px; border-radius: var(--ha-border-radius-sm, 4px); }
  .crumbs a:hover { background: var(--secondary-background-color); }
  .crumbs .here { color: var(--primary-text-color); padding: 4px 6px; font-weight: var(--ha-font-weight-medium, 500); }
  .crumbs ha-icon { --mdc-icon-size: 18px; }
  .count { margin-inline-start: auto; font-size: var(--ha-font-size-s, 12px); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--mm-tile, 160px), 1fr)); gap: var(--ha-space-4, 16px); }
  :host([narrow]) .grid { --mm-tile: 140px; gap: var(--ha-space-2, 8px); }
  .tile { cursor: pointer; content-visibility: auto; contain-intrinsic-size: auto 220px; }
  .tile ha-card { overflow: hidden; height: 100%; transition: box-shadow 0.1s; }
  .tile.drop ha-card { outline: 2px solid var(--primary-color); outline-offset: 2px; }
  .thumb { position: relative; padding-bottom: 100%; background: var(--secondary-background-color); }
  .thumb img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  .thumb ha-icon { position: absolute; inset: 0; margin: auto; width: 40%; height: 40%; display: flex;
    align-items: center; justify-content: center; --mdc-icon-size: 100%; color: var(--secondary-text-color); }
  .thumb ha-icon.folder { color: var(--primary-color); }
  .tile:hover .thumb img { filter: brightness(85%); }
  .label { display: flex; align-items: center; min-height: 48px; padding-inline-start: var(--ha-space-3, 12px); }
  .label .name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: var(--ha-font-size-m, 14px); }
  .empty { padding: var(--ha-space-8, 32px) var(--ha-space-4, 16px); text-align: center; color: var(--secondary-text-color); }
  .center { display: flex; justify-content: center; padding: var(--ha-space-8, 32px); }
  #drop { position: fixed; inset: 0; z-index: 5; display: none; align-items: flex-end; justify-content: center; pointer-events: none;
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08); box-shadow: inset 0 0 0 3px var(--primary-color); }
  #drop.on { display: flex; }
  #drop div { margin-bottom: calc(var(--ha-space-6, 24px) + var(--safe-area-inset-bottom, 0px)); padding: 12px 20px; border-radius: var(--ha-border-radius-pill, 999px);
    background: var(--primary-color); color: var(--text-primary-color); font-weight: var(--ha-font-weight-medium, 500); box-shadow: var(--ha-box-shadow-m, 0 2px 6px rgba(0,0,0,.3)); }
  #uploads { position: fixed; z-index: 4; right: var(--ha-space-4, 16px); bottom: calc(var(--ha-space-4, 16px) + var(--safe-area-inset-bottom, 0px)); width: 360px; max-width: calc(100vw - 32px); }
  :host([narrow]) #uploads { right: 8px; left: 8px; width: auto; max-width: none; }
  #uploads[hidden] { display: none; }
  #uploads ha-card { max-height: 50vh; display: flex; flex-direction: column; }
  .up-head { display: flex; align-items: center; padding: 4px 4px 4px 16px; font-weight: var(--ha-font-weight-medium, 500); border-bottom: 1px solid var(--divider-color); }
  .up-head span { flex: 1; }
  .up-list { overflow: auto; padding: 4px 0; }
  .up { display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; padding: 6px 16px; font-size: var(--ha-font-size-s, 12px); align-items: center; }
  .up .n { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .up ha-icon { --mdc-icon-size: 18px; }
  .up .ok { color: var(--success-color, #43a047); } .up .bad { color: var(--error-color, #db4437); }
  .bar { grid-column: 1 / -1; height: 4px; border-radius: 2px; background: var(--divider-color); overflow: hidden; }
  .bar i { display: block; height: 100%; width: 0; background: var(--primary-color); transition: width 0.2s; }
  .up .err { grid-column: 1 / -1; color: var(--error-color, #db4437); }
  .actions-row { display: flex; gap: var(--ha-space-2, 8px); margin-bottom: var(--ha-space-4, 16px); flex-wrap: wrap; }
  .rot { display: flex; gap: var(--ha-space-4, 16px); padding: var(--ha-space-4, 16px); align-items: center; border-top: 1px solid var(--divider-color); }
  .rot:first-child { border-top: 0; }
  .previews ha-icon { aspect-ratio: 1; display: flex; align-items: center; justify-content: center; color: var(--secondary-text-color); background: var(--secondary-background-color); border-radius: var(--ha-border-radius-sm, 4px); }
  .rot .pic { width: 72px; height: 72px; border-radius: var(--ha-border-radius-md, 8px); object-fit: cover; flex: none;
    background: var(--secondary-background-color); display: flex; align-items: center; justify-content: center; color: var(--secondary-text-color); }
  .rot .txt { flex: 1; min-width: 0; }
  :host([narrow]) .rot { gap: var(--ha-space-2, 8px); padding: var(--ha-space-3, 12px) var(--ha-space-2, 8px); }
  :host([narrow]) .rot .pic { width: 48px; height: 48px; }
  .rot .nm { font-size: var(--ha-font-size-l, 16px); font-weight: var(--ha-font-weight-medium, 500); }
  .rot .sub { color: var(--secondary-text-color); font-size: var(--ha-font-size-s, 12px); overflow-wrap: anywhere; }
  code { font-family: var(--ha-font-family-code, monospace); font-size: 0.95em; background: var(--secondary-background-color); padding: 1px 4px; border-radius: 4px; }
  /* dialogs */
  .dlg-text { margin: 0; color: var(--primary-text-color); }
  .folders { max-height: 50vh; overflow: auto; margin-top: var(--ha-space-2, 8px); }
  .folder-row { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: var(--ha-border-radius-md, 8px); cursor: pointer; }
  .folder-row:hover { background: var(--secondary-background-color); }
  .folder-row.sel { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.15); color: var(--primary-color); }
  .folder-row[disabled] { opacity: 0.4; pointer-events: none; }
  .viewer { display: flex; align-items: center; justify-content: center; min-height: 40vh; position: relative; }
  .viewer img { max-width: 100%; max-height: 70vh; display: block; border-radius: var(--ha-border-radius-sm, 4px); }
  .viewer .nav { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(var(--rgb-card-background-color, 255, 255, 255), 0.6); border-radius: 50%; }
  .viewer .prev { left: 0; } .viewer .next { right: 0; }
  .meta { color: var(--secondary-text-color); font-size: var(--ha-font-size-s, 12px); margin-top: var(--ha-space-2, 8px); text-align: center; overflow-wrap: anywhere; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: var(--ha-space-3, 12px) 0; align-items: center; }
  @media (max-width: 600px) { .chips { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; } .chips > * { flex: none; } }
  .chips .lbl { color: var(--secondary-text-color); font-size: var(--ha-font-size-s, 12px); margin-inline-end: 4px; }
  .patterns { display: flex; flex-direction: column; gap: var(--ha-space-2, 8px); }
  .prow { display: flex; align-items: center; gap: 4px; }
  .prow ha-input { flex: 1; }
  .match { margin-top: var(--ha-space-3, 12px); color: var(--secondary-text-color); }
  .previews { display: grid; grid-template-columns: repeat(auto-fill, minmax(72px, 1fr)); gap: 6px; margin-top: var(--ha-space-2, 8px); }
  .previews img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: var(--ha-border-radius-sm, 4px); background: var(--secondary-background-color); }
  ha-input { display: block; }
  [hidden] { display: none !important; }
`;

class ShoeboxPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._folder = "";
    this._view = "files";
    this._items = [];
    this._uploads = [];
    this._dragDepth = 0;
    this.shadowRoot.addEventListener("click", (e) => this._click(e));
    // a picture that cannot be shown (file gone, unreadable): an icon instead of the browser's broken image
    this.shadowRoot.addEventListener("error", (e) => {
      const img = e.target;
      if (img?.tagName !== "IMG" || img.closest?.("shoebox-crop")) return;
      const ic = document.createElement("ha-icon");
      ic.icon = "mdi:image-broken-variant";
      ic.className = img.className;
      ic.title = img.title;
      img.replaceWith(ic);
    }, true);
  }

  // ------------------------------------------------------------------ properties set by HA

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) this._start();
    else if (this._lang !== (hass.locale?.language || hass.language)) this._renderShell();
  }

  get hass() { return this._hass; }

  set narrow(v) {
    this._narrow = !!v;
    this.toggleAttribute("narrow", this._narrow);
    const bar = this.shadowRoot.querySelector("ha-top-app-bar-fixed");
    if (bar) bar.narrow = this._narrow;
  }

  set route(route) {
    this._route = route;
    if (this._ready) this._applyRoute();
  }

  set panel(p) { this._panel = p; }

  // ------------------------------------------------------------------ start, shell, routing

  async _start() {
    // HA loads its elements lazily; wait for those used here (they are normally there within moments)
    await Promise.race([
      Promise.all(ELEMENTS.map((n) => customElements.whenDefined(n))),
      new Promise((r) => setTimeout(r, 5000)),
    ]);
    this._renderShell();
    this._bindDrop();
    this._ready = true;
    this._applyRoute();
  }

  _renderShell() {
    this.t = translator(this._hass);
    this._lang = this._hass.locale?.language || this._hass.language;
    const t = this.t;
    this.shadowRoot.innerHTML = `<style>${STYLE}</style>
      <ha-top-app-bar-fixed>
        <h1 class="page-title" slot="title">${esc(t("title"))}</h1>
        ${iconButton("mdi:image-multiple-outline", t("rotations"), 'slot="actionItems" data-act="toggle-view" id="toggle"')}
        ${iconButton("mdi:folder-plus-outline", t("new_folder"), 'slot="actionItems" data-act="new-folder" class="files-only"')}
        ${iconButton("mdi:upload", t("upload"), 'slot="actionItems" data-act="upload" class="files-only"')}
        ${iconButton("mdi:refresh", t("refresh"), 'slot="actionItems" data-act="refresh"')}
        <div class="content" id="content"></div>
      </ha-top-app-bar-fixed>
      <input type="file" id="picker" multiple accept="image/*,video/*,audio/*" hidden>
      <div id="drop"><div></div></div>
      <div id="uploads" hidden></div>`;
    const bar = this.shadowRoot.querySelector("ha-top-app-bar-fixed");
    bar.narrow = !!this._narrow;
    this.shadowRoot.getElementById("picker").addEventListener("change", (e) => {
      this._upload([...e.target.files], this._folder);
      e.target.value = "";
    });
    if (this._ready) this._applyRoute(true);
  }

  _applyRoute(force = false) {
    const path = (this._route?.path || "").replace(/^\/+/, "");
    let view = "files", folder = "";
    if (path === "rotations") { view = "rotations"; folder = this._folder || ""; }  // back to the same folder
    else if (path.startsWith("folder/")) folder = path.slice(7).split("/").map(decodeURIComponent).join("/");
    if (!force && view === this._view && folder === this._folder && this._loadedOnce) return;
    this._view = view;
    this._folder = folder;
    this._loadedOnce = true;
    // the toggle shows where it leads: rotations from the files, the files from the rotations
    const toggle = this.shadowRoot.getElementById("toggle");
    const to = view === "files" ? ["mdi:image-multiple-outline", "rotations"] : ["mdi:folder-multiple-image", "files"];
    toggle.setAttribute("label", this.t(to[1]));
    toggle.innerHTML = icon(to[0]);
    this.shadowRoot.querySelectorAll(".files-only").forEach((el) => { el.hidden = view !== "files"; });
    if (view === "rotations") this._loadRotations();
    else this._loadFolder();
  }

  _navigate(view, folder = "") {
    const prefix = this._route?.prefix || "/shoebox";
    let path = prefix;
    if (view === "rotations") path += "/rotations";
    else if (folder) path += "/folder/" + folder.split("/").map(encodeURIComponent).join("/");
    history.pushState(null, "", path);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }

  // ------------------------------------------------------------------ backend

  _ws(type, data = {}) { return this._hass.callWS({ type: `${DOMAIN}/${type}`, ...data }); }

  async _action(service, data) {
    const r = await this._hass.callWS({ type: "call_service", domain: DOMAIN, service, service_data: data, return_response: true });
    return r?.response;
  }

  _toast(message) {
    this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message }, bubbles: true, composed: true }));
  }

  _error(err) { this._toast(this.t("error", { message: err?.message || err?.body?.message || String(err) })); }

  // ------------------------------------------------------------------ clicks

  _click(e) {
    const path = e.composedPath();
    const el = (sel) => path.find((n) => n instanceof Element && n.matches?.(sel));
    if (el("ha-dropdown")) return; // menus handle their own selection
    const act = el("[data-act]");
    if (act) {
      const a = act.dataset.act;
      if (a === "upload") this.shadowRoot.getElementById("picker").click();
      else if (a === "toggle-view") this._view === "files" ? this._navigate("rotations") : this._navigate("files", this._folder);
      else if (a === "new-folder") this._newFolder();
      else if (a === "refresh") this._view === "rotations" ? this._loadRotations() : this._loadFolder();
      else if (a === "crumb") this._navigate("files", act.dataset.path);
      else if (a === "add-rotation") this._editRotation(null);
      else if (a === "edit-rotation") this._editRotation(this._rotations.find((r) => r.name === act.dataset.name));
      else if (a === "delete-rotation") this._deleteRotation(act.dataset.name);
      else if (a === "close-uploads") this._closeUploads();
      return;
    }
    const tile = el(".tile");
    if (tile) {
      const item = this._items[Number(tile.dataset.i)];
      if (item.type === "folder") this._navigate("files", item.path);
      else if (item.type === "image") this._openViewer(item);
    }
  }

  _menu(e, item) {
    const v = e.detail?.item?.value;
    if (v === "open") item.type === "folder" ? this._navigate("files", item.path) : this._openViewer(item);
    else if (v === "rename") this._rename(item);
    else if (v === "move") this._move(item);
    else if (v === "delete") this._delete(item);
  }

  // ------------------------------------------------------------------ files

  async _loadFolder() {
    const content = this.shadowRoot.getElementById("content");
    if (!this._items.length || this._shownFolder !== this._folder) content.innerHTML = `<div class="center"><ha-spinner></ha-spinner></div>`;
    try {
      const r = await this._ws("browse", { path: this._folder });
      this._items = r.items;
      this._shownFolder = r.path;
      this._renderFolder();
    } catch (err) {
      content.innerHTML = `<ha-alert alert-type="error">${esc(err.message || err)}</ha-alert>
        <div class="crumbs"><a data-act="crumb" data-path="">${icon("mdi:folder-home")} ${esc(this.t("media"))}</a></div>`;
    }
  }

  _renderFolder() {
    const t = this.t;
    const parts = this._folder ? this._folder.split("/") : [];
    const crumbs = [`<a data-act="crumb" data-path="">${icon("mdi:folder-home-outline")}&nbsp;${esc(t("media"))}</a>`];
    parts.forEach((p, i) => {
      const path = parts.slice(0, i + 1).join("/");
      crumbs.push(icon("mdi:chevron-right"));
      crumbs.push(i === parts.length - 1 ? `<span class="here">${esc(p)}</span>` : `<a data-act="crumb" data-path="${esc(path)}">${esc(p)}</a>`);
    });
    const tiles = this._items.map((it, i) => {
      let thumb;
      if (it.type === "folder") thumb = `<ha-icon class="folder" icon="mdi:folder"></ha-icon>`;
      else if (it.type === "image") thumb = `<img loading="lazy" decoding="async" alt="" src="${esc(it.thumb)}">`;
      else thumb = `<ha-icon icon="${VIDEO.test(it.name) ? "mdi:file-video-outline" : AUDIO.test(it.name) ? "mdi:file-music-outline" : "mdi:file-outline"}"></ha-icon>`;
      return `<div class="tile" data-i="${i}" ${it.type === "folder" ? `data-folder="${esc(it.path)}"` : ""} title="${esc(it.name)}${it.type !== "folder" ? ` · ${sizeText(it.size)}` : ""}">
        <ha-card outlined><div class="thumb">${thumb}</div>
          <div class="label"><span class="name">${esc(it.name)}</span>
            <ha-dropdown data-i="${i}" placement="bottom-end">
              ${iconButton("mdi:dots-vertical", t("menu"), 'slot="trigger"')}
              ${it.type !== "file" ? `<ha-dropdown-item value="open">${icon(it.type === "folder" ? "mdi:folder-open-outline" : "mdi:image-outline", "icon")}${esc(t("open"))}</ha-dropdown-item>` : ""}
              <ha-dropdown-item value="rename">${icon("mdi:rename-outline", "icon")}${esc(t("rename"))}</ha-dropdown-item>
              <ha-dropdown-item value="move">${icon("mdi:folder-move-outline", "icon")}${esc(t("move"))}</ha-dropdown-item>
              <ha-dropdown-item value="delete" variant="danger">${icon("mdi:delete-outline", "icon")}${esc(t("delete"))}</ha-dropdown-item>
            </ha-dropdown></div></ha-card></div>`;
    });
    const content = this.shadowRoot.getElementById("content");
    content.innerHTML = `<div class="crumbs">${crumbs.join("")}<span class="count">${esc(t("pictures", { count: this._items.length }))}</span></div>
      ${this._items.length ? `<div class="grid">${tiles.join("")}</div>` : `<ha-card outlined><div class="empty">${icon("mdi:image-plus-outline")}<p>${esc(t("empty"))}</p></div></ha-card>`}`;
    content.querySelectorAll("ha-dropdown").forEach((dd) => {
      dd.addEventListener("wa-select", (e) => this._menu(e, this._items[Number(dd.dataset.i)]));
    });
  }

  _newFolder() {
    const t = this.t;
    this._prompt(t("new_folder"), t("folder_name"), "", t("create"), async (name) => {
      const path = this._folder ? `${this._folder}/${name}` : name;
      await this._action("create_folder", { path });
      await this._loadFolder();
    });
  }

  _rename(item, after) {
    const t = this.t;
    this._prompt(t("rename"), t("new_name"), item.name, t("rename"), async (name) => {
      if (name === item.name) return;
      const r = await this._action("rename", { path: item.path, name });
      await this._loadFolder();
      after?.(r?.path);
    }, item.type !== "folder");
  }

  async _move(item, after) {
    const t = this.t;
    let folders;
    try { folders = (await this._ws("folders")).folders; } catch (err) { this._error(err); return; }
    const all = ["", ...folders];
    const from = parent(item.path);
    let selected = null;
    const rows = (filter) => all
      .filter((f) => !filter || f.toLowerCase().includes(filter.toLowerCase()))
      .map((f) => {
        const off = f === from || (item.type === "folder" && (f === item.path || f.startsWith(item.path + "/")));
        return `<div class="folder-row ${f === selected ? "sel" : ""}" data-f="${esc(f)}" ${off ? "disabled" : ""}>
          ${icon(f ? "mdi:folder-outline" : "mdi:folder-home-outline")}<span>${esc(f || t("media"))}</span></div>`;
      }).join("");
    const dlg = this._dialog({
      title: t("move_title", { name: item.name }),
      body: `<ha-input with-clear label="${esc(t("filter_folders"))}" id="filter"></ha-input><div class="folders">${rows("")}</div>`,
      primary: t("move_to"),
      onPrimary: async () => {
        if (selected === null) return false;
        await this._action("move", { path: item.path, to: selected });
        await this._loadFolder();
        after?.(selected ? `${selected}/${item.name}` : item.name);
        return true;
      },
    });
    const list = dlg.querySelector(".folders");
    dlg.querySelector("#filter").addEventListener("input", (e) => { list.innerHTML = rows(e.target.value || ""); });
    list.addEventListener("click", (e) => {
      const row = e.target.closest(".folder-row");
      if (!row) return;
      selected = row.dataset.f;
      list.querySelectorAll(".folder-row").forEach((r) => r.classList.toggle("sel", r === row));
    });
  }

  _delete(item, after) {
    const t = this.t;
    this._dialog({
      title: t("delete_title", { name: item.name }),
      type: "alert",
      width: "small",
      body: `<p class="dlg-text">${esc(item.type === "folder" ? t("delete_folder") : t("delete_file"))}</p>`,
      primary: t("delete"),
      danger: true,
      onPrimary: async () => {
        await this._action("delete", { path: item.path });
        await this._loadFolder();
        after?.();
        return true;
      },
    });
  }

  // ------------------------------------------------------------------ dialogs (ha-dialog)

  // A dialog in HA's style. onPrimary returns false to stay open; errors are shown in the dialog.
  _dialog({ title, body, primary, danger = false, onPrimary, width = "medium", type = "standard", header = "", footer = true, onClose }) {
    const t = this.t;
    const dlg = document.createElement("ha-dialog");
    dlg.headerTitle = title;
    dlg.setAttribute("width", width);
    dlg.type = type;
    dlg.innerHTML = `${header}<ha-alert alert-type="error" class="dlg-error" hidden></ha-alert>${body}
      ${footer ? `<ha-dialog-footer slot="footer">
        <ha-button slot="secondaryAction" appearance="plain" data-dlg="cancel">${esc(t("cancel"))}</ha-button>
        ${primary ? `<ha-button slot="primaryAction" ${danger ? 'variant="danger"' : ""} data-dlg="ok">${esc(primary)}</ha-button>` : ""}
      </ha-dialog-footer>` : ""}`;
    const close = () => { dlg.open = false; };
    dlg.addEventListener("closed", (e) => { if (e.target === dlg) { dlg.remove(); onClose?.(); } });
    const ok = async () => {
      const btn = dlg.querySelector('[data-dlg="ok"]');
      if (btn?.loading) return;
      const errBox = dlg.querySelector(".dlg-error");
      errBox.hidden = true;
      if (btn) btn.loading = true;
      try {
        if ((await onPrimary?.()) !== false) close();
      } catch (err) {
        errBox.textContent = err?.message || String(err);
        errBox.hidden = false;
      } finally {
        if (btn) btn.loading = false;
      }
    };
    dlg.addEventListener("click", (e) => {
      const b = e.target.closest?.("[data-dlg]");
      if (b?.dataset.dlg === "cancel") close();
      else if (b?.dataset.dlg === "ok") ok();
    });
    dlg.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target.closest?.("ha-input") && dlg.querySelector('[data-dlg="ok"]')) { e.preventDefault(); ok(); }
    });
    dlg.close = close;
    dlg.submit = ok;
    this.shadowRoot.appendChild(dlg);
    requestAnimationFrame(() => { dlg.open = true; });
    return dlg;
  }

  _prompt(title, label, value, primary, onValue, selectStem = false) {
    const dlg = this._dialog({
      title,
      width: "small",
      body: `<ha-input autofocus label="${esc(label)}" id="value"></ha-input>`,
      primary,
      onPrimary: async () => {
        const v = String(dlg.querySelector("#value").value || "").trim();
        if (!v) return false;
        await onValue(v);
        return true;
      },
    });
    const input = dlg.querySelector("#value");
    input.value = value;
    if (selectStem && value.includes(".")) {
      dlg.addEventListener("after-show", () => {
        const native = input.shadowRoot?.querySelector("wa-input")?.shadowRoot?.querySelector("input")
          || input.shadowRoot?.querySelector("input");
        native?.setSelectionRange?.(0, value.lastIndexOf("."));
      });
    }
  }

  // ------------------------------------------------------------------ viewer and editor

  async _openViewer(item) {
    const t = this.t;
    const images = () => this._items.filter((i) => i.type === "image");
    let current = item;
    let info = null;
    let cropMode = false;
    let aspect = null;
    const header = `
      ${iconButton("mdi:rotate-left", t("rotate_left"), 'slot="headerActionItems" data-v="left" class="ed"')}
      ${iconButton("mdi:rotate-right", t("rotate_right"), 'slot="headerActionItems" data-v="right" class="ed"')}
      ${iconButton("mdi:crop", t("crop"), 'slot="headerActionItems" data-v="crop" class="ed"')}
      <ha-dropdown slot="headerActionItems" placement="bottom-end" id="more">
        ${iconButton("mdi:dots-vertical", t("menu"), 'slot="trigger"')}
        <ha-dropdown-item value="rename">${icon("mdi:rename-outline", "icon")}${esc(t("rename"))}</ha-dropdown-item>
        <ha-dropdown-item value="move">${icon("mdi:folder-move-outline", "icon")}${esc(t("move"))}</ha-dropdown-item>
        <ha-dropdown-item value="delete" variant="danger">${icon("mdi:delete-outline", "icon")}${esc(t("delete"))}</ha-dropdown-item>
      </ha-dropdown>`;
    const dlg = this._dialog({ title: item.name, width: "large", header, body: `<div id="body"></div>`, footer: false });
    const body = dlg.querySelector("#body");

    const setButtons = () => {
      dlg.querySelectorAll(".ed").forEach((b) => { b.disabled = !info?.editable || cropMode; });
    };
    const load = async (it) => {
      current = it;
      dlg.headerTitle = it.name;
      cropMode = false;
      body.innerHTML = `<div class="center"><ha-spinner></ha-spinner></div>`;
      try {
        info = await this._ws("info", { path: it.path });
      } catch (err) {
        body.innerHTML = `<ha-alert alert-type="error">${esc(err.message)}</ha-alert>`;
        return;
      }
      showView();
    };
    const showView = () => {
      cropMode = false;
      dlg.querySelector(".crop-footer")?.remove();
      setButtons();
      const list = images();
      const idx = list.findIndex((i) => i.path === current.path);
      body.innerHTML = `<div class="viewer">
          <img alt="${esc(current.name)}" src="${esc(info.view)}">
          ${idx > 0 ? iconButton("mdi:chevron-left", t("previous"), 'class="nav prev" data-v="prev"') : ""}
          ${idx >= 0 && idx < list.length - 1 ? iconButton("mdi:chevron-right", t("next"), 'class="nav next" data-v="next"') : ""}
        </div>
        <div class="meta">${esc(current.path)} · ${info.width} × ${info.height} · ${esc(info.format || "")}${current.size ? ` · ${sizeText(current.size)}` : ""}</div>`;
    };
    const showCrop = () => {
      cropMode = true;
      setButtons();
      aspect = null;
      body.innerHTML = `<div class="chips"><span class="lbl">${esc(t("aspect"))}</span>
          ${ASPECTS.map(([k]) => `<ha-button size="small" appearance="${k === "free" ? "filled" : "plain"}" data-aspect="${k}">${esc(k === "free" ? t("free") : k === "original" ? t("original") : k)}</ha-button>`).join("")}
        </div><shoebox-crop></shoebox-crop>`;
      const footer = document.createElement("ha-dialog-footer");
      footer.slot = "footer";
      footer.className = "crop-footer";
      footer.innerHTML = `
          <ha-button slot="secondaryAction" appearance="plain" data-v="reset" title="${esc(t("reset_hint"))}">${icon("mdi:restore", "start")}${esc(t("reset"))}</ha-button>
          <ha-button slot="secondaryAction" appearance="plain" data-v="cancel-crop">${esc(t("cancel"))}</ha-button>
          <ha-button slot="primaryAction" data-v="save-crop">${esc(t("save"))}</ha-button>`;
      dlg.appendChild(footer);
      const crop = body.querySelector("shoebox-crop");
      crop.label = t("preview");
      crop.src = info.base;
      crop.box = info.crop;
    };
    const save = async (data) => {
      try {
        info = await this._ws("edit", { path: current.path, ...data });
        showView();
        this._refreshThumb(current.path);
      } catch (err) { this._error(err); }
    };

    dlg.addEventListener("click", async (e) => {
      const b = e.composedPath().find((n) => n instanceof Element && (n.dataset?.v || n.dataset?.aspect));
      if (!b || b.disabled) return;
      const v = b.dataset.v;
      const list = images();
      const idx = list.findIndex((i) => i.path === current.path);
      if (v === "left" || v === "right") await save({ rotate: v === "left" ? -90 : 90, crop: info.crop });
      else if (v === "crop") showCrop();
      else if (v === "cancel-crop") showView();
      else if (v === "prev" && idx > 0) load(list[idx - 1]);
      else if (v === "next" && idx < list.length - 1) load(list[idx + 1]);
      else if (v === "reset") await save({ crop: null });  // only the crop; turning stays as set
      else if (v === "save-crop") {
        const box = body.querySelector("shoebox-crop").box;
        const whole = !box || (box[0] < 0.001 && box[1] < 0.001 && box[2] > 0.999 && box[3] > 0.999);
        await save({ crop: whole ? null : box.map((x) => Math.min(Math.max(x, 0), 1)) });
      } else if (b.dataset.aspect) {
        const crop = body.querySelector("shoebox-crop");
        body.querySelectorAll("[data-aspect]").forEach((x) => x.setAttribute("appearance", x === b ? "filled" : "plain"));
        const a = ASPECTS.find(([k]) => k === b.dataset.aspect)[1];
        const [w, h] = crop.natural;
        aspect = a === "original" ? w / h : a;
        crop.aspect = aspect;
      }
    });
    dlg.addEventListener("keydown", (e) => {
      if (cropMode || e.target.closest?.("ha-input")) return;
      const list = images();
      const idx = list.findIndex((i) => i.path === current.path);
      if (e.key === "ArrowLeft" && idx > 0) load(list[idx - 1]);
      if (e.key === "ArrowRight" && idx >= 0 && idx < list.length - 1) load(list[idx + 1]);
    });
    dlg.querySelector("#more").addEventListener("wa-select", (e) => {
      const v = e.detail?.item?.value;
      const it = { ...current, type: "image" };
      if (v === "rename") this._rename(it, (p) => p && load({ ...current, path: p, name: base(p) }));
      else if (v === "move") this._move(it, () => dlg.close());
      else if (v === "delete") this._delete(it, () => dlg.close());
    });
    load(item);
  }

  _refreshThumb(path) {
    // the file changed (its mtime is part of the variant key): list the folder again for new thumbnails
    clearTimeout(this._refreshTimer);
    this._refreshTimer = setTimeout(() => this._view === "files" && this._loadFolder(), 300);
  }

  // ------------------------------------------------------------------ upload

  _bindDrop() {
    const hasFiles = (e) => [...(e.dataTransfer?.types || [])].includes("Files");
    const overlay = () => this.shadowRoot.getElementById("drop");
    const tileOf = (e) => e.composedPath().find((n) => n instanceof Element && n.classList?.contains("tile") && n.dataset.folder !== undefined);
    const mark = (tile) => {
      this.shadowRoot.querySelectorAll(".tile.drop").forEach((x) => x !== tile && x.classList.remove("drop"));
      tile?.classList.add("drop");
      const target = tile ? tile.dataset.folder : this._folder;
      const o = overlay();
      if (!o) return;
      o.querySelector("div").textContent = this.t("drop_here", { folder: target ? `/media/${target}` : "/media" });
      o.classList.add("on");
    };
    const clear = () => {
      this._dragDepth = 0;
      overlay()?.classList.remove("on");
      this.shadowRoot.querySelectorAll(".tile.drop").forEach((x) => x.classList.remove("drop"));
    };
    this.addEventListener("dragenter", (e) => {
      if (!hasFiles(e) || this._view !== "files") return;
      e.preventDefault();
      this._dragDepth++;
      mark(tileOf(e));
    });
    this.addEventListener("dragover", (e) => {
      if (!hasFiles(e) || this._view !== "files") return;
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
      mark(tileOf(e));
    });
    this.addEventListener("dragleave", (e) => {
      if (!hasFiles(e)) return;
      if (--this._dragDepth <= 0) clear();
    });
    this.addEventListener("drop", (e) => {
      if (!hasFiles(e) || this._view !== "files") return;
      e.preventDefault();
      const tile = tileOf(e);
      const folder = tile ? tile.dataset.folder : this._folder;
      clear();
      this._upload([...e.dataTransfer.files], folder);
    });
  }

  _upload(files, folder) {
    if (!files.length) return;
    if (this._uploads.length && this._uploads.every((u) => u.state !== "busy" && u.state !== "wait")) this._uploads = [];
    for (const file of files) this._uploads.push({ file, folder, state: "wait", progress: 0, error: "" });
    this._renderUploads();
    this._pump();
  }

  _pump() {
    while (this._uploads.filter((u) => u.state === "busy").length < PARALLEL_UPLOADS) {
      const next = this._uploads.find((u) => u.state === "wait");
      if (!next) break;
      next.state = "busy";
      this._send(next).finally(() => { this._renderUploads(); this._pump(); this._afterUpload(next); });
    }
    // all done without errors: the list goes away by itself after a moment (errors stay until closed)
    clearTimeout(this._hideTimer);
    if (this._uploads.length && this._uploads.every((u) => u.state === "done")) {
      this._hideTimer = setTimeout(() => {
        if (this._uploads.every((u) => u.state === "done")) this._closeUploads();
      }, 4000);
    }
  }

  async _send(u) {
    const auth = this._hass.auth;
    try {
      if (auth?.expired && auth.refreshAccessToken) await auth.refreshAccessToken();
    } catch (err) { /* the request below reports it */ }
    const token = auth?.accessToken || auth?.data?.access_token;
    await new Promise((resolve) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${UPLOAD_URL}?folder=${encodeURIComponent(u.folder)}`);
      if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) { u.progress = e.loaded / e.total; this._renderUpload(u); }
      };
      xhr.onload = () => {
        let body = {};
        try { body = JSON.parse(xhr.responseText); } catch (err) { /* not JSON */ }
        if (xhr.status === 200) { u.state = "done"; u.progress = 1; u.path = body.path; }
        else { u.state = "error"; u.error = body.message || `HTTP ${xhr.status}`; }
        resolve();
      };
      xhr.onerror = () => { u.state = "error"; u.error = "network error"; resolve(); };
      const form = new FormData();
      form.append("file", u.file, u.file.name);
      xhr.send(form);
    });
  }

  _afterUpload(u) {
    if (u.state === "done" && this._view === "files" && (u.folder === this._folder || parent(u.folder) === this._folder)) {
      clearTimeout(this._reloadTimer);
      this._reloadTimer = setTimeout(() => this._loadFolder(), 400);
    }
  }

  _renderUploads() {
    const box = this.shadowRoot.getElementById("uploads");
    if (!box) return;
    const t = this.t;
    const total = this._uploads.length;
    if (!total) { box.hidden = true; return; }
    const done = this._uploads.filter((u) => u.state === "done").length;
    const busy = this._uploads.some((u) => u.state === "busy" || u.state === "wait");
    box.hidden = false;
    box.innerHTML = `<ha-card raised><div class="up-head"><span>${esc(t(busy ? "uploading" : "uploaded", { done, total }))}</span>
        ${busy ? "" : iconButton("mdi:close", t("close"), 'data-act="close-uploads"')}</div>
      <div class="up-list">${this._uploads.map((u, i) => `<div class="up" data-u="${i}">
        <span class="n" title="${esc(u.folder ? `${u.folder}/${u.file.name}` : u.file.name)}">${esc(u.path ? base(u.path) : u.file.name)}</span>
        <span class="s">${u.state === "done" ? `<ha-icon class="ok" icon="mdi:check-circle"></ha-icon>` : u.state === "error" ? `<ha-icon class="bad" icon="mdi:alert-circle"></ha-icon>` : `${Math.round(u.progress * 100)} %`}</span>
        ${u.state === "error" ? `<span class="err">${esc(u.error)}</span>` : `<span class="bar"><i style="width:${Math.round(u.progress * 100)}%"></i></span>`}
      </div>`).join("")}</div></ha-card>`;
  }

  _renderUpload(u) {
    const row = this.shadowRoot.querySelector(`.up[data-u="${this._uploads.indexOf(u)}"]`);
    if (!row) return;
    row.querySelector(".s").textContent = `${Math.round(u.progress * 100)} %`;
    const bar = row.querySelector(".bar i");
    if (bar) bar.style.width = `${Math.round(u.progress * 100)}%`;
  }

  _closeUploads() { this._uploads = []; this._renderUploads(); }

  // ------------------------------------------------------------------ rotations

  async _loadRotations() {
    const t = this.t;
    const content = this.shadowRoot.getElementById("content");
    content.innerHTML = `<div class="center"><ha-spinner></ha-spinner></div>`;
    try {
      this._rotations = (await this._ws("rotations")).rotations;
    } catch (err) {
      content.innerHTML = `<ha-alert alert-type="error">${esc(err.message)}</ha-alert>`;
      return;
    }
    const rows = this._rotations.map((r) => `<div class="rot">
        ${r.thumb ? `<img class="pic" alt="" src="${esc(r.thumb)}">` : `<div class="pic">${icon("mdi:image-off-outline")}</div>`}
        <div class="txt"><div class="nm">${esc(r.name)}</div>
          <div class="sub">${r.patterns.map((p) => `<code>${esc(p)}</code>`).join(" → ")}</div>
          <div class="sub">${esc(r.position ? t("position", { position: r.position, count: r.count }) : t("not_started", { count: r.count }))} · ${esc(t("entity", { entity: `image.${r.name}` }))}</div>
          ${r.file ? `<div class="sub">${esc(t("current", { file: r.file }))}</div>` : ""}</div>
        ${iconButton("mdi:pencil", t("edit_rotation"), `data-act="edit-rotation" data-name="${esc(r.name)}"`)}
        ${iconButton("mdi:delete-outline", t("delete"), `data-act="delete-rotation" data-name="${esc(r.name)}"`)}
      </div>`).join("");
    content.innerHTML = `<div class="actions-row"><ha-button data-act="add-rotation">${icon("mdi:plus", "start")}${esc(t("add_rotation"))}</ha-button></div>
      <ha-card outlined>${rows || `<div class="empty">${esc(t("no_rotations"))}</div>`}</ha-card>`;
  }

  _editRotation(rot) {
    const t = this.t;
    let patterns = rot ? [...rot.patterns] : [""];
    const patternRows = () => patterns.map((p, i) => `<div class="prow">
        <ha-input data-p="${i}" label="${esc(i ? t("fallback") : t("pattern"))}" ${i ? "" : `hint="${esc(t("pattern_hint"))}"`}></ha-input>
        ${patterns.length > 1 ? iconButton("mdi:close", t("remove_pattern"), `data-rm="${i}"`) : ""}</div>`).join("");
    const dlg = this._dialog({
      title: rot ? t("edit_rotation") : t("add_rotation"),
      body: `<ha-input id="name" label="${esc(t("rotation_name"))}" ${rot ? "" : "autofocus"}></ha-input>
        <div class="patterns"></div>
        <div class="actions-row" style="margin:8px 0 0"><ha-button appearance="plain" size="small" data-add>${icon("mdi:plus", "start")}${esc(t("add_pattern"))}</ha-button></div>
        <div class="match"></div><div class="previews"></div>`,
      primary: t("save"),
      onPrimary: async () => {
        const name = String(dlg.querySelector("#name").value || "").trim();
        const pats = patterns.map((p) => p.trim()).filter(Boolean);
        if (!NAME_RX.test(name)) throw new Error(t("invalid_name"));
        if (!pats.length) return false;
        if (rot && name !== rot.name) await this._action("rename_rotation", { rotation: rot.name, name });
        await this._action("set_rotation", { rotation: name, pattern: pats });
        await this._loadRotations();
        return true;
      },
    });
    const list = dlg.querySelector(".patterns");
    const fill = () => {
      list.innerHTML = patternRows();
      list.querySelectorAll("ha-input").forEach((inp) => { inp.value = patterns[Number(inp.dataset.p)]; });
    };
    fill();
    dlg.querySelector("#name").value = rot?.name || "";
    let timer;
    let seq = 0;
    const update = () => {
      clearTimeout(timer);
      timer = setTimeout(async () => {
        const my = ++seq;
        const match = dlg.querySelector(".match"), previews = dlg.querySelector(".previews");
        const pats = patterns.map((p) => p.trim()).filter(Boolean);
        if (!pats.length) { match.textContent = ""; previews.innerHTML = ""; return; }
        try {
          const r = await this._ws("match", { pattern: pats, limit: 24 });
          if (my !== seq) return;
          match.innerHTML = r.count
            ? esc(pats.length > 1 ? t("matches_with", { count: r.count, pattern: r.pattern }) : t("matches", { count: r.count }))
            : esc(t("no_matches"));
          previews.innerHTML = r.items.map((i) => `<img loading="lazy" alt="" title="${esc(i.path)}" src="${esc(i.thumb)}">`).join("");
        } catch (err) {
          if (my !== seq) return;
          match.innerHTML = `<ha-alert alert-type="warning">${esc(err.message)}</ha-alert>`;
          previews.innerHTML = "";
        }
      }, 300);
    };
    list.addEventListener("input", (e) => {
      const inp = e.composedPath().find((n) => n.dataset?.p !== undefined);
      if (!inp) return;
      patterns[Number(inp.dataset.p)] = inp.value || "";
      update();
    });
    dlg.addEventListener("click", (e) => {
      const b = e.composedPath().find((n) => n instanceof Element && (n.dataset?.rm !== undefined || n.hasAttribute?.("data-add")));
      if (!b) return;
      if (b.hasAttribute("data-add")) patterns.push("");
      else patterns.splice(Number(b.dataset.rm), 1);
      fill();
      update();
    });
    update();
  }

  _deleteRotation(name) {
    const t = this.t;
    this._dialog({
      title: t("delete_rotation", { name }),
      type: "alert",
      width: "small",
      body: `<p class="dlg-text">${esc(t("delete_rotation_text"))}</p>`,
      primary: t("delete"),
      danger: true,
      onPrimary: async () => {
        await this._action("remove_rotation", { rotation: name });
        await this._loadRotations();
        return true;
      },
    });
  }
}

if (!customElements.get("shoebox-panel")) customElements.define("shoebox-panel", ShoeboxPanel);
