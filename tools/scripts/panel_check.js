// Opens the Shoebox panel of the dev Home Assistant in Chromium (light, dark, phone width),
// fails on a missing Home Assistant element or a console error, and saves screenshots.
// Usage: panel_check.js <screenshot folder>   (run through `mise run dev:panel`)
const { chromium } = require("playwright");
const fs = require("fs");

const BASE = process.env.HA_URL || "http://localhost:8123";
const OUT = process.argv[2] || "docker/screenshots";
const PANEL = fs.readFileSync("custom_components/shoebox/frontend/shoebox-panel.js", "utf8");
const ELEMENTS = [...new Set(PANEL.match(/"(ha-[a-z-]+)"/g).map((s) => s.slice(1, -1)))];
const RUNS = [
  { name: "light", viewport: { width: 1280, height: 800 }, colorScheme: "light" },
  { name: "dark", viewport: { width: 1280, height: 800 }, colorScheme: "dark" },
  { name: "phone", viewport: { width: 390, height: 844 }, colorScheme: "light" },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  let failed = false;
  for (const run of RUNS) {
    const context = await browser.newContext({ viewport: run.viewport, colorScheme: run.colorScheme });
    const page = await context.newPage();
    const errors = [];
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.goto(`${BASE}/shoebox`);
    await page.fill('input[name="username"]', "dev");
    await page.fill('input[name="password"]', "dev");
    await page.keyboard.press("Enter");
    await page.waitForSelector("shoebox-panel", { timeout: 30000 });
    await page.waitForTimeout(3000);
    const missing = await page.evaluate((names) => names.filter((n) => !customElements.get(n)), ELEMENTS);
    await page.screenshot({ path: `${OUT}/${run.name}.png` });
    const ok = !missing.length && !errors.length;
    failed ||= !ok;
    console.log(`${ok ? "ok  " : "FAIL"} ${run.name}`, missing.length ? `missing ${missing}` : "", errors.join(" | "));
    await context.close();
  }
  await browser.close();
  console.log(`screenshots in ${OUT}`);
  process.exit(failed ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
