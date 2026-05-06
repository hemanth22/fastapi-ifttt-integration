import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: "var(--surface)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        "primary-light": "var(--primary-light)",
        "primary-dark": "var(--primary-dark)",
        accent: "var(--accent)",
        "accent-light": "var(--accent-light)",
        border: "var(--border)",
        "text-secondary": "var(--text-secondary)",
        success: "var(--success)",
        warning: "var(--warning)",
        error: "var(--error)",
      },
    },
  },
  plugins: [],
};

export default config;
