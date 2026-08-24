import { M1, P } from '../core/params.js';
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

export function generateWorld(seed: number, m1 = false): WorldState {
  const rng = new RNG(seed, 'worldgen');
  const size = P.WORLD;
  const elevation = valueNoise(rng, size);
  if (m1) return generateWorldM1(seed, rng, size, elevation);

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

/**
 * M1 world (SPEC-M1 §2, §3.4): scaled for 60–200 agents, with pith arranged
 * as three sites of IDENTICAL node count, cap, and regen, rotationally
 * symmetric about the map centre. Which site an agent favours is a choice
 * with no expected-value difference — the fitness-neutral degree of freedom
 * the milestone measures. A seed-derived rotation varies the geometry across
 * seeds without breaking the symmetry.
 */
function generateWorldM1(seed: number, rng: RNG, size: number,
                         elevation: Float32Array): WorldState {
  const nodes: ResourceNode[] = [];
  let nid = 0;
  const cx0 = size / 2, cy0 = size / 2;
  const clamp = (v: number) => Math.max(1, Math.min(size - 2, Math.round(v)));

  // kind 1 — pith: the three-way symmetric sites
  const theta0 = rng.next() * 2 * Math.PI;
  const siteCenters: [number, number][] = [];
  for (let s = 0; s < M1.PITH_SITES; s++) {
    const th = theta0 + (s * 2 * Math.PI) / M1.PITH_SITES;
    siteCenters.push([clamp(cx0 + M1.PITH_SITE_RADIUS * Math.cos(th)),
                      clamp(cy0 + M1.PITH_SITE_RADIUS * Math.sin(th))]);
  }
  for (const [sx, sy] of siteCenters) {
    for (let i = 0; i < M1.PITH_PER_SITE; i++) {
      nodes.push({
        id: nid++, k: 1,
        x: clamp(sx + rng.normal(0, M1.PITH_SPREAD)),
        y: clamp(sy + rng.normal(0, M1.PITH_SPREAD)),
        q: M1.PITH_CAP * rng.range(0.5, 1),
      });
    }
  }

  // kinds 0 and 2 — scaled up for the larger population, organic clusters
  const scaled: { k: Kind; n: number; clusters: number; cap: number;
                  spread: number }[] = [
    { k: 0, n: M1.THREN_NODES, clusters: M1.THREN_CLUSTERS, cap: M1.THREN_CAP,
      spread: P.RESOURCES[0].clusterSpread },
    { k: 2, n: M1.OSK_NODES, clusters: M1.OSK_CLUSTERS, cap: M1.OSK_CAP,
      spread: P.RESOURCES[2].clusterSpread },
  ];
  for (const spec of scaled) {
    const centers: [number, number][] = [];
    for (let c = 0; c < spec.clusters; c++) {
      centers.push([4 + rng.int(size - 8), 4 + rng.int(size - 8)]);
    }
    const per = Math.ceil(spec.n / spec.clusters);
    let placed = 0;
    for (const [ccx, ccy] of centers) {
      for (let i = 0; i < per && placed < spec.n; i++, placed++) {
        nodes.push({
          id: nid++, k: spec.k,
          x: clamp(ccx + rng.normal(0, spec.spread)),
          y: clamp(ccy + rng.normal(0, spec.spread)),
          q: spec.cap * rng.range(0.5, 1),
        });
      }
    }
  }

  return { tick: 0, nodes, caches: [], spills: [], signals: [], elevation,
           siteCenters };
}

/** M1 node parameters (cap/regen) by kind — used by world rules and reports */
export function m1NodeSpec(k: Kind): { cap: number; regen: number } {
  if (k === 1) return { cap: M1.PITH_CAP, regen: M1.PITH_REGEN };
  if (k === 0) return { cap: M1.THREN_CAP, regen: M1.THREN_REGEN };
  return { cap: M1.OSK_CAP, regen: M1.OSK_REGEN };
}
