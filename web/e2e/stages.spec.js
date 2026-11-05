import { test, expect } from '@playwright/test';
import { shot } from './pixels.js';

const luma = (d, i) => 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];

// share of pixels that are ink (dark) and that are mid-tone (shading, shadows, clay in light)
function tones(img) {
  let ink = 0, mid = 0;
  const n = img.width * img.height;
  for (let i = 0; i < 4 * n; i += 4) {
    const l = luma(img.data, i);
    if (l < 110) ink++;
    else if (l < 205) mid++;
  }
  return { ink: ink / n, mid: mid / n };
}

async function open(page) {
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
}

async function at(page, p) {
  await page.evaluate((p) => window.__fl.setProgress(p), p);
  await page.waitForTimeout(400);
}

test('Skizze is hidden-line: ink on paper, no shading', async ({ page }) => {
  await open(page);
  await at(page, 0);
  expect(await page.evaluate(() => window.__fl.linesVisible)).toBe(true);
  const sk = tones(await shot(page, 'skizze.png'));
  await at(page, 1);
  const ms = tones(await shot(page, 'massing.png'));
  expect(sk.ink).toBeGreaterThan(0.01);
  expect(sk.mid).toBeLessThan(0.05);              // only anti-aliasing between ink and paper
  expect(ms.mid).toBeGreaterThan(2 * sk.mid);     // massing has shaded clay and shadows (measured 2.5×)
  expect(await page.evaluate(() => window.__fl.linesVisible)).toBe(true);   // fade out across 1→2
  await at(page, 2);
  expect(await page.evaluate(() => window.__fl.linesVisible)).toBe(false);
});

test('Skizze hides interior lines', async ({ page }) => {
  await open(page);
  await at(page, 0);
  const shown = tones(await shot(page, 'skizze.png')).ink;
  await page.evaluate(() => window.__fl.setSurfaces(false));
  await page.waitForTimeout(400);
  const xray = tones(await shot(page, 'skizze_xray.png')).ink;
  expect(shown).toBeLessThan(0.8 * xray);
});

// mean colour of a 7×7 CSS-pixel patch around a model point (z-up metres)
async function patch(page, img, x, y, z) {
  const s = await page.evaluate((p) => window.__fl.project(...p), [x, y, z]);
  const acc = [0, 0, 0];
  for (let dy = -3; dy <= 3; dy++)
    for (let dx = -3; dx <= 3; dx++) {
      const i = 4 * (Math.round(s.y + dy) * img.width + Math.round(s.x + dx));
      for (let k = 0; k < 3; k++) acc[k] += img.data[i + k] / 49;
    }
  return acc;
}

test('Detailmodell is coloured: blue shutters, larch cladding', async ({ page }) => {
  await open(page);
  await at(page, 2);
  const se = await shot(page, 'detail.png');
  const [r, , b] = await patch(page, se, 3.6, -0.031, 1.5);         // south EG shutter
  expect(b).toBeGreaterThan(r + 15);
  await page.evaluate(() => window.__fl.lookFrom(-22, 34, 13));
  await page.waitForTimeout(500);
  const nw = await shot(page, 'detail_nw.png');
  const [r2, , b2] = await patch(page, nw, -0.08, 9.0, 3.5);         // west larch cladding
  expect(r2).toBeGreaterThan(b2 + 25);
  for (const [name, p] of [['detail_west_close.png', [-7, 10, 3]], ['detail_shutters_close.png', [4.5, -6, 2]]]) {
    await page.evaluate((p) => window.__fl.lookFrom(...p), p);      // close-ups for the eye
    await page.waitForTimeout(500);
    await shot(page, name);
  }
});

test('garden per stage: circles, clay blobs, then grass and leaves', async ({ page }) => {
  await open(page);
  const g = () => page.evaluate(() => window.__fl.garden);
  await at(page, 0);
  let s = await g();
  expect(s.shrubs).toBe(s.layoutShrubs);                      // one shrub per layout entry
  // Skizze: only the circles (a paper blob would hide them)
  expect(s).toMatchObject({ grassVisible: false, circlesVisible: true, leavesVisible: false, blobsVisible: false });
  await at(page, 1);
  expect(await g()).toMatchObject({ grassVisible: false, leavesVisible: false, blobsVisible: true });
  await at(page, 2);
  s = await g();
  expect(s).toMatchObject({ grassVisible: true, leavesVisible: true, circlesVisible: false });
  expect(s.grassCount).toBeGreaterThan(1000);
  const ms = await page.evaluate(async () => {                // mean frame time over 30 frames
    const t0 = performance.now();
    for (let i = 0; i < 30; i++) await new Promise((r) => requestAnimationFrame(r));
    return (performance.now() - t0) / 30;
  });
  console.log(`grassCount ${s.grassCount}, mean frame ${ms.toFixed(1)} ms (headless Chromium, WebGL2 on GPU)`);
  await shot(page, 'detail.png');
});

