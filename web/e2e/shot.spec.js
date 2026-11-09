// web/shot.js: one headless screenshot of a Show URL (code/show.py), Claude's own look.
import { test, expect } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import { SHOTS } from './pixels.js';

const ROOT = new URL('../../', import.meta.url).pathname;

test('shot.js writes a screenshot of the URL', async ({ page }) => {
  const url = execFileSync(ROOT + '.venv/bin/python', [ROOT + 'code/show.py', 'EG_Haustuer', '--print'],
    { encoding: 'utf8' }).trim();
  expect(url).toMatch(/^http:\/\/localhost:5377\/\?cam=/);
  const png = SHOTS + 'shot-haustuer.png';
  rmSync(png, { force: true });
  execFileSync('node', [ROOT + 'web/shot.js', url, png], { cwd: ROOT + 'web', timeout: 90_000 });
  expect(existsSync(png)).toBe(true);
  // decode it in the browser: 1280x720 and not one flat colour
  await page.goto('about:blank');
  const { w, h, colours } = await page.evaluate(async (b64) => {
    const img = new Image();
    img.src = 'data:image/png;base64,' + b64;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = img.width; c.height = img.height;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const d = ctx.getImageData(0, 0, c.width, c.height).data, seen = new Set();
    for (let i = 0; i < d.length; i += 4 * 97) seen.add((d[i] >> 4) << 8 | (d[i + 1] >> 4) << 4 | d[i + 2] >> 4);
    return { w: img.width, h: img.height, colours: seen.size };
  }, (await import('node:fs')).readFileSync(png).toString('base64'));
  expect([w, h]).toEqual([1280, 720]);
  expect(colours).toBeGreaterThan(20);
});
