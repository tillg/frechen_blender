// The Ofen sub-model page (ofen.html): line drawing of house_core.build_ofen() with its dimensions.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { shot } from './pixels.js';

const glb = readFileSync(new URL('../public/ofen.glb', import.meta.url));
const DIMS = JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString()).scenes[0].extras.dims;

test('Ofen page draws the stove with the core dimensions, without errors', async ({ page }) => {
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/ofen.html');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  expect(await page.evaluate(() => window.__ofen.edges)).toBeGreaterThan(50);
  await expect(page.locator('.dim')).toHaveCount(DIMS.length);
  await expect(page.locator('.dim', { hasText: 'Tür 65' })).toBeVisible();
  await page.getByRole('button', { name: 'Von oben' }).click();
  await expect(page.locator('.dim', { hasText: 'Höhe' })).toBeHidden();      // heights: not in the plan
  await expect(page.locator('.dim', { hasText: 'Bett 190' })).toBeVisible();
  const img = await shot(page, 'ofen_e2e_top.png');
  let ink = 0;
  for (let i = 0; i < img.data.length; i += 16) if (img.data[i] < 110) ink++;
  expect(ink).toBeGreaterThan(20);                                               // lines are drawn
  expect(errors).toEqual([]);
});

test('Ofen looks: Drahtmodell, Masse, Gerendert (fire behind the glass)', async ({ page }) => {
  await page.goto('/ofen.html');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  await page.getByRole('button', { name: 'Auf die Feuertür' }).click();
  const fire = async (name) => {
    await page.getByRole('button', { name }).click();
    expect(await page.evaluate(() => window.__ofen.look())).toBe({ Drahtmodell: 'wire', Masse: 'mass', Gerendert: 'full' }[name]);
    await page.waitForTimeout(800);
    const img = await shot(page, `ofen_e2e_${name}.png`);
    let n = 0;
    for (let i = 0; i < img.data.length; i += 4) if (img.data[i] > 200 && img.data[i + 1] > 90 && img.data[i + 1] < 190 && img.data[i + 2] < 90) n++;
    return n;
  };
  expect(await fire('Masse')).toBe(0);                                          // clay: no colours
  expect(await fire('Gerendert')).toBeGreaterThan(2000);                        // orange flames
  expect(await fire('Drahtmodell')).toBe(0);
});

test('"← Haus" leads back to the house', async ({ page }) => {
  await page.goto('/ofen.html');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  await page.getByRole('link', { name: '← Haus' }).click();
  await page.waitForFunction(() => window.__fl?.ready === true);
  expect(new URL(page.url()).pathname).toBe('/');
});

test('house and Ofen page share the menu style (title panel, toolbar, link, pressed button)', async ({ page }) => {
  const look = () => page.evaluate(() => {
    const css = (sel, keys) => { const s = getComputedStyle(document.querySelector(sel)); return keys.map((k) => s[k]); };
    return {
      title: css('.fl-title', ['top', 'left', 'backgroundColor', 'borderRadius', 'boxShadow']),
      h1: css('.fl-title h1', ['fontFamily', 'fontSize']),
      tools: css('.fl-tools', ['top', 'right', 'backgroundColor', 'borderRadius', 'padding', 'fontSize']),
      link: css('.fl-tools a', ['padding', 'borderRadius', 'fontSize', 'color', 'textDecorationLine']),
      button: css('.fl-tools button:not([aria-pressed="true"])', ['padding', 'borderRadius', 'backgroundColor']),
      pressed: css('.fl-tools button[aria-pressed="true"]', ['backgroundColor', 'color']),
    };
  });
  await page.goto('/');
  await page.waitForFunction(() => window.__fl?.ready === true);
  const house = await look();
  await page.goto('/ofen.html');
  await page.waitForFunction(() => window.__ofen?.ready === true);
  expect(await look()).toEqual(house);
  await page.getByRole('button', { name: 'Auf die Feuertür' }).click();       // dimension labels stay below
  await page.waitForTimeout(800);
  await page.addStyleTag({ content: '.dim { pointer-events: auto !important; }' });   // so elementFromPoint sees them
  expect(await page.evaluate(() => [...document.querySelectorAll('.fl-tools > *')].every((e) => {
    const r = e.getBoundingClientRect();
    return e.contains(document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2));
  }))).toBe(true);
});
