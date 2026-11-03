import { test, expect } from 'vitest';
import * as THREE from 'three';

test('vitest runs and three is installed', () => {
  expect(THREE.REVISION).toBe('187');
});
