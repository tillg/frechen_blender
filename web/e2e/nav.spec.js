// The toolbar of every page (toolbar.js): Modell / Darstellung / Standpunkt, sun toggle, Reset.
import { test, expect } from '@playwright/test';
import { choose, entries } from './menu.js';

const PAGES = [['/', '__fl'], ['/ofen.html', '__ofen'], ['/desk.html', '__desk'], ['/bad.html', '__bad'],
  ['/kueche.html', '__kueche'], ['/gaeste_wc.html', '__gaeste_wc'], ['/regal.html', '__regal']];

async function open(page, url = '/', hook = '__fl') {
  await page.goto(url);
  await page.waitForFunction((h) => window[h]?.ready === true, hook);
}

const boxes = (page) => page.evaluate(() => ['Modell', 'Darstellung', 'Standpunkt', '↺ Reset'].map((n) => {
  const b = [...document.querySelectorAll('.fl-tools button')].find((e) => e.getAttribute('aria-label') === n || e.textContent === n);
  return b.getBoundingClientRect().toJSON();
}));

test('the three drop-downs and Reset sit at the same box on the house and every sub-model page', async ({ page }) => {
  await open(page);
  const house = await boxes(page);
  for (const [url, hook] of PAGES.slice(1)) {
    await open(page, url, hook);
    expect(await boxes(page), url).toEqual(house);
  }
});

test('Modell lists Ganzes Haus, Erdgeschoss, Erdgeschoss - Alternativ, 1. Stock, a separator, then the six sub-models', async ({ page }) => {
  for (const [url, hook] of [PAGES[0], PAGES[1]]) {
    await open(page, url, hook);
    await page.getByRole('button', { name: 'Modell', exact: true }).click();
    expect(await entries(page), url).toEqual(['Ganzes Haus', 'Erdgeschoss', 'Erdgeschoss - Alternativ', '1. Stock', '—', 'Ofen', 'Schreibtisch',
      'Bad Oma & Opa', 'Küche', 'Gäste-WC', 'Schrank im Büro']);
  }
});

test('Darstellung lists the five stages (Ganzes Haus: then the plan sheets) on the house and the three looks on a sub-model', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Darstellung', exact: true }).click();
  expect(await entries(page)).toEqual(['Skizze', 'Massenmodell', 'Detailmodell', 'Gebaut', 'Eingerichtet',
    'Grundriss EG', 'Grundriss OG', 'Ansicht Nord', 'Ansicht Ost', 'Ansicht Süd', 'Ansicht West']);
  await open(page, '/ofen.html', '__ofen');
  await page.getByRole('button', { name: 'Darstellung', exact: true }).click();
  expect(await entries(page)).toEqual(['Drahtmodell', 'Masse', 'Gerendert']);
});

test('the lists open below their box', async ({ page }) => {
  await open(page);
  await choose(page, 'Standpunkt', 'Um und durch das Haus');               // the last entry chosen
  await page.getByRole('button', { name: 'Beenden' }).click();
  const btn = page.getByRole('button', { name: 'Standpunkt', exact: true });
  await btn.click();
  const [b, l] = [await btn.boundingBox(), await page.locator('.fl-list:not([hidden])').boundingBox()];
  expect(l.y).toBeGreaterThan(b.y + b.height);
});

test('Erdgeschoss hides roof and OG, without a reload', async ({ page }) => {
  await open(page);
  await page.evaluate(() => { window.__same = true; });
  await choose(page, 'Modell', 'Erdgeschoss');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('eg');
  for (const n of ['Dach', 'OG_Waende']) expect(await page.evaluate((x) => window.__fl.visible(x), n)).toBe(false);
  expect(await page.evaluate(() => window.__fl.visible('EG_Waende'))).toBe(true);
  expect(await page.evaluate(() => window.__same)).toBe(true);
  await expect(page.getByRole('button', { name: 'Modell', exact: true })).toHaveText('Erdgeschoss');
});

// ---------------------------------------------------------------- saved view per model entry, Reset
const btnText = (page, name) => page.getByRole('button', { name, exact: true }).textContent();

