// Cloud saves. Every player gets a private save code; their files live in the
// Blob store under a folder named after a hash of that code, so knowing the
// code is what unlocks listing, uploading and deleting. Browsers upload and
// download the files directly; this function only hands out short-lived
// upload tokens, lists a code's leagues and deletes old files.

import { createHash } from "node:crypto";
import { del, list } from "@vercel/blob";
import { generateClientTokenFromReadWriteToken } from "@vercel/blob/client";

const CODE = /^[0-9A-HJKMNP-TV-Z]{16}$/;
const LID = /^[A-Za-z0-9_-]{1,64}$/;
const FILE = /^(state|chunk|manifest)-\d{13}\.(json\.gz|ndjson\.gz|json)$/;
const MAX_BYTES = 300 * 1024 * 1024;

const CORS = {
  // the downloadable single-file version runs from file:// and syncs too
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type",
  "access-control-max-age": "86400",
};

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...CORS } });
}

function folderFor(code: unknown): string | null {
  if (typeof code !== "string") return null;
  const c = code.toUpperCase().replace(/[^0-9A-Z]/g, "");
  if (!CODE.test(c)) return null;
  return `saves/${createHash("sha256").update(`hardwood:${c}`).digest("hex").slice(0, 32)}/`;
}

interface Body {
  action?: string;
  code?: string;
  lid?: string;
  files?: string[];
  urls?: string[];
}

export function OPTIONS(): Response {
  return new Response(null, { status: 204, headers: CORS });
}

export async function POST(request: Request): Promise<Response> {
  let body: Body;
  try {
    body = (await request.json()) as Body;
  } catch {
    return json({ error: "Bad request" }, 400);
  }
  const folder = folderFor(body.code);
  if (!folder) return json({ error: "Invalid save code" }, 400);
  try {
    switch (body.action) {
      case "tokens": {
        // one token per file this sync will write: <lid>/<kind>-<time>.<ext>
        if (!LID.test(body.lid ?? "") || !Array.isArray(body.files) || body.files.length === 0 || body.files.length > 4) return json({ error: "Bad files" }, 400);
        const tokens: Record<string, { token: string; pathname: string }> = {};
        for (const f of body.files) {
          if (typeof f !== "string" || !FILE.test(f)) return json({ error: `Bad file name ${f}` }, 400);
          const pathname = `${folder}${body.lid}/${f}`;
          const token = await generateClientTokenFromReadWriteToken({
            pathname,
            addRandomSuffix: true,
            allowOverwrite: false,
            maximumSizeInBytes: MAX_BYTES,
            allowedContentTypes: ["application/gzip", "application/json"],
            // every file name is unique, so browsers and the CDN may keep them
            cacheControlMaxAge: 365 * 24 * 60 * 60,
            validUntil: Date.now() + 15 * 60 * 1000,
          });
          tokens[f] = { token, pathname };
        }
        // the league's current manifest, so a device that fell behind uploads a full copy
        let current: string | null = null;
        let currentAt = 0;
        const page = await list({ prefix: `${folder}${body.lid}/manifest-`, limit: 1000 });
        for (const b of page.blobs) {
          const at = new Date(b.uploadedAt).getTime();
          if (at >= currentAt) {
            current = b.url;
            currentAt = at;
          }
        }
        return json({ tokens, current });
      }
      case "list": {
        // each league's newest manifest, plus every file for cleanup
        const leagues: Record<string, { manifest: string | null; manifestAt: number; files: { url: string; size: number; uploadedAt: number }[] }> = {};
        let cursor: string | undefined;
        do {
          const page = await list({ prefix: folder, cursor, limit: 1000 });
          for (const b of page.blobs) {
            const rest = b.pathname.slice(folder.length);
            const [lid, name] = rest.split("/");
            if (!lid || !name) continue;
            const e = (leagues[lid] ??= { manifest: null, manifestAt: 0, files: [] });
            const at = new Date(b.uploadedAt).getTime();
            e.files.push({ url: b.url, size: b.size, uploadedAt: at });
            if (name.startsWith("manifest-") && at >= e.manifestAt) {
              e.manifest = b.url;
              e.manifestAt = at;
            }
          }
          cursor = page.hasMore ? page.cursor : undefined;
        } while (cursor);
        return json({ leagues });
      }
      case "delete": {
        // specific old files, or a whole league
        let urls: string[] = [];
        if (body.lid !== undefined) {
          if (!LID.test(body.lid)) return json({ error: "Bad league" }, 400);
          let cursor: string | undefined;
          do {
            const page = await list({ prefix: `${folder}${body.lid}/`, cursor, limit: 1000 });
            urls.push(...page.blobs.map((b) => b.url));
            cursor = page.hasMore ? page.cursor : undefined;
          } while (cursor);
        } else if (Array.isArray(body.urls)) {
          urls = body.urls.filter((u) => typeof u === "string" && new URL(u).pathname.slice(1).startsWith(folder));
          if (urls.length !== body.urls.length) return json({ error: "Not your files" }, 403);
        }
        if (urls.length) await del(urls);
        return json({ deleted: urls.length });
      }
      default:
        return json({ error: "Unknown action" }, 400);
    }
  } catch (e) {
    return json({ error: (e as Error).message }, 500);
  }
}
