// The Küche sub-model page (kueche.html): house_core.build_kueche() (code/kueche.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { choose, entries } from './menu.js';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/kueche.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Küche page draws the kitchen with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/kueche.html');
  await page.waitForFunction(() => window.__kueche?.ready === true);
  expect(await page.evaluate(() => window.__kueche.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBe(8);                                     // kueche.py draws eight
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['Spülzeile 150.5', 'Ostzeile 60', 'Herd 80', 'Besenschrank 51', '55 tief', 'Abzug ab 180', 'Halbinsel 198.5', 'Abzug 30 tief (angenommen)']) {
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Spülzeile', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `kueche_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the drop-down reaches every page, from the house and from a sub-model', async ({ page }) => {
  const pages = [['Ofen', '/ofen.html', '__ofen'], ['Schreibtisch', '/desk.html', '__desk'], ['Bad Oma & Opa', '/bad.html', '__bad'], ['Küche', '/kueche.html', '__kueche'], ['Gäste-WC', '/gaeste_wc.html', '__gaeste_wc'], ['Schrank im Büro', '/regal.html', '__regal'], ['Schrankbett', '/schrankbett.html', '__schrankbett'], ['Gästebad', '/gaestebad.html', '__gaestebad'], ['Bad Nadine & Till', '/elternbad.html', '__elternbad']];
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  const sel = page.getByRole('button', { name: 'Modell', exact: true });
  await sel.click();
  expect(await entries(page)).toEqual(['Ganzes Haus', 'Erdgeschoss', 'Erdgeschoss - Alternativ', '1. Stock', '—', ...pages.map((p) => p[0])]);
  await sel.click();
  await expect(sel).toHaveText('Ganzes Haus');
  for (const [label, path, hook] of pages) {
    await choose(page, 'Modell', label);
    await page.waitForFunction((h) => window[h]?.ready === true, hook);
    expect(new URL(page.url()).pathname).toBe(path);
    await expect(sel).toHaveText(label);
    await choose(page, 'Modell', 'Ganzes Haus');
    await page.waitForFunction(() => window.__fl?.ready === true);
    expect(new URL(page.url()).pathname).toBe('/');
  }
  await page.goto('/kueche.html');                                  // sub-model to sub-model
  await page.waitForFunction(() => window.__kueche?.ready === true);
  await choose(page, 'Modell', 'Ofen');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/ofen.html');
});