test('Ofen: Masse + Von oben survive leaving to the house and coming back', async ({ page }) => {
  await open(page, '/ofen.html', '__ofen');
  await choose(page, 'Darstellung', 'Masse');
  await choose(page, 'Standpunkt', 'Von oben');
  await page.waitForTimeout(500);                                          // the view is written after 300 ms
  await choose(page, 'Modell', 'Ganzes Haus');
  await page.waitForFunction(() => window.__fl?.ready === true);
  await page.goto('/ofen.html');                                          // no query: the saved view
  await page.waitForFunction(() => window.__ofen?.ready === true);
  expect(await page.evaluate(() => window.__ofen.look())).toBe('mass');
  const cam = await page.evaluate(() => window.__ofen.camera);
  [1.701, 1.1, 8.5].forEach((v, i) => expect(Math.abs(cam[i] - v)).toBeLessThan(0.01));
  expect(await btnText(page, 'Darstellung')).toBe('Masse');
  expect(await btnText(page, 'Standpunkt')).toBe('Von oben');
});

test('a sub-model: orbiting shows Eigene Ansicht, and picking the view again returns the camera', async ({ page }) => {
  await open(page, '/ofen.html', '__ofen');
  await page.mouse.move(640, 400);
  await page.mouse.down();
  await page.mouse.move(450, 380, { steps: 10 });
  await page.mouse.up();
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toHaveText('Eigene Ansicht');
  await choose(page, 'Standpunkt', 'Schräg');
  await page.waitForTimeout(300);
  const cam = await page.evaluate(() => window.__ofen.camera);
  [5.0, 4.4, 3.0].forEach((v, i) => expect(Math.abs(cam[i] - v)).toBeLessThan(0.01));
  expect(await btnText(page, 'Standpunkt')).toBe('Schräg');
});

test('Erdgeschoss and Ganzes Haus remember their own Darstellung; the bare URL opens the last entry', async ({ page }) => {
  await open(page);
  await choose(page, 'Darstellung', 'Gebaut');
  await choose(page, 'Modell', 'Erdgeschoss');
  await choose(page, 'Darstellung', 'Massenmodell');
  await page.waitForTimeout(500);
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(await btnText(page, 'Modell')).toBe('Erdgeschoss');
  expect(await page.evaluate(() => document.body.dataset.stage)).toBe('massing');
  await choose(page, 'Modell', 'Ganzes Haus');
  expect(await page.evaluate(() => document.body.dataset.stage)).toBe('built');
  expect(await page.evaluate(() => document.body.dataset.cutaway)).toBe('all');
});

test('a ?cam= link wins over the saved view', async ({ page }) => {
  await open(page, '/ofen.html', '__ofen');
  await choose(page, 'Darstellung', 'Masse');
  await page.waitForTimeout(500);
  await page.goto('/ofen.html?cam=3.6,3.6,1&at=0.95,0.95,0.6&look=full');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  expect(await page.evaluate(() => window.__ofen.look())).toBe('full');
});

test('Reset: lowest Darstellung and the standard Standpunkt, and the saved view is gone', async ({ page }) => {
  await open(page, '/ofen.html', '__ofen');
  await choose(page, 'Darstellung', 'Gerendert');
  await choose(page, 'Standpunkt', 'Von oben');
  await page.waitForTimeout(500);
  await page.getByRole('button', { name: '↺ Reset' }).click();
  expect(await page.evaluate(() => window.__ofen.look())).toBe('wire');
  expect(await btnText(page, 'Standpunkt')).toBe('Schräg');
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith('frechenlehen:ofen')))).toEqual([]);
  await open(page);
  await choose(page, 'Darstellung', 'Eingerichtet');
  await page.evaluate(() => window.__fl.lookFrom(-22, 34, 13));
  await page.getByRole('button', { name: '↺ Reset' }).click();
  expect(await page.evaluate(() => document.body.dataset.stage)).toBe('sketch');
  expect(await page.evaluate(() => window.__fl.cameraAt())).toEqual([33, -24, 13]);
  expect(await btnText(page, 'Standpunkt')).toBe('Von Südosten');
  await page.waitForTimeout(500);
  expect(await page.evaluate(() => Object.keys(localStorage).filter((k) => k === 'frechenlehen:index:haus'))).toEqual([]);
});

