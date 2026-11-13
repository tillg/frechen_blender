// The Schrankbett sub-model page (schrankbett.html): house_core.build_schrankbett() (code/schrankbett.py),
// the Yoga room's wall bed with its dimensions; the bed folds up and down every few seconds (#7).
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { existsSync, readFileSync } from 'node:fs';
import { shot, SHOTS } from './pixels.js';

const file = new URL('../public/schrankbett.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Schrankbett page draws the Schrankwand and the bed with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/schrankbett.html');
  await page.waitForFunction(() => window.__schrankbett?.ready === true);
  expect(await page.evaluate(() => window.__schrankbett.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(8);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['Schrank 36', 'Bett 206', 'Tiefe 45', 'Raumhöhe 220', 'Blende 10', 'Liegefläche 200', 'Liegehöhe 39']) {
    await expect(page.locator('.dim', { hasText: t }).first()).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Von vorn', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `schrankbett_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the bed folds up into the Schrankwand in 3 s, its feet folding in, rests 4 s, folds down again', async ({ page }) => {
  await page.goto('/schrankbett.html');
  await page.waitForFunction(() => window.__schrankbett?.ready === true);
  const at = () => page.evaluate(() => window.__schrankbett.lift());
  expect(await at()).toEqual({ Schrankbett_Klappbett: { pos: 0, angle: 0 }, Schrankbett_Klappfuesse: { pos: 0, angle: 0 } });   // as built: down
  await page.screenshot({ path: SHOTS + 'schrankbett_e2e_down.png', scale: 'css' });
  await page.waitForFunction(() => window.__schrankbett.lift().Schrankbett_Klappbett.pos === 1, null, { timeout: 12000 });
  const t0 = Date.now();
  expect((await at()).Schrankbett_Klappbett.angle).toBeCloseTo(Math.PI / 2, 5);           // folded up
  expect((await at()).Schrankbett_Klappfuesse.pos).toBe(1);                                 // the feet with it
  await page.screenshot({ path: SHOTS + 'schrankbett_e2e_up.png', scale: 'css' });
  await page.waitForTimeout(Math.max(0, 3000 - (Date.now() - t0)));
  expect((await at()).Schrankbett_Klappbett.pos).toBe(1);                                   // rests up (4 s)
  await page.waitForFunction(() => window.__schrankbett.lift().Schrankbett_Klappbett.pos === 0, null, { timeout: 6000 });
  expect(Date.now() - t0).toBeGreaterThan(3900);                                            // rest + stroke
});
