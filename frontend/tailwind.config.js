/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        background: "#1a1a1a",
        foreground: "#ffffff",
        card: "#2a2a2a",
        "card-foreground": "#ffffff",
        primary: "#00ff88",
        "primary-foreground": "#000000",
        secondary: "#10b981",
        "secondary-foreground": "#ffffff",
        accent: "#3b82f6",
        "accent-foreground": "#ffffff",
        destructive: "#ff4757",
        "destructive-foreground": "#ffffff",
        muted: "#404040",
        "muted-foreground": "#a0a0a0",
        border: "#333333",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      boxShadow: {
        glass: "0 4px 30px rgba(0, 0, 0, 0.1)",
      },
      backdropBlur: {
        glass: "10px",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
} 