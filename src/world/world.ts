import { P } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type { Kind, ResourceNode, WorldState } from '../core/types.js';

/**
 * World generation and world rules.
 *
 * All of this is derived from the seed (not the noise stream), so two runs
 * with the same seed and different streams share an identical map — the
 * setup for §4.2 criterion 3.
 */

export function atmosphere(tick: number): number {
  // smooth 0..1 scalar; the "open" phase for kind 0 is where it exceeds a
  // threshold. Agents perceive the scalar itself, never a phase name (§2.2).
  const phase = (tick % P.ATMOS_PERIOD) / P.ATMOS_PERIOD;
  return 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
}

export function kind0Open(tick: number): boolean {
  // open for exactly ATMOS_OPEN ticks per period, centered on the peak
  const t = tick % P.ATMOS_PERIOD;
  const peak = P.ATMOS_PERIOD / 2;
  return Math.abs(t - peak) <= P.ATMOS_OPEN / 2;
}

export function nodeOpen(k: Kind, tick: number): boolean {
  return !P.RESOURCES[k].seasonal || kind0Open(tick);
}

function valueNoise(rng: RNG, size: number): Float32Array {
  // simple multi-octave value noise for the viewer's terrain wash (L0 comes
  // much later; this gates nothing).
  const out = new Float32Array(size * size);
  for (const cell of [16, 8, 4]) {
    const gw = Math.ceil(size / cell) + 1;
    const grid = new Float32Array(gw * gw);
    for (let i = 0; i < grid.length; i++) grid[i] = rng.next();
    const amp = cell / 28;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const gx = x / cell, gy = y / cell;
        const x0 = Math.floor(gx), y0 = Math.floor(gy);
        const fx = gx - x0, fy = gy - y0;
        const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
        const v00 = grid[y0 * gw + x0], v10 = grid[y0 * gw + x0 + 1];
        const v01 = grid[(y0 + 1) * gw + x0], v11 = grid[(y0 + 1) * gw + x0 + 1];
        out[y * size + x] +=
          amp * ((v00 * (1 - sx) + v10 * sx) * (1 - sy) +
                 (v01 * (1 - sx) + v11 * sx) * sy);
      }
    }
  }
  let max = 0;
  for (const v of out) max = Math.max(max, v);
  for (let i = 0; i < out.length; i++) out[i] /= max;
  return out;
}

export function generateWorld(seed: number): WorldState {
  const rng = new RNG(seed, 'worldgen');
  const size = P.WORLD;
  const elevation = valueNoise(rng, size);

  const nodes: ResourceNode[] = [];
  let nid = 0;
  for (let k = 0 as Kind; k < 3; k++) {
    const spec = P.RESOURCES[k];
    const nClusters = P.N_CLUSTERS[k];
    const centers: [number, number][] = [];
    for (let c = 0; c < nClusters; c++) {
      centers.push([4 + rng.int(size - 8), 4 + rng.int(size - 8)]);
    }
    const perCluster = Math.ceil(spec.nodes / nClusters);
    let placed = 0;
    for (const [cx, cy] of centers) {
      for (let i = 0; i < perCluster && placed < spec.nodes; i++, placed++) {
        const x = Math.max(0, Math.min(size - 1,
          Math.round(cx + rng.normal(0, spec.clusterSpread))));
        const y = Math.max(0, Math.min(size - 1,
          Math.round(cy + rng.normal(0, spec.clusterSpread))));
        nodes.push({ id: nid++, x, y, k: k as Kind, q: spec.cap * rng.range(0.5, 1) });
      }
    }
  }

  return { tick: 0, nodes, caches: [], spills: [], signals: [], elevation };
}
