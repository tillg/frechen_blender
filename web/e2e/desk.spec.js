// The desk sub-model page (desk.html): house_core.build_desk() with its dimensions; in Gerendert the
// two monitors show the screenshots (a12 left: its blue hero band, pilcrow right: the green meadow).
import { test, expect } from '@playwright/test';
import { choose } from './menu.js';
import { readFileSync } from 'node:fs';
import { SHOTS, shot } from './pixels.js';

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
  await expect(page.locator('.dim', { hasText: 'Tisch 190' })).toBeVisible();
  const img = await shot(page, 'desk_e2e_wire.png');
  let ink = 0;
  for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
  expect(ink).toBeGreaterThan(20);
  expect(errors).toEqual([]);
});

test('in Gerendert the monitors show the two screenshots', async ({ page }) => {
  await page.goto('/desk.html');
  await page.waitForFunction(() => window.__desk?.ready === true);
  await choose(page, 'Standpunkt', 'Auf die Bildschirme');
  await choose(page, 'Darstellung', 'Gerendert');
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
  await choose(page, 'Modell', 'Schreibtisch');
  await page.waitForFunction(() => window.__desk?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/desk.html');
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/');
});

// #10: the cherry top on the crank frame goes up 30 cm with everything on it, the hand wheel turning
const LIFTED = ['Desk_Bildschirm_L', 'Desk_Bildschirm_R', 'Desk_Geraete', 'Desk_Schreibtisch'];
test('the desk cranks up 30 cm in 3 s with all on it, rests 4 s, cranks down; the hand wheel turns', async ({ page }) => {
  await page.goto('/desk.html?cam=3.4,-2.6,1.6&at=0.95,0.5,0.7&look=full');
  await page.waitForFunction(() => window.__desk?.ready === true);
  const at = () => page.evaluate(() => window.__desk.lift());
  const s0 = await at();
  expect(Object.keys(s0).sort()).toEqual([...LIFTED, 'Desk_Handrad'].sort());
  expect(Object.values(s0).map((s) => s.pos)).toEqual([0, 0, 0, 0, 0]);               // as built: 75 cm
  await page.screenshot({ path: SHOTS + 'desk_e2e_low.png', scale: 'css' });
  await page.waitForFunction(() => window.__desk.lift().Desk_Schreibtisch.pos === 1, null, { timeout: 12000 });
  const t0 = Date.now(), up = await at();
  for (const n of LIFTED) expect(up[n].dy).toBeCloseTo(0.30, 5);                        // together, 30 cm
  expect(up.Desk_Handrad.angle).toBeCloseTo(8 * Math.PI, 5);                             // four turns
  await page.screenshot({ path: SHOTS + 'desk_e2e_high.png', scale: 'css' });   // to look at
  await page.waitForTimeout(Math.max(0, 3000 - (Date.now() - t0)));
  expect((await at()).Desk_Schreibtisch.pos).toBe(1);                                    // rests up there (4 s)
  await page.waitForFunction(() => window.__desk.lift().Desk_Schreibtisch.pos === 0, null, { timeout: 6000 });
  expect(Date.now() - t0).toBeGreaterThan(3900);                                         // rest + stroke
});

test('in the house the desk cranks up too: in Eingerichtet, drawn while it moves; not in the Rundgang', async ({ page }) => {
  await page.goto('/?cam=11.9,9.4,1.6&at=11.9,12.0,0.9&p=4&cut=eg');                   // Bibliothek, onto the desk
  await page.waitForFunction(() => window.__fl?.ready === true);
  const at = () => page.evaluate(() => window.__fl.lift());
  expect(Object.keys(await at()).sort()).toEqual(['EG_Bildschirm_L', 'EG_Bildschirm_R', 'EG_Geraete', 'EG_Handrad', 'EG_Schreibtisch',
    'OG_Klappbett', 'OG_Klappfuesse']);                                                  // the Schrankbett on the same clock (#7)
  await page.waitForFunction(() => { const p = window.__fl.lift().EG_Schreibtisch.pos; return p > 0 && p < 0.5; }, null, { timeout: 12000, polling: 16 });
  const d0 = await page.evaluate(() => window.__fl.draws);
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => window.__fl.draws)).toBeGreaterThan(d0 + 3);        // drawn while it moves
  await page.evaluate(() => window.__fl.setProgress(3));                                // Gebaut: as built
  await page.waitForTimeout(100);
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0, 0, 0, 0, 0, 0, 0]);
  await choose(page, 'Modell', 'Ganzes Haus');                                         // the routes are listed there
  await choose(page, 'Standpunkt', 'Um und durch das Haus');                            // the tour (the film)
  await page.waitForTimeout(8000);                                                      // sees it as built
  expect(Object.values(await at()).map((s) => s.pos)).toEqual([0, 0, 0, 0, 0, 0, 0]);
});