// ---------------------------------------------------------------- house Standpunkte (tour.py SPOTS)
const camAt = (page) => page.evaluate(() => window.__fl.cameraAt());
const distTo = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

test('Bibliothek - Ecke hinten rechts puts the camera at its spot, looking at its target; dragging turns the view in place', async ({ page }) => {
  await open(page);
  await choose(page, 'Standpunkt', 'Bibliothek - Ecke hinten rechts');
  expect(distTo(await camAt(page), [13.7, 12.05, 1.6])).toBeLessThan(0.01);
  const c = await page.evaluate(() => window.__fl.project(9.2, 9.4, 1.0));       // the target sits mid-screen
  const vp = page.viewportSize();
  expect(Math.abs(c.x - vp.width / 2)).toBeLessThan(2);
  expect(Math.abs(c.y - vp.height / 2)).toBeLessThan(2);
  expect(await page.evaluate(() => window.__fl.fov)).toBe(60);
  const v0 = await page.evaluate(() => window.__fl.view);
  await page.mouse.move(640, 400);
  await page.mouse.down();
  await page.mouse.move(400, 380, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(800);
  expect(distTo(await camAt(page), [13.7, 12.05, 1.6])).toBeLessThan(0.15);       // stays in the corner
  const v1 = await page.evaluate(() => window.__fl.view);
  expect(v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]).toBeLessThan(0.99);        // but the view turned
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toHaveText('Eigene Ansicht');
});

test('Ganzes Haus lists the outside views, both storeys\' rooms and the routes; Erdgeschoss no OG room', async ({ page }) => {
  await open(page);
  await page.getByRole('button', { name: 'Standpunkt', exact: true }).click();
  const all = await entries(page);
  for (const n of ['Von Südosten', 'Von Nordwesten', 'Stube', 'Bibliothek - Ecke hinten rechts', 'Bibliothek - Klavierspieler', 'Bichlach', 'Yoga', 'Um und durch das Haus', 'Durch die Stube & Küche'])
    expect(all, n).toContain(n);
  await page.keyboard.press('Escape');
  await choose(page, 'Modell', 'Erdgeschoss');
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toHaveText('Von oben');   // its standard
  await page.getByRole('button', { name: 'Standpunkt', exact: true }).click();
  const eg = await entries(page);
  expect(eg).toContain('Bibliothek - Ecke hinten rechts');
  expect(eg).toContain('Bibliothek - Klavierspieler');
  for (const n of ['Bichlach', 'Yoga', 'Von Südosten', 'Um und durch das Haus']) expect(eg, n).not.toContain(n);
});

test('orbiting shows Eigene Ansicht; Von Südosten restores orbiting', async ({ page }) => {
  await open(page);
  await page.evaluate(() => window.__fl.lookFrom(-22, 34, 13));
  await expect(page.getByRole('button', { name: 'Standpunkt', exact: true })).toHaveText('Eigene Ansicht');
  await choose(page, 'Standpunkt', 'Stube');
  await choose(page, 'Standpunkt', 'Von Südosten');
  expect(await camAt(page)).toEqual([33, -24, 13]);
  expect(await page.evaluate(() => window.__fl.fov)).toBe(28);
  await page.mouse.move(640, 360);                                                  // orbit again: the camera moves
  await page.mouse.down();
  await page.mouse.move(500, 360, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(800);
  expect(distTo(await camAt(page), [33, -24, 13])).toBeGreaterThan(1);
});

test('a show.py view from above inside the walls still orbits and zooms (no look-around)', async ({ page }) => {
  await page.goto('/?cam=11.636,3.269,4.566&at=9.66,5.245,0.575&p=4&cut=eg');        // show.py EG_Ofen_Koerper
  await page.waitForFunction(() => window.__fl?.ready === true);
  const d0 = distTo(await camAt(page), [9.66, 5.245, 0.575]);
  await page.mouse.move(640, 360);
  await page.mouse.wheel(0, -400);                                                     // zoom in
  await page.waitForTimeout(800);
  expect(distTo(await camAt(page), [9.66, 5.245, 0.575])).toBeLessThan(d0 - 0.3);
});
