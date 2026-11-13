import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";
import { fileURLToPath } from "node:url";
import siteConfig from "../../../sites/common_site_config.json" with {
  type: "json",
};

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const webserverPort = siteConfig.webserver_port || 8000;

const buildVersionPlugin = {
  name: "dashboard-build-version",
  apply: "build",
  generateBundle() {
    this.emitFile({
      type: "asset",
      fileName: "version.json",
      source: JSON.stringify({ version: Date.now().toString() }),
    });
  },
};

export default defineConfig({
  plugins: [vue(), tailwindcss(), buildVersionPlugin],

  base:
    process.env.NODE_ENV === "production"
      ? "/assets/quantumberg_project_management_dashboard/dashboard/"
      : "/",

  server: {
    host: "0.0.0.0",
    port: 8080,
    strictPort: true,

    proxy: {
      "/api": {
        target: `http://127.0.0.1:${webserverPort}`,
        changeOrigin: true,
      },
      "/assets": {
        target: `http://127.0.0.1:${webserverPort}`,
        changeOrigin: true,
      },
      "/files": {
        target: `http://127.0.0.1:${webserverPort}`,
        changeOrigin: true,
      },
      "/private": {
        target: `http://127.0.0.1:${webserverPort}`,
        changeOrigin: true,
      },
    },
  },

  resolve: {
    alias: {
      "@": path.resolve(currentDir, "src"),
    },
  },

  build: {
    outDir: path.resolve(
      currentDir,
      "../quantumberg_project_management_dashboard/public/dashboard"
    ),

    emptyOutDir: true,
    target: "es2020",
    cssCodeSplit: false,
    sourcemap: false,
    assetsInlineLimit: 4096,

    // This app is mounted by a Frappe Desk page.
    // Keep a single JavaScript bundle.
    rolldownOptions: {
      output: {
        format: "iife",
        name: "QuantumbergProjectManagementDashboard",
        codeSplitting: false,
        entryFileNames: "index.js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith(".css")) {
            return "index.css";
          }

          return "assets/[name][extname]";
        },
      },
    },

    chunkSizeWarningLimit: 2500,
  },
});