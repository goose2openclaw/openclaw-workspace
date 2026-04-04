/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#07080c',
        'bg-secondary': '#0c0f14',
        'bg-card': '#10141c',
        'bg-elevated': '#161c26',
        'accent-primary': '#00f5d4',
        'accent-secondary': '#00bbf9',
        'accent-purple': '#9d4edd',
        'text-primary': '#f0f2f5',
        'text-secondary': '#8b8d94',
        'text-muted': '#4a4c56',
        'success': '#00f5a0',
        'danger': '#ff4757',
        'warning': '#ffd43b',
        'gold': '#ffd700',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'monospace'],
        'sans': ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
