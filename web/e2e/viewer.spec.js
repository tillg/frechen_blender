import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { shot, pixel } from './pixels.js';

const glb = readFileSync(new URL('../public/frechenlehen.glb', import.meta.url));
const NODES = JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).nodes.length;
const BACKGROUND = [0xf3, 0xef, 0xe6];

test('page renders a canvas without console errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await expect(page.locator('canvas')).toBeVisible();
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(errors).toEqual([]);
});

test('blueprint is loaded', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await page.evaluate(() => window.__fl.objectCount)).toBe(NODES);
  await page.evaluate(() => window.__fl.setProgress(1));                 // Massenmodell
  await page.waitForTimeout(400);
  const img = await shot(page, 'massing.png');
  // the house fills the centre third: most of it is not background (clay ≈ paper, so count
  // shading, shadows and edges rather than a single pixel)
  let n = 0, off = 0;
  for (let y = img.height / 3; y < (2 * img.height) / 3; y += 4)
    for (let x = img.width / 3; x < (2 * img.width) / 3; x += 4, n++)
      if (Math.max(...pixel(img, x, y).map((v, i) => Math.abs(v - BACKGROUND[i]))) > 12) off++;
  expect(off / n).toBeGreaterThan(0.3);
  await page.evaluate(() => window.__fl.lookFrom(-22, 34, 13));         // north-west, for the eye
  await page.waitForTimeout(500);
  await shot(page, 'massing_nw.png');
});
