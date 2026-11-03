// Screenshot the page and decode it in the browser: { width, height, data } (RGBA, 1x CSS pixels).
import { mkdirSync } from 'node:fs';

export const SHOTS = new URL('../../tmp/web/', import.meta.url).pathname;

export async function shot(page, name) {
  mkdirSync(SHOTS, { recursive: true });
  const png = await page.screenshot({ path: SHOTS + name, scale: 'css' });
  return page.evaluate(async (b64) => {
    const img = new Image();
    img.src = 'data:image/png;base64,' + b64;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = img.width; c.height = img.height;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    return { width: c.width, height: c.height, data: Array.from(ctx.getImageData(0, 0, c.width, c.height).data) };
  }, png.toString('base64'));
}

export function pixel(img, x, y) {
  const i = 4 * (Math.round(y) * img.width + Math.round(x));
  return img.data.slice(i, i + 3);
}
