/**
 * Deterministic RNG with named substreams.
 *
 * Every stochastic choice in the simulation draws from a stream derived from
 * (seed, streamName). Nothing in the simulation may call Math.random or read
 * the clock. This is what makes §4.2 criterion 3 (reproducible-in-kind)
 * testable: same seed + different noise stream = same world, different luck.
 */

function fnv1a(str: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/** sfc32 — small fast counter PRNG, good statistical quality for sim work. */
export class RNG {
  private a: number;
  private b: number;
  private c: number;
  private d: number;

  constructor(seed: number, stream: string) {
    const s = fnv1a(`${seed}:${stream}`);
    this.a = s ^ 0x9e3779b9;
    this.b = fnv1a(`${stream}:${seed}`) ^ 0x85ebca6b;
    this.c = Math.imul(s, 0xc2b2ae35) >>> 0;
    this.d = seed >>> 0 || 1;
    // warm up past correlated initial state
    for (let i = 0; i < 12; i++) this.next();
  }

  /** uniform in [0, 1) */
  next(): number {
    this.a >>>= 0; this.b >>>= 0; this.c >>>= 0; this.d >>>= 0;
    let t = (this.a + this.b) | 0;
    this.a = this.b ^ (this.b >>> 9);
    this.b = (this.c + (this.c << 3)) | 0;
    this.c = (this.c << 21) | (this.c >>> 11);
    this.d = (this.d + 1) | 0;
    t = (t + this.d) | 0;
    this.c = (this.c + t) | 0;
    return (t >>> 0) / 4294967296;
  }

  int(n: number): number {
    return Math.floor(this.next() * n);
  }

  range(lo: number, hi: number): number {
    return lo + this.next() * (hi - lo);
  }

  /** standard normal via Box–Muller */
  normal(mean = 0, sd = 1): number {
    const u = Math.max(this.next(), 1e-12);
    const v = this.next();
    return mean + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  /** Gumbel noise for perturbing candidate scores (§3.4 exploration noise) */
  gumbel(): number {
    const u = Math.max(this.next(), 1e-12);
    return -Math.log(-Math.log(u));
  }

  pick<T>(arr: T[]): T {
    return arr[this.int(arr.length)];
  }

  shuffle<T>(arr: T[]): T[] {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = this.int(i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }
}