test('no grass while the camera is indoors, except in the Rundgang', async ({ page }) => {
  await open(page);
  await at(page, 2);
  const grass = () => page.evaluate(() => window.__fl.garden.grassVisible);
  await page.evaluate(() => window.__fl.lookFrom(7.25, 0.6, 1.6));      // Küche
  await page.waitForTimeout(300);
  expect(await grass()).toBe(false);
  await page.evaluate(() => window.__fl.lookFrom(33, -24, 13));         // outside again
  await page.waitForTimeout(300);
  expect(await grass()).toBe(true);
  // the film keeps everything: a tour frame inside the house still has the grass
  await page.getByRole('button', { name: 'Rundgang', exact: true }).click();
  await page.evaluate(() => {
    const T = window.__fl.tour.duration;
    for (let i = 0; ; i++) {
      const [x, y] = window.__fl.tourKey(i);
      if (x > 1 && x < 13 && y > 1 && y < 11) return window.__fl.tour.seek(i / 25);
      if (i / 25 > T) throw new Error('no indoor tour frame');
    }
  });
  await page.waitForTimeout(300);
  expect(await grass()).toBe(true);
});

// leaf-green pixels (green clearly above red and blue) within r CSS px of a model point
async function greenAround(page, img, [x, y, z], r) {
  const s = await page.evaluate((p) => window.__fl.project(...p), [x, y, z]);
  let n = 0;
  for (let dy = -r; dy <= r; dy++)
    for (let dx = -r; dx <= r; dx++) {
      const i = 4 * (Math.round(s.y + dy) * img.width + Math.round(s.x + dx));
      const [R, G, B] = img.data.slice(i, i + 3);
      if (G > R + 8 && G > B + 8) n++;
    }
  return n;
}

test('shrub leaves stay in the beds mid-transition', async ({ page }) => {
  await open(page);
  await at(page, 1.5);                                       // uDetail 0.5: leaves half grown
  await page.evaluate(() => { window.__fl.setSurfaces(false); window.__fl.lookFrom(7.6, 6.0, 45); });
  await page.waitForTimeout(500);
  const img = await shot(page, 'leaves_mid.png');
  let inside = 0;                                            // no grass, blobs or leaves in the footprint
  for (let x = 1.5; x < 14; x += 1.5) for (let y = 1.5; y < 12; y += 1.5) inside += await greenAround(page, img, [x, y, 0.3], 12);
  expect(inside).toBe(0);
  expect(await greenAround(page, img, [15.32, 9.5, 0.3], 25)).toBeGreaterThan(20);   // east bed
  expect(await greenAround(page, img, [-0.36, 10.7, 0.3], 25)).toBeGreaterThan(20);  // west bed
});

test('Gebaut is darker outside, with warm windows', async ({ page }) => {
  await open(page);
  const sky = (img) => {                                   // mean luma of the top 15 % (sky)
    let s = 0, n = 0;
    for (let i = 0; i < img.width * Math.floor(img.height * 0.15) * 4; i += 16, n++) s += luma(img.data, i);
    return s / n;
  };
  await at(page, 2);
  const day = await shot(page, 'detail.png');
  await at(page, 3);
  const dusk = await shot(page, 'gebaut.png');
  expect(sky(dusk)).toBeLessThan(sky(day) - 40);
  const [r, , b] = await patch(page, dusk, 11.3, 0.2, 1.2);    // Stube glazed doors, light behind
  expect(r).toBeGreaterThan(b + 10);
});

test('no lines for smooth objects (pebbles, lamps)', async ({ page }) => {
  await open(page);
  const src = await page.evaluate(() => window.__fl.lineSources);
  expect(src).toContain('EG_Waende');
  expect(src).not.toContain('Kiesel');
  expect(src).not.toContain('Aussenleuchten');
});
