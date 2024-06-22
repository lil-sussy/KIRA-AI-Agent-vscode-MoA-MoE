import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
	plugins: [react()],
	build: {
		outDir: "out/web",
		emptyOutDir: true,
		rollupOptions: {
			input: "src/webview/index.html",
		},
	},
});
