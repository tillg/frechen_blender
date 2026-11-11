// The "Schrank im Büro" sub-model page (regal.html): house_core.build_regal() (code/regal.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/regal.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Schrank im Büro page draws the bookcase round the window with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/regal.html');
  await page.waitForFunction(() => window.__regal?.ready === true);
  expect(await page.evaluate(() => window.__regal.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(10);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['48 frei', 'Säule 94', 'Mitte 94', '30 frei', 'Fenster 90', 'Unterteil 95', 'Brücke 36', 'Höhe 238', 'Tür 106', '10,5 Luft']) {
    await expect(page.locator('.dim', { hasText: t }).first()).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Von vorn', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `regal_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the Büro door swings shut in 2 s, rests 4 s, swings open again: to show how it clears the bookcase', async ({ page }) => {
  await page.goto('/regal.html');
  await page.waitForFunction(() => window.__regal?.ready === true);
  const at = () => page.evaluate(() => window.__regal.doors());
  expect(await at()).toEqual({ Regal_Buerotuer: { pos: 0, yaw: 0 } });                 // as built: open 90 deg
  await page.waitForFunction(() => window.__regal.doors().Regal_Buerotuer.pos === 1, null, { timeout: 9000 });
  const t0 = Date.now();
  expect(Math.abs((await at()).Regal_Buerotuer.yaw)).toBeCloseTo(Math.PI / 2, 3);      // a quarter turn: shut
  await page.waitForTimeout(3000);
  expect((await at()).Regal_Buerotuer.pos).toBe(1);                                    // still shut (4 s rest)
  await page.waitForFunction(() => window.__regal.doors().Regal_Buerotuer.pos === 0, null, { timeout: 5000 });
  expect(Date.now() - t0).toBeGreaterThan(3900);                                       // rest + swing
});
