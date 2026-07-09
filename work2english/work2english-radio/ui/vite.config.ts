import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Work2English OS — Vite config
// Dev server reachable on the LAN so the host Mac and other devices can open it.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Proxy API + generated files to server.py (run separately on :8000)
    // so the UI works identically in `npm run dev` and production.
    proxy: {
      "/api": "http://localhost:8000",
      "/files": "http://localhost:8000",
    },
  },
  preview: {
    host: true,
    port: 4173,
  },
});
