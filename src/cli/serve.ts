import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';

/**
 * Tiny static server for the L3 viewer: `npm run view`, then open
 * http://localhost:8737 — serves viewer/ and runs/ from the repo root.
 */
const root = process.cwd();
const types: Record<string, string> = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.jsonl': 'application/x-ndjson',
};

const server = createServer(async (req, res) => {
  try {
    let p = decodeURIComponent((req.url ?? '/').split('?')[0]);
    if (p === '/') p = '/viewer/index.html';
    const file = normalize(join(root, p));
    if (!file.startsWith(root) || !existsSync(file)) {
      res.writeHead(404); res.end('not found'); return;
    }
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': types[extname(file)] ?? 'application/octet-stream' });
    res.end(body);
  } catch (err) {
    res.writeHead(500); res.end(String(err));
  }
});
server.listen(8737, () => {
  console.log('L3 viewer at http://localhost:8737  (run `npm run demo` first)');
});
