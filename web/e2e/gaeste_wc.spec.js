// The Gäste-WC sub-model page (gaeste_wc.html): house_core.build_gaeste_wc() (code/gaeste_wc.py) with its dimensions.
import { test, expect } from '@playwright/test';
import { existsSync, readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const file = new URL('../public/gaeste_wc.glb', import.meta.url);
const glb = existsSync(file) ? readFileSync(file) : null;
const DIMS = glb ? JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims : [];

test('Gäste-WC page draws WC, Garderobe and basin with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/gaeste_wc.html');
  await page.waitForFunction(() => window.__gaeste_wc?.ready === true);
  expect(await page.evaluate(() => window.__gaeste_wc.edges)).toBeGreaterThan(50);
  expect(DIMS.length).toBeGreaterThan(10);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  for (const t of ['WC 101', 'Garderobe 94', 'Tür 76', '40 frei', '59 frei', '83 frei', 'Bank 35 × 110', 'HWB 40', 'Spiegel 54 × 74']) {
    await expect(page.locator('.dim', { hasText: t })).toBeVisible();
  }
  for (const [view, look] of [['Schräg', 'Drahtmodell'], ['Von oben', 'Masse'], ['Vom Flur', 'Gerendert']]) {
    await page.getByRole('button', { name: view }).click();
    await page.getByRole('button', { name: look }).click();
    await page.waitForTimeout(600);
    const img = await shot(page, `gaeste_wc_e2e_${look}.png`);
    let ink = 0;
    for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
    expect(ink).toBeGreaterThan(20);
  }
  expect(errors).toEqual([]);
});

test('the three doors swing: every 3 s one, picked at random, to its other state in 3 s', async ({ page }) => {
  await page.goto('/gaeste_wc.html');
  await page.waitForFunction(() => window.__gaeste_wc?.ready === true);
  const at = () => page.evaluate(() => window.__gaeste_wc.doors());
  const first = await at();
  expect(Object.keys(first).sort()).toEqual(['GaesteWC_Hintertuer', 'GaesteWC_WC_Tuer', 'GaesteWC_Windfangtuer']);
  expect(Object.values(first).map((s) => s.pos)).toEqual([0, 0, 0]);               // as built after loading
  await page.waitForFunction(() => Object.values(window.__gaeste_wc.doors()).some((s) => s.pos > 0.2 && s.pos < 0.8), null, { timeout: 6000, polling: 16 });
  await page.waitForFunction(() => Object.values(window.__gaeste_wc.doors()).some((s) => s.pos === 1), null, { timeout: 6000 });
  const swung = Object.values(await at()).filter((s) => s.pos === 1);
  expect(swung).toHaveLength(1);
  expect(Math.abs(swung[0].yaw)).toBeCloseTo(Math.PI / 2, 3);                      // a quarter turn about the hinge
});

test('in the house the doors swing too: in Eingerichtet, drawn while they move; not in the Rundgang', async ({ page }) => {
  await page.goto('/?cam=1.0,8.35,1.6&at=1.5,6.2,1.0&p=4&cut=eg');               // back hall, looking south
  await page.waitForFunction(() => window.__fl?.ready === true);
  const at = () => page.evaluate(() => window.__fl.doors());
  expect(Object.keys(await at()).sort()).toEqual(['EG_Hintertuer', 'EG_WC_Tuer', 'EG_Windfangtuer']);
  await page.waitForFunction(() => Object.values(window.__fl.doors()).some((s) => s.pos > 0 && s.pos < 0.5), null, { timeout: 9000, polling: 16 });
  const d0 = await page.evaluate(() => window.__fl.draws);
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => window.__fl.draws)).toBeGreaterThan(d0 + 3);   // drawn while swinging
  await page.evaluate(() => window.__fl.setProgress(3));                            // Gebaut: as built
  await page.waitForTimeout(100);
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0, 0, 0]);
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();        // Eingerichtet again,
  await page.waitForTimeout(4000);                                                  // but the tour (the film)
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0, 0, 0]);          // sees them as built
});
