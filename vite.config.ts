import { defineConfig, loadEnv, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

/** Serves api/saves.ts during `npm run dev`, the way Vercel serves it in production. */
function devApi(): Plugin {
  return {
    name: "dev-api",
    apply: "serve",
    configureServer(server) {
      // the Blob token lives in .env.local (from `vercel env pull`)
      Object.assign(process.env, loadEnv("development", process.cwd(), ""));
      server.middlewares.use("/api/saves", async (req, res) => {
        const chunks: Buffer[] = [];
        for await (const c of req) chunks.push(c as Buffer);
        const mod = (await server.ssrLoadModule("/api/saves.ts")) as Record<string, (r: Request) => Promise<Response> | Response>;
        const handler = mod[req.method ?? "GET"];
        if (!handler) {
          res.statusCode = 405;
          res.end();
          return;
        }
        const request = new Request(`http://localhost${req.originalUrl ?? req.url}`, {
          method: req.method,
          headers: req.headers as Record<string, string>,
          body: req.method === "POST" ? Buffer.concat(chunks) : undefined,
        });
        const out = await handler(request);
        res.statusCode = out.status;
        out.headers.forEach((v, k) => res.setHeader(k, v));
        res.end(Buffer.from(await out.arrayBuffer()));
      });
    },
  };
}

export default defineConfig({
  base: "./",
  plugins: [react(), devApi()],
  server: { host: true, port: 5173 },
  build: {
    chunkSizeWarningLimit: 2000,
    // fonts are inlined into the CSS so the single-file build stays self-contained
    assetsInlineLimit: (file) => (file.endsWith(".woff2") ? true : undefined),
  },
});
