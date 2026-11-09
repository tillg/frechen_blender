// One headless screenshot of a viewer URL (Claude's own look before a Show link goes to the user):
//   node shot.js <url> <png>
// Waits for the page's first rendered frames (window.__fl / __ofen / __desk / __bad / __kueche ready, as the
// e2e tests do), then saves the page at 1x CSS pixels. GPU flags as in playwright.config.js.
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const [url, png] = process.argv.slice(2);
if (!url || !png) {
  console.error('usage: node shot.js <url> <png>');
  process.exit(2);
}
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.waitForFunction(() => ['__fl', '__ofen', '__desk', '__bad', '__kueche'].some((h) => window[h]?.ready === true),
    null, { timeout: 60_000 });
  // the desk's two screen images load after ready (as desk.spec.js waits for them)
  await page.waitForFunction(() => !window.__desk || window.__desk.textures() === 2, null, { timeout: 60_000 });
  await page.waitForTimeout(500);                       // stage blend and URL view settle
  mkdirSync(dirname(png), { recursive: true });
  await page.screenshot({ path: png, scale: 'css' });
  console.log(png);
} finally {
  await browser.close();
}
