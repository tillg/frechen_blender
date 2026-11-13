// The Gästebad sub-model page (gaestebad.html, #18): house_core.build_gaestebad() (code/gaestebad.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/gaestebad.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Gästebad page draws WC niche, shower and basin with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/gaestebad.html');
  await page.waitForFunction(() => window.__gaestebad?.ready === true);
  expect(await page.evaluate(() => window.__gaestebad.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(10);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['WC 101', 'Dusche 115 × 139', 'Glas 65', '50 offen', 'Waschbecken 120', 'Spiegel 140 × 95', 'Tür 81']) {
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Von der Tür', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `gaestebad_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});
