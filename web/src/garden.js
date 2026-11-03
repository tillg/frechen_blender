// Garden from the shared layout (scene extras "garden"): meadow grass at 25 % of Blender's
// density within 30 m of the house, and the shrubs per stage (ink circle / clay blob / leaves).
// The windrose rectangles are ignored: the viewer draws no rose, so grass grows there.
import * as THREE from 'three/webgpu';
import { attribute, color, instancedBufferAttribute, mix, positionLocal, vec3 } from 'three/tsl';
import { CLAY, PAPER } from './materials.js';
import { INK } from './ink.js';

export const SHARE = 0.25;          // of Blender's render density
export const RADIUS = 30;           // m around the house

export function density(g, x, y) {
  const r = Math.hypot(x - g.HOUSE_C[0], y - g.HOUSE_C[1]);
  const t = Math.min(Math.max((r - g.NEAR) / (g.FAR - g.NEAR), 0), 1);
  return 1 - (1 - g.FAR_DENS) * t;
}

function rng(seed) {                 // mulberry32
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function poisson(mean, rand) {
  const l = Math.exp(-mean);
  let k = 0, p = rand();
  while (p > l) { k++; p *= rand(); }
  return k;
}

// clump positions in model coordinates (z-up); per CELL a Poisson count, like the emitter grid
export function scatterGrass(g, seed) {
  const rand = rng(seed), [x0, x1, y0, y1] = g.ground, c = g.CELL, out = [];
  for (let i = 0; x0 + i * c < x1; i++)
    for (let j = 0; y0 + j * c < y1; j++) {
      const ax = x0 + i * c, ay = y0 + j * c, mx = ax + c / 2, my = ay + c / 2;
      if (Math.hypot(mx - g.HOUSE_C[0], my - g.HOUSE_C[1]) > RADIUS - c) continue;
      if (g.no_grass.some(([a, b, cc, d]) => a < ax + c && ax < b && cc < ay + c && ay < d)) continue;
      const n = poisson(density(g, mx, my) * g.DENSITY * c * c * SHARE, rand);
      for (let k = 0; k < n; k++)
        out.push({ x: ax + rand() * c, y: ay + rand() * c, rz: rand() * 2 * Math.PI,
          tx: (rand() - 0.5) * 0.3, ty: (rand() - 0.5) * 0.3, s: 0.6 + rand() * 0.7 });
    }
  return out;
}

const yup = (x, y, z) => new THREE.Vector3(x, z, -y);
const LEAF = [[0, [0.012, 0.045, 0.008]], [0.6, [0.035, 0.12, 0.018]], [1, [0.10, 0.26, 0.035]]];
const GRASS = [[0, [0.015, 0.04, 0.008]], [0.45, [0.07, 0.20, 0.025]], [1, [0.28, 0.40, 0.07]]];

function rampJS(stops, t) {
  for (let i = 1; i < stops.length; i++) {
    const [t0, c0] = stops[i - 1], [t1, c1] = stops[i];
    if (t <= t1) return c0.map((v, k) => v + ((c1[k] - v) * (t - t0)) / (t1 - t0));
  }
  return stops.at(-1)[1];
}

function rampTSL(stops, t) {
  let col = color(...stops[0][1]);
  for (let i = 1; i < stops.length; i++) {
    const [t0] = stops[i - 1], [t1, c1] = stops[i];
    col = mix(col, color(...c1), t.sub(t0).div(t1 - t0).clamp(0, 1));
  }
  return col;
}

function grassMesh(g, clumpGeometry, uDetail) {
  const clumps = scatterGrass(g, 7);
  const m = new THREE.MeshStandardNodeMaterial({ side: THREE.DoubleSide, roughness: 0.6 });
  m.colorNode = rampTSL(GRASS, attribute('_h', 'float'));
  m.positionNode = positionLocal.mul(vec3(1, uDetail, 1));             // grows in with the detail
  const mesh = new THREE.InstancedMesh(clumpGeometry, m, clumps.length);
  const q = new THREE.Quaternion(), e = new THREE.Euler(), mat = new THREE.Matrix4(), s = new THREE.Vector3();
  clumps.forEach((c, i) => {
    q.setFromEuler(e.set(c.tx, -c.rz, c.ty, 'YXZ'));
    mat.compose(yup(c.x, c.y, g.ground[4]), q, s.setScalar(c.s));
    mesh.setMatrixAt(i, mat);
  });
  mesh.receiveShadow = true;
  return mesh;
}

// leaves on the surface of a rounded shrub, after bush() in garden.py (without its noise lobes)
function leaves(shrubs, uDetail, rand) {
  const n = 1400, geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute([1, 0, 0, 0, 0.45, 0, -1, 0, 0, 0, -0.45, 0], 3));
  geo.setIndex([0, 1, 2, 0, 2, 3]);
  geo.computeVertexNormals();
  // grow each leaf about its own centre: positionLocal is already instance-transformed here
  const centres = new Float32Array(3 * n * shrubs.length);
  const centre = instancedBufferAttribute(new THREE.InstancedBufferAttribute(centres, 3));   // r187: a bare array reads per vertex
  const m = new THREE.MeshStandardNodeMaterial({ side: THREE.DoubleSide, roughness: 0.55 });
  m.positionNode = centre.add(positionLocal.sub(centre).mul(uDetail));
  const mesh = new THREE.InstancedMesh(geo, m, n * shrubs.length);
  const gauss = () => Math.sqrt(-2 * Math.log(rand() || 1e-9)) * Math.cos(2 * Math.PI * rand());
  const mat = new THREE.Matrix4(), col = new THREE.Color();
  let i = 0;
  for (const [x, y, r, h] of shrubs)
    for (let k = 0; k < n; k++, i++) {
      const nv = new THREE.Vector3(gauss(), gauss(), gauss() + 0.35).normalize();
      const f = 0.86 + rand() * 0.14;
      const p = yup(x + nv.x * r * f, y + nv.y * r * f, -0.03 + Math.max(nv.z, -0.1) * h * f * 0.9 + h * 0.1);
      const out = yup(nv.x + gauss() * 0.5, nv.y + gauss() * 0.5, nv.z + gauss() * 0.5).normalize();
      const t1 = new THREE.Vector3().crossVectors(out, Math.abs(out.y) < 0.9 ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(1, 0, 0)).normalize();
      const t2 = new THREE.Vector3().crossVectors(out, t1);
      const sz = 0.028 + rand() * 0.022;
      mat.makeBasis(t1.multiplyScalar(sz), t2.multiplyScalar(sz), out.multiplyScalar(sz)).setPosition(p);
      mesh.setMatrixAt(i, mat);
      p.toArray(centres, 3 * i);
      mesh.setColorAt(i, col.setRGB(...rampJS(LEAF, rand() ** 0.8 * (0.6 + 0.4 * Math.max(nv.z, 0)))));
    }
  mesh.castShadow = true;
  return mesh;
}

