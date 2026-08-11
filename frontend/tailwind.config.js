/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0b0f19",
        cardBg: "#151c2e",
        emeraldAccent: "#10b981",
        cyanAccent: "#06b6d4",
        purpleAccent: "#8b5cf6",
        amberAccent: "#f59e0b",
      }
    },
  },
  plugins: [],
}
