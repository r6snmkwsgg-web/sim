// Inline the production build into one self-contained HTML file that runs
// straight from disk (double-click to play, no server needed).
//   npm run build:single  ->  release/hardwood-dynasty.html

import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const dist = "dist";
let html = readFileSync(join(dist, "index.html"), "utf8");
const assets = readdirSync(join(dist, "assets"));

for (const f of assets) {
  const body = readFileSync(join(dist, "assets", f), "utf8");
  if (f.endsWith(".js")) {
    const re = new RegExp(`<script[^>]*src="\\.?/?assets/${f.replace(/\./g, "\\.")}"[^>]*></script>`);
    // keep the bundle from closing the inline script tag early
    const safe = body.replace(/<\/script/gi, "<\\/script");
    html = html.replace(re, () => `<script type="module">${safe}</script>`);
  } else if (f.endsWith(".css")) {
    const re = new RegExp(`<link[^>]*href="\\.?/?assets/${f.replace(/\./g, "\\.")}"[^>]*>`);
    html = html.replace(re, () => `<style>${body}</style>`);
  }
}
if (/src="\.?\/?assets\//.test(html) || /href="\.?\/?assets\//.test(html)) {
  throw new Error("some assets were not inlined");
}
mkdirSync("release", { recursive: true });
writeFileSync(join("release", "hardwood-dynasty.html"), html);
console.log(`release/hardwood-dynasty.html (${(html.length / 1024).toFixed(0)} KB)`);
