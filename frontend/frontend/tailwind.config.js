/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app.vue', // Main app file
    './components/**/*.{vue,js,ts}', // All components
    './layouts/**/*.vue', // Layout files
    './pages/**/*.vue', // Page files
    './plugins/**/*.{js,ts}', // Plugins
    './nuxt.config.ts', // Nuxt configuration
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
