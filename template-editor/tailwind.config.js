/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        glow: {
          '0%, 100%': { textShadow: '0 0 30px rgba(0,255,255,0.5)' },
          '50%': { textShadow: '0 0 50px rgba(0,255,255,0.8)' },
        },
      },
      animation: {
        'rotate': 'rotate 20s linear infinite',
        'glow': 'glow 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
} 