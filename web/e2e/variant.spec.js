import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { shot } from './pixels.js';

// Issue #5: the EG variant Alternativ (cabinet C on the Essen's west wall, saloon door to the Speis)
// is the house entry "Erdgeschoss - Alternativ" (cutaway eg_alt); every other entry shows the default.
async function open(page, q = '') {
  await page.goto('/' + q);
  await page.waitForFunction(() => window.__fl?.ready === true);
}
const vis = (page, name) => page.evaluate((n) => window.__fl.visible(n), name);
const MAIN = ['EG_Speis_C', 'EG_Speis_Schiebetuer', 'EG_Speis_Waende'];
const ALT = ['EG_Alt_Schrank', 'EG_Alt_Speis', 'EG_Alt_Pendeltuer_S', 'EG_Alt_Pendeltuer_N'];
async function expectVariant(page, v) {
  for (const n of MAIN) expect(await vis(page, n), n).toBe(v === 'main');
  for (const n of ALT) expect(await vis(page, n), n).toBe(v === 'alt');
}

test('Erdgeschoss - Alternativ shows the variant, Erdgeschoss the default, and a reload keeps it', async ({ page }) => {
  await open(page);
  await expectVariant(page, 'main');                                         // Ganzes Haus: the default
  await choose(page, 'Modell', 'Erdgeschoss - Alternativ');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('eg_alt');
  await expectVariant(page, 'alt');
  for (const n of ['OG_Waende', 'Dach']) expect(await vis(page, n)).toBe(false);   // cut as Erdgeschoss
  for (const n of ['EG_Waende', 'EG_Speis', 'Gelaende']) expect(await vis(page, n)).toBe(true);
  expect(await page.evaluate(() => window.__fl.spot)).not.toBeNull();       // an Erdgeschoss Standpunkt
  await choose(page, 'Darstellung', 'Gebaut');
  await expectVariant(page, 'alt');                                          // also without the furniture
  await page.waitForTimeout(300);
  await shot(page, 'variant_eg_alt.png');                                    // for the eye
  await page.waitForTimeout(400);                                            // the view lands in the URL
  await page.reload();
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('eg_alt');
  await expectVariant(page, 'alt');
  await choose(page, 'Modell', 'Erdgeschoss');
  await expectVariant(page, 'main');
});

test('the Skizze lines follow the variant', async ({ page }) => {
  await open(page, '?p=0&cut=eg_alt');
  const inks = () => page.evaluate(() => window.__fl.inks());
  expect(await inks()).toContain('Ink_EG_base_alt');
  expect(await inks()).not.toContain('Ink_EG_base_main');
  await page.evaluate(() => window.__fl.setCutaway('eg'));
  expect(await inks()).toContain('Ink_EG_base_main');
  expect(await inks()).not.toContain('Ink_EG_base_alt');
});
