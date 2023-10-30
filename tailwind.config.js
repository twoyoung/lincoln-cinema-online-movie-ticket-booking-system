/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        primary: '#1a202c',
        secondary: '#2d3748',
      }
    }
  },
  plugins: [
    require('tailwindcss'),
    require('autoprefixer')
  ],
}

