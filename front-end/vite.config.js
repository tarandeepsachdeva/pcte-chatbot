import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    // Disable source maps to save memory
    sourcemap: false,
    // Use ESBuild for minification (included with Vite)
    minify: 'esbuild',
    // ESBuild minification options
    esbuild: {
      drop: ['console'],  // Remove all console.* statements
      pure: ['console.log'],  // Remove console.log specifically
      minify: true,
      target: 'es2020',
      treeShaking: true
    },
    // Disable code splitting to reduce memory usage
    rollupOptions: {
      output: {
        manualChunks: undefined,
        inlineDynamicImports: true
      }
    },
    // Set memory limit for the build
    chunkSizeWarningLimit: 1000 // in KB
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom'],
    force: true
  },
  // Set environment variables
  define: {
    'process.env.NODE_ENV': JSON.stringify('production')
  }
});