export function buildGarden(bp, { uPaper, uDetail, uInk }) {
  const g = bp.extras.garden, group = new THREE.Group();
  const clump = bp.byName.GA_Grasbuschel;
  const grass = grassMesh(g, (clump.isMesh ? clump : clump.children[0]).geometry, uDetail);

  // shrub cores: clay blob in Massenmodell, dark leaf core in detail, paper in Skizze
  const blob = new THREE.MeshStandardNodeMaterial({ roughness: 0.9 });
  blob.colorNode = mix(color(CLAY), color(...LEAF[0][1]), uDetail).mul(uPaper.oneMinus());
  blob.emissiveNode = color(PAPER).mul(uPaper);
  const sphere = new THREE.SphereGeometry(1, 24, 16);
  const cores = g.shrubs.map(([x, y, r, h]) => {
    const m = new THREE.Mesh(sphere, blob);
    m.position.copy(yup(x, y, -0.03 + h * 0.1));
    m.scale.set(r * 0.85, h * 0.77, r * 0.85);
    m.castShadow = m.receiveShadow = true;
    return m;
  });

  // Skizze: one ink circle per shrub
  const ink = new THREE.LineBasicNodeMaterial({ color: INK, transparent: true, depthWrite: false });
  ink.opacityNode = uInk;
  const circles = new THREE.Group();
  for (const [x, y, r] of g.shrubs) {
    const pts = Array.from({ length: 49 }, (_, k) => {         // closed: last point = first
      const a = (k / 48) * 2 * Math.PI;
      return yup(x + r * Math.cos(a), y + r * Math.sin(a), 0.02);
    });
    circles.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), ink));   // no LineLoop in WebGPU
  }

  const leafMesh = leaves(g.shrubs, uDetail, rng(11));
  const blobs = new THREE.Group().add(...cores);
  group.add(grass, leafMesh, circles, blobs);
  return {
    group,
    update(w) {
      const d = w.detail + w.built;
      grass.visible = leafMesh.visible = d > 0.001;
      circles.visible = w.sketch + w.massing > 0.001;
      blobs.visible = w.sketch < 0.999;              // pure Skizze: the circles alone
    },
    get state() {
      return { shrubs: cores.length, layoutShrubs: g.shrubs.length, grassCount: grass.count,
        grassVisible: grass.visible, leavesVisible: leafMesh.visible, circlesVisible: circles.visible,
        blobsVisible: blobs.visible };
    },
  };
}
