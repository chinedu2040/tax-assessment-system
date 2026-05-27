/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        nigerian: {
          green: '#008751',
          'green-dark': '#005c38',
          'green-light': '#e8f5e9',
        },
      },
    },
  },
  plugins: [],
}
