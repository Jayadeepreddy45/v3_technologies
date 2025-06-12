// tailwind.config.js
module.exports = {
  content: [
    "./templates/**/*.html",   // scan all HTML files inside the templates folder
    "./static/js/**/*.js"      // optional: scan JS files if you're using Tailwind classes in JS
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
