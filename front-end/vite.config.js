import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    // Disable source maps to save memory
    sourcemap: false,
    // Enable minification
    minify: 'terser',
    // Configure Terser options for better minification
    terserOptions: {
      compress: {
        // Drop console logs in production
        drop_console: true,
        // Other optimizations
        ecma: 2020,
        keep_fargs: false,
        passes: 2
      }
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
