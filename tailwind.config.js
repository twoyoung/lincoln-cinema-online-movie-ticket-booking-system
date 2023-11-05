/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["app/templates/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        primary: '#222831',
        secondary: '#393E46',
        tertiary: '#00ADB5',
        background: '#EEEEEE',
        highlight: '#FFD369'
      }
    }
  },
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}

