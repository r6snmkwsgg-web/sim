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

/** facesjs needs a live DOM node (it measures paths), so render offscreen and keep the markup. */
function renderSvg(face: FaceConfig, teamColors: [string, string, string]): string {
  if (!stage) {
    stage = document.createElement("div");
    stage.style.cssText = "position:absolute;left:-10000px;top:0;width:200px;height:300px;visibility:hidden;pointer-events:none";
    document.body.appendChild(stage);
  }
  stage.innerHTML = "";
  display(stage, face, { teamColors });
  const out = stage.innerHTML;
  stage.innerHTML = "";
  return out;
}

export const Face = memo(function Face({ seed, race, colors, size = 40, round, frame = true, ratio }: { seed: number; race: Race; colors?: [string, string]; size?: number; round?: boolean; frame?: boolean; ratio?: number }) {
  const c = colors ?? ["#4b5563", "#e5e7eb"];
  const key = `${seed}:${race}:${c[0]}:${c[1]}`;
  let svg = svgCache.get(key);
  if (!svg) {
    svg = renderSvg(faceFor(seed, race), [c[0], c[1], "#111111"]);
    if (svgCache.size > 3000) svgCache.clear();
    svgCache.set(key, svg);
  }
  return (
    <div
      // without an explicit ratio, crop to a headshot centered on the face
      className={`face${round ? " round" : ""}${ratio === undefined ? " crop" : ""}`}
      style={{
        width: size,
        height: round ? size : Math.round(size * (ratio ?? 1.02)),
        ["--face-c" as string]: c[0],
        ["--crop" as string]: `${Math.round(-size * 0.17)}px`,
        ...(frame ? null : { background: "none", border: "none" }),
      }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
});
