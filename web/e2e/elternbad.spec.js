// The Bad Nadine & Till sub-model page (elternbad.html, #3): house_core.build_elternbad() (code/elternbad.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/elternbad.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Bad Nadine & Till page draws shower, toilet and basin with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/elternbad.html');
  await page.waitForFunction(() => window.__elternbad?.ready === true);
  expect(await page.evaluate(() => window.__elternbad.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(10);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['Dusche 213 × 98', 'Glas 153', '60 offen', 'Waschbecken 100', 'Spiegel 110 × 85', 'Tür 93', 'Fenster 88']) {
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Von der Tür', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `elternbad_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});
