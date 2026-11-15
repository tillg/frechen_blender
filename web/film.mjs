// Captures the viewer's Rundgang frame by frame (25 fps, fake clock: 40 ms per frame, so the fire
// flickers in film time) to tmp/film_web/frame_####.png in full quality (hires=on).
// Usage (from web/): node film.mjs [url] [first] [last]   — `just film` runs it.
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const [url = 'http://localhost:5377/', first = '0', last] = process.argv.slice(2);
const OUT = fileURLToPath(new URL('../tmp/film_web/', import.meta.url));
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('console', (m) => { if (m.type() === 'error') console.log('console:', m.text()); });
await page.clock.install();
// full quality: hires=on switches off the viewer's speed shortcuts (light pool, pixel-ratio cap, no grass indoors)
const u = new URL(url);
u.searchParams.set('hires', 'on');
await page.goto(u.href);
await page.waitForFunction(() => window.__fl?.ready === true, null, { timeout: 120_000 });
const hires = await page.evaluate(() => window.__fl.hires);
if (hires !== true) throw new Error('viewer is not in hires mode: the capture would not be full quality');
await page.getByRole('button', { name: 'Standpunkt', exact: true }).click();          // the route, from the toolbar
await page.getByRole('option', { name: 'Um und durch das Haus', exact: true }).click();
await page.addStyleTag({ content: '.fl-title, .fl-tools, .fl-bar { display: none !important; }' });
const n = await page.evaluate(() => Math.round(window.__fl.tour.duration * 25) + 1);
const end = Math.min(Number(last ?? n - 1), n - 1);
await page.clock.pauseAt(new Date(Date.now() + 60_000));
// the first seek of a run only takes effect a frame later: seek once without a picture, so a run
// that starts mid-route (first > 0, e.g. after a pause) does not begin with the route's start pose
await page.evaluate((t) => window.__fl.tour.seek(t), Number(first) / 25);
await page.clock.runFor(40);
const t0 = Date.now();
for (let i = Number(first); i <= end; i++) {
  await page.evaluate((t) => window.__fl.tour.seek(t), i / 25);
  await page.clock.runFor(40);
  await page.screenshot({ path: `${OUT}frame_${String(i + 1).padStart(4, '0')}.png` });
  if (i % 100 === 0) console.log(`frame ${i + 1}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
}
console.log('done', end + 1, 'of', n);
await browser.close();
