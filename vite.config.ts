import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "./",
  plugins: [react()],
  server: { host: true, port: 5173 },
  build: {
    chunkSizeWarningLimit: 2000,
    // fonts are inlined into the CSS so the single-file build stays self-contained
    assetsInlineLimit: (file) => (file.endsWith(".woff2") ? true : undefined),
  },
});
