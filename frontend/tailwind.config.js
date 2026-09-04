/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#0B0F17",
          card: "rgba(18, 24, 38, 0.75)",
          border: "rgba(255, 255, 255, 0.08)",
          accent: "#6366F1",
          cyan: "#06B6D4",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E",
          purple: "#8B5CF6",
        },
      },
      boxShadow: {
        glow: "0 0 25px -5px rgba(99, 102, 241, 0.3)",
        'glow-cyan': "0 0 25px -5px rgba(6, 182, 212, 0.3)",
        'glow-rose': "0 0 25px -5px rgba(244, 63, 94, 0.3)",
        'glow-emerald': "0 0 25px -5px rgba(16, 185, 129, 0.3)",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
