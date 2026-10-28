/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#E10600',
        background: {
          DEFAULT: '#0F0F0F',
          secondary: '#1A1A1A',
          tertiary: '#252525',
        },
        card: {
          DEFAULT: '#1E1E1E',
          border: '#2A2A2A',
        },
        success: '#00D26A',
        warning: '#FFB800',
        accent: '#E10600',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
