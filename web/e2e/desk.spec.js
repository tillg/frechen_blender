// The desk sub-model page (desk.html): house_core.build_desk() with its dimensions; in Gerendert the
// two monitors show the screenshots (a12 left: its blue hero band, pilcrow right: the green meadow).
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const glb = readFileSync(new URL('../public/desk.glb', import.meta.url));
const DIMS = JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims;

test('desk page draws the desk with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/desk.html');
  await page.waitForFunction(() => window.__desk?.ready === true);
  expect(await page.evaluate(() => window.__desk.edges)).toBeGreaterThan(50);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  await expect(page.locator('.dim', { hasText: 'Tisch 194.8' })).toBeVisible();
  const img = await shot(page, 'desk_e2e_wire.png');
  let ink = 0;
  for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
  expect(ink).toBeGreaterThan(20);
  expect(errors).toEqual([]);
});

test('in Gerendert the monitors show the two screenshots', async ({ page }) => {
  await page.goto('/desk.html');
  await page.waitForFunction(() => window.__desk?.ready === true);
  await page.getByRole('button', { name: 'Auf die Bildschirme' }).click();
  await page.getByRole('button', { name: 'Gerendert' }).click();
  await page.waitForFunction(() => window.__desk.textures() === 2);
  await page.waitForTimeout(800);
  const img = await shot(page, 'desk_e2e_full.png');
  let blueL = 0, greenR = 0;
  for (let y = 0; y < img.height; y += 2) for (let x = 0; x < img.width; x += 2) {
    const i = 4 * (y * img.width + x), [r, g, b] = img.data.slice(i, i + 3);
    if (x < img.width / 2 && b > 100 && b > r + 50 && b > g + 20) blueL++;
    if (x > img.width / 2 && g > 70 && g > r + 25 && g > b + 25) greenR++;
  }
  expect(blueL).toBeGreaterThan(2000);
  expect(greenR).toBeGreaterThan(2000);
});

test('the house links to the desk page and back', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  await page.getByRole('link', { name: 'Schreibtisch' }).click();
  await page.waitForFunction(() => window.__desk?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/desk.html');
  await page.getByRole('link', { name: '← Haus' }).click();
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/');
});
