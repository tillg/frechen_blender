// Plan versions (issue #59, ADR-005-JXWL; no three.js): the list versionen.json ([{id, name}],
// newest first, written by code/versionen.py build), the one chosen by ?v=<id> (none or an unknown id:
// Aktuell, the live model) and where its files are (v/<id>/frechenlehen.glb, v/<id>/plans/).

// the list, or [] where there is none (a build without versions, offline without it)
export async function loadVersions(base) {
  try {
    const r = await fetch(`${base}versionen.json`);
    return r.ok ? await r.json() : [];
  } catch {
    return [];
  }
}

// the chosen version, or null for Aktuell
export const pick = (list, search) => list.find((v) => v.id === new URLSearchParams(search).get('v')) ?? null;

// the directory the house .glb and the plan sheets come from
export const dataBase = (base, version) => (version ? `${base}v/${version.id}/` : base);

// the query with v set to id (null: removed), the other pairs kept as they are (cam=x,y,z unescaped)
export function versionHref(search, id) {
  const kept = (search ?? '').replace(/^\?/, '').split('&').filter((kv) => kv && kv.split('=')[0] !== 'v');
  if (id) kept.push(`v=${encodeURIComponent(id)}`);
  return kept.length ? `?${kept.join('&')}` : '';
}

// "2026-11-25 Nach Vincent & Silvia-Ideen"
export const versionLabel = (v) => `${v.id} ${v.name}`;
