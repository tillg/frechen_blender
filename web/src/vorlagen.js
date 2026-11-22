// The photo pages (vorlagen.html, issue #31): the reference pictures of code/vorlagen.py, sorted by
// Bereich. Without ?b= the index of all Bereiche (cover picture, count), with ?b=<key> the Bereich's
// pictures with captions; a click opens the copy at full size. The manifest is public/vorlagen.json
// (npm run blueprint), the copies are public/vorlagen/<key>/<file>.
import { pageUrl, pickBereich } from './vorlagen-data.js';
import './offline.js';

const base = import.meta.env.BASE_URL;
const res = await fetch(`${base}vorlagen.json`);
if (!res.ok) throw new Error(`vorlagen.json: ${res.status}`);
const manifest = await res.json();
const b = pickBereich(manifest, location.search);
const src = (key, f) => `${base}vorlagen/${key}/${f.file}`;

function el(tag, attrs = {}, text = '') {
  const e = Object.assign(document.createElement(tag), attrs);
  if (text) e.textContent = text;
  return e;
}
function card(href, img, alt, title, sub) {
  const fig = el('figure');
  const a = el('a', { href });
  a.append(el('img', { src: img, alt, loading: 'lazy' }));
  const cap = el('figcaption');
  cap.append(el(title.tag, {}, title.text), el('small', {}, sub));
  a.append(cap);
  fig.append(a);
  return fig;
}

// header and the links: the 3D house, the index, every Bereich
document.title = `Frechenlehen – ${b ? b.title : 'Fotos & Vorlagen'}`;
document.querySelector('header h1').textContent = b ? b.title : 'Fotos & Vorlagen';
document.querySelector('header p').textContent = b
  ? `Vorlagen – ${b.fotos.length} ${b.fotos.length === 1 ? 'Bild' : 'Bilder'}`
  : 'Die Bilder, nach denen das Haus gebaut ist, nach Bereichen';
const nav = document.querySelector('nav');
nav.append(el('a', { href: './' }, '3D-Haus'), el('a', { href: pageUrl() }, 'Alle Bereiche'));
for (const x of manifest.bereiche) {
  const a = el('a', { href: pageUrl(x.key) }, x.title);
  if (x === b) a.setAttribute('aria-current', 'page');
  nav.append(a);
}

const grid = document.querySelector('.grid');
if (b) {
  for (const f of b.fotos) grid.append(card(src(b.key, f), src(b.key, f), f.caption, { tag: 'span', text: f.caption }, f.src.split('/').pop()));
} else {
  grid.classList.add('bereich');
  for (const x of manifest.bereiche)
    grid.append(card(pageUrl(x.key), src(x.key, x.fotos[0]), x.title, { tag: 'strong', text: x.title },
      `${x.fotos.length} ${x.fotos.length === 1 ? 'Bild' : 'Bilder'}`));
}
if (import.meta.env.MODE !== 'production') window.__vorlagen = { ready: true };   // test hook (shot.js, e2e)
