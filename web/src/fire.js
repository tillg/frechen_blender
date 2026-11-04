// Flickering fire, the viewer side of code/fire.py: the core's fire beds (scene extras "fires":
// base, u, w, h, d and the component's tongues) and the flame outline and colours ("fire").
// Each tongue is a flat teardrop (outer + a smaller, brighter core) that leaps, breathes and
// sways; tick(seconds) moves them. No light of its own (the tour's frame rate).
import * as THREE from 'three/webgpu';
import { color } from 'three/tsl';

const yup = ([x, y, z]) => new THREE.Vector3(x, z, -y);        // model z-up -> three.js y-up
const wave = (t, s, p) => 0.6 * Math.sin(2 * Math.PI * 1.7 * s * t + p) + 0.4 * Math.sin(2 * Math.PI * 3.1 * s * t + 1.3 * p + 1);

function material({ rgba, emit }) {
  const m = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
  m.colorNode = color(rgba[0], rgba[1], rgba[2]).mul(emit);
  return m;
}

export function createFire(extras) {
  const group = new THREE.Group();
  group.name = 'Feuer';
  const tongues = [];
  if (extras.fires) {
    const shape = new THREE.Shape(extras.fire.profile.map(([x, z]) => new THREE.Vector2(x, z)));
    const geo = new THREE.ShapeGeometry(shape);
    const [cw, ch] = extras.fire.core;
    const outer = material(extras.fire.outer), inner = material(extras.fire.inner);
    for (const f of extras.fires) {
      const g = new THREE.Group();
      g.position.copy(yup(f.base));
      g.rotation.y = Math.atan2(f.u[1], f.u[0]);
      for (const t of f.tongues) {
        for (const [mat, sw, sh, dz, dp] of [[outer, 1, 1, 0, 0], [inner, cw, ch, -0.3 * f.d, 1.7]]) {
          const m = new THREE.Mesh(geo, mat);
          m.position.set(t.u, 0, dz);                  // local -z faces the viewer (towards the room)
          m.userData = { w: t.w * sw, h: t.h * sh, phase: t.phase + dp, speed: t.speed };
          g.add(m);
          tongues.push(m);
        }
      }
      group.add(g);
    }
  }
  function tick(seconds) {
    for (const m of tongues) {
      const { w, h, phase, speed } = m.userData;
      m.scale.set(w * (1 + 0.12 * wave(seconds, speed * 0.8, phase + 3)), h * (1 + 0.3 * wave(seconds, speed, phase)), 1);
      m.rotation.z = 0.12 * wave(seconds, speed * 0.6, phase + 5);
    }
  }
  tick(0);
  return { group, tick };
}
