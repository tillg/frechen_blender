// The Bad Großeltern sub-model page (bad.html): house_core.build_bad() (code/bad.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
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
  for (const t of ['Raumbreite 204.8', 'Raumtiefe 381.7', 'Dusche 90', 'Glas 75', 'Einstieg 55', 'Öffnung 102.4',
                   '130 tief', 'HWB 60', 'Spiegel 60 × 85']) {   // #63: WC and shower in the niche, basin on the north wall
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['In die Nische', 'Gerendert']]) {
    await choose(page, 'Standpunkt', view);
    await choose(page, 'Darstellung', look);
    await page.waitForTimeout(600);
    const img = await shot(page, `bad_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the sliding leaf rolls (#61: one): every 4 s to its other end of travel', async ({ page }) => {
  await page.goto('/bad.html');
  await page.waitForFunction(() => window.__bad?.ready === true);
  const at = () => page.evaluate(() => window.__bad.slides());
  const first = await at();
  expect(Object.keys(first).sort()).toEqual(['Bad_Schiebetuer']);
  expect(Object.values(first).map((s) => s.pos)).toEqual([0]);                 // as built after loading
  await page.waitForFunction(() => Object.values(window.__bad.slides()).some((s) => s.pos === 1), null, { timeout: 9000 });
  const rolled = Object.values(await at()).filter((s) => s.pos === 1);
  expect(rolled).toHaveLength(1);
  expect(rolled[0].dx).toBeCloseTo(-0.979, 3);                                       // node moved by the core's slide
});

test('in the house the leaf rolls too: in Eingerichtet, drawn while it moves; not in the Rundgang', async ({ page }) => {
  await page.goto('/?cam=3.9,10.4,1.7&at=1.2,9.9,0.9&p=4&cut=eg');                 // bedroom, the niche ahead
  await page.waitForFunction(() => window.__fl?.ready === true);
  const at = () => page.evaluate(() => window.__fl.slides());
  expect(Object.keys(await at()).sort()).toEqual(['EG_Schiebetuer']);
  await page.waitForFunction(() => Object.values(window.__fl.slides()).some((s) => s.pos > 0 && s.pos < 0.5), null, { timeout: 9000, polling: 16 });
  const d0 = await page.evaluate(() => window.__fl.draws);
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => window.__fl.draws)).toBeGreaterThan(d0 + 3);   // drawn while rolling
  await page.waitForFunction(() => Object.values(window.__fl.slides()).some((s) => s.pos === 1), null, { timeout: 9000 });
  expect(Object.values(await at()).find((s) => s.pos === 1).dx).toBeCloseTo(-0.979, 3);
  await page.evaluate(() => window.__fl.setProgress(3));                            // Gebaut: as built
  await page.waitForTimeout(100);
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0]);
  await choose(page, 'Modell', 'Ganzes Haus');                      // the routes are listed there
  await choose(page, 'Standpunkt', 'Um und durch das Haus');        // Eingerichtet again,
  await page.waitForTimeout(5000);                                                  // but the tour sees them
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0]);             // as built
});

test('the house links to the Bad page and back', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  await choose(page, 'Modell', 'Bad Oma & Opa');
  await page.waitForFunction(() => window.__bad?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/bad.html');
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/');
});
