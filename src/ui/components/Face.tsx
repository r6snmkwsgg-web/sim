import { memo } from "react";
import { display, generate } from "facesjs";
import type { FaceConfig } from "facesjs";
import type { Race } from "../../engine/types";

const faceCache = new Map<string, FaceConfig>();
const svgCache = new Map<string, string>();
const JERSEYS = ["jersey", "jersey2", "jersey3", "jersey4", "jersey5"];

function seeded(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    let t = (s = (s + 0x6d2b79f5) >>> 0);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Deterministic face from a seed (facesjs uses Math.random internally). */
export function faceFor(seed: number, race: Race): FaceConfig {
  const key = `${seed}:${race}`;
  const hit = faceCache.get(key);
  if (hit) return hit;
  const orig = Math.random;
  const rnd = seeded(seed);
  Math.random = rnd;
  let f: FaceConfig;
  try {
    const acc = rnd();
    f = generate(
      {
        jersey: { id: JERSEYS[Math.floor(rnd() * JERSEYS.length)] },
        accessories: { id: acc < 0.12 ? "headband" : acc < 0.18 ? "headband-high" : "none" },
      },
      { race },
    );
  } finally {
    Math.random = orig;
  }
  faceCache.set(key, f);
  return f;
}

let stage: HTMLDivElement | null = null;

/**
 * facesjs draws on a 400x600 canvas: empty space above the hair (y < ~60),
 * the head from ~60 to ~510, and the shoulders/jersey below that.
 * "bust" frames head and shoulders; "head" is a square crop around the whole head.
 */
const CROPS = {
  bust: { viewBox: "0 48 400 552", ratio: 552 / 400 },
  head: { viewBox: "-25 58 450 450", ratio: 1 },
} as const;
export type FaceCrop = keyof typeof CROPS;

/** facesjs needs a live DOM node (it measures paths), so render offscreen and keep the markup. */
function renderSvg(face: FaceConfig, teamColors: [string, string, string], crop: FaceCrop): string {
  if (!stage) {
    stage = document.createElement("div");
    stage.style.cssText = "position:absolute;left:-10000px;top:0;width:200px;height:300px;visibility:hidden;pointer-events:none";
    document.body.appendChild(stage);
  }
  stage.innerHTML = "";
  display(stage, face, { teamColors });
  const svg = stage.querySelector("svg");
  if (svg) {
    svg.setAttribute("viewBox", CROPS[crop].viewBox);
    svg.setAttribute("preserveAspectRatio", "xMidYMax slice");
  }
  const out = stage.innerHTML;
  stage.innerHTML = "";
  return out;
}

export const Face = memo(function Face({
  seed,
  race,
  colors,
  size = 40,
  crop,
  round,
  frame = true,
}: {
  seed: number;
  race: Race;
  colors?: [string, string];
  size?: number;
  /** defaults to a headshot for small avatars and head-and-shoulders for larger ones */
  crop?: FaceCrop;
  round?: boolean;
  frame?: boolean;
}) {
  const c = colors ?? ["#4b5563", "#e5e7eb"];
  const mode: FaceCrop = crop ?? (size < 56 || round ? "head" : "bust");
  const key = `${seed}:${race}:${c[0]}:${c[1]}:${mode}`;
  let svg = svgCache.get(key);
  if (!svg) {
    svg = renderSvg(faceFor(seed, race), [c[0], c[1], "#111111"], mode);
    if (svgCache.size > 3000) svgCache.clear();
    svgCache.set(key, svg);
  }
  return (
    <div
      className={`face ${mode}${round ? " round" : ""}${frame ? "" : " bare"}`}
      style={{ width: size, height: Math.round(size * CROPS[mode].ratio), ["--face-c" as string]: c[0] }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
});
