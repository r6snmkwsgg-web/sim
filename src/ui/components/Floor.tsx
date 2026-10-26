// The landing page's header: a maple floor seen from above, with the half-court
// line, the sideline and the name painted on the apron like a real court.

const W = 1600;
const H = 640;
/** One maple strip, in viewBox units (about 10px tall on a laptop). */
const STRIP = 11;

/** Small seeded generator so the floor looks the same on every visit. */
function seeded(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

interface Plank {
  x: number;
  y: number;
  w: number;
  fill: string;
}

function layPlanks(): Plank[] {
  const r = seeded(1947);
  const out: Plank[] = [];
  for (let y = 0; y < H; y += STRIP) {
    // stagger the end joints from row to row
    let x = -r() * 420;
    while (x < W) {
      const w = 170 + r() * 380;
      // maple under a gym finish: honey-gold, with the odd darker strip
      const dark = r() < 0.05;
      const hue = 30 + r() * 5;
      const sat = 46 + r() * 12;
      const light = dark ? 54 + r() * 4 : 61 + r() * 8;
      out.push({ x, y, w, fill: `hsl(${hue.toFixed(1)} ${sat.toFixed(0)}% ${light.toFixed(1)}%)` });
      x += w;
    }
  }
  return out;
}

const PLANKS = layPlanks();

export function Floor({ title }: { title: string }) {
  return (
    <header className="floor">
      <svg className="floor-wood" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMax slice" aria-hidden>
        {PLANKS.map((p, i) => (
          <rect key={i} x={p.x} y={p.y} width={p.w} height={STRIP} fill={p.fill} />
        ))}
        {PLANKS.map((p, i) => (
          <rect key={`j${i}`} x={p.x} y={p.y} width={1.4} height={STRIP} fill="rgba(70, 38, 14, 0.38)" />
        ))}
        {Array.from({ length: Math.ceil(H / STRIP) }, (_, i) => (
          <rect key={`s${i}`} x={0} y={i * STRIP} width={W} height={0.8} fill="rgba(70, 38, 14, 0.2)" />
        ))}
      </svg>
      <div className="floor-mid" />
      <div className="floor-apron">
        <h1 className="floor-word">{title}</h1>
      </div>
      {/* wood grain over everything, paint included: stretched noise so it runs along the strips */}
      <svg className="floor-grain" aria-hidden>
        <filter id="floor-grain" x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.003 0.16" numOctaves="3" seed="7" />
          <feColorMatrix values="0 0 0 0 0.30  0 0 0 0 0.17  0 0 0 0 0.07  1.8 0 0 0 -0.75" />
        </filter>
        <rect width="100%" height="100%" filter="url(#floor-grain)" />
      </svg>
      <div className="floor-light" />
    </header>
  );
}
