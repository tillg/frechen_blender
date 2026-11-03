import { test, expect } from '@playwright/test';
import { shot } from './pixels.js';

async function open(page) {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
}

const stage = (page) => page.evaluate(() => document.body.dataset.stage);
const vis = (page, name) => page.evaluate((n) => window.__fl.visible(n), name);

test('clicking "Detailmodell" selects the detail stage', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Detailmodell' }).click();
  expect(await stage(page)).toBe('detail');
  expect(await page.evaluate(() => window.__fl.progress)).toBe(2);
});

test('dragging the scrubber to its end selects Gebaut', async ({ page }) => {
  await open(page);
  const s = page.getByRole('slider');
  const box = await s.boundingBox();
  await page.mouse.move(box.x + 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width + 20, box.y + box.height / 2, { steps: 8 });
  await page.mouse.up();
  expect(await stage(page)).toBe('built');
});

test('Play advances p and stops at 3', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Abspielen' }).click();
  await page.waitForTimeout(1500);
  const mid = await page.evaluate(() => window.__fl.progress);
  expect(mid).toBeGreaterThan(0);
  await page.waitForFunction(() => window.__fl.progress === 3, null, { timeout: 30_000 });
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => window.__fl.progress)).toBe(3);
  expect(await stage(page)).toBe('built');
});

test('"Ohne Dach" hides the roof collection, keeps the ground', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Ohne Dach' }).click();
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('noroof');
  for (const n of ['Dach', 'Dach_Sparren', 'Verschalung_West', 'Giebel']) expect(await vis(page, n)).toBe(false);
  for (const n of ['Gelaende', 'OG_Waende', 'EG_Waende']) expect(await vis(page, n)).toBe(true);
});

test('"Nur EG" also hides the OG and its balconies', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Nur EG' }).click();
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('eg');
  for (const n of ['Dach', 'OG_Waende', 'OG_Decke_EG', 'OG_Laeden_Querbretter', 'Balkon_OG_Nord', 'Balkon_OG_Ost', 'Balkon_OG_Sued'])
    expect(await vis(page, n)).toBe(false);
  for (const n of ['Gelaende', 'EG_Waende', 'Balkon_EG_Nord']) expect(await vis(page, n)).toBe(true);
  await page.getByRole('button', { name: 'Detailmodell' }).click();
  await page.waitForTimeout(500);
  await shot(page, 'cutaway_eg.png');                                       // for the eye
  await page.getByRole('button', { name: 'Ganzes Haus' }).click();
  expect(await vis(page, 'Dach')).toBe(true);
});

for (const [w, h] of [[1280, 720], [1920, 1080]])
  test(`controls don't overlap at ${w}×${h}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: h });
    await open(page);
    const boxes = await page.evaluate(() =>
      ['.fl-title', '.fl-bar', '.fl-tools'].map((s) => document.querySelector(s).getBoundingClientRect().toJSON()));
    for (let i = 0; i < boxes.length; i++)
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        const overlap = a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
        expect(overlap, `${i}/${j}`).toBe(false);
      }
    for (const b of boxes) expect(b.right <= w && b.bottom <= h && b.left >= 0 && b.top >= 0).toBe(true);
    // every control group sits on its own paper panel, so it stays readable on the dusk sky
    const bgs = await page.evaluate(() =>
      ['.fl-title', '.fl-bar', '.fl-tools'].map((s) => getComputedStyle(document.querySelector(s)).backgroundColor));
    for (const bg of bgs) expect(bg).not.toBe('rgba(0, 0, 0, 0)');
    await shot(page, `ui_${w}.png`);
  });
