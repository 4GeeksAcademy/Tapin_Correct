import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/front/src/test/setup.js",
    exclude: ["**/node_modules/**", "**/dist/**", "**/e2e/**"],
  },
});
