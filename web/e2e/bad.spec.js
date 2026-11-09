// The Bad Großeltern sub-model page (bad.html): house_core.build_bad() (code/bad.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/bad.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Bad page draws the bathroom with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/bad.html');
  await page.waitForFunction(() => window.__bad?.ready === true);
  expect(await page.evaluate(() => window.__bad.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(8);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['Dusche 80', 'Glas 35', 'Mauer 120', 'Waschtrog 100', 'WC 96.4', 'Schrank 96.4', '120 tief', 'Durchgang 96.7']) {
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  await expect(page.locator('.dim', { hasText: /^60$/ })).toHaveCount(1);                    // the cabinet's depth (the wardrobe is gone)
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['In die Nische', 'Gerendert']]) {
    await page.getByRole('button', { name: view }).click();
    await page.getByRole('button', { name: look }).click();
    await page.waitForTimeout(600);
    const img = await shot(page, `bad_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the house links to the Bad page and back', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  await page.getByLabel('Teilmodell').selectOption({ label: 'Bad Oma & Opa' });
  await page.waitForFunction(() => window.__bad?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/bad.html');
  await page.getByLabel('Teilmodell').selectOption({ label: 'Haus' });
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/');
});
