/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0066cc",
          dark: "#0052a3",
          light: "#3385d6",
          50: "#e6f2ff",
          100: "#b3d9ff",
          200: "#80bfff",
          300: "#4da6ff",
          400: "#1a8cff",
          500: "#0066cc",
          600: "#0052a3",
          700: "#003d7a",
          800: "#002952",
          900: "#001429",
        },
        purple: {
          primary: "#8B5CF6",
          dark: "#6D28D9",
          light: "#A78BFA",
        },
        blue: {
          primary: "#0066cc",
          dark: "#0052a3",
          light: "#3385d6",
        },
      },
      backgroundImage: {
        "gradient-admin": "linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%)",
        "gradient-button": "linear-gradient(135deg, #0066cc 0%, #0052a3 100%)",
        "gradient-primary": "linear-gradient(135deg, #0066cc 0%, #3385d6 100%)",
        "gradient-dark": "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)",
      },
      backdropBlur: {
        xs: "2px",
      },
      keyframes: {
        particle: {
          "0%, 100%": { transform: "translate(0, 0)" },
          "50%": { transform: "translate(var(--tx), var(--ty))" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
      animation: {
        particle: "particle 20s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
      },
      fontFamily: {
        pacifico: ["Pacifico", "cursive"],
        secular: ["Secular One", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
        "glass-lg": "0 8px 32px 0 rgba(0, 102, 204, 0.3)",
        "primary-glow": "0 0 20px rgba(0, 102, 204, 0.5)",
      },
    },
  },
  plugins: [],
};

