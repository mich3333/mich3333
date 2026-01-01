/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Design tokens using CSS variables
        bg: 'hsl(var(--bg))',
        'bg-subtle': 'hsl(var(--bg-subtle))',

        surface: 'hsl(var(--surface))',
        'surface-hover': 'hsl(var(--surface-hover))',

        border: 'hsl(var(--border))',
        'border-hover': 'hsl(var(--border-hover))',

        text: 'hsl(var(--text))',
        'text-muted': 'hsl(var(--text-muted))',
        'text-subtle': 'hsl(var(--text-subtle))',

        primary: 'hsl(var(--primary))',
        'primary-hover': 'hsl(var(--primary-hover))',
        'primary-muted': 'hsl(var(--primary-muted))',

        accent: 'hsl(var(--accent))',
        'accent-hover': 'hsl(var(--accent-hover))',
        'accent-muted': 'hsl(var(--accent-muted))',

        success: 'hsl(var(--success))',
        warning: 'hsl(var(--warning))',
        error: 'hsl(var(--error))',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        DEFAULT: 'var(--radius)',
        lg: 'var(--radius-lg)',
      },
      animation: {
        'gradient': 'gradient 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-in-right': 'slideInRight 0.3s ease-out',
      },
      keyframes: {
        gradient: {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
        float: {
          '0%, 100%': {
            transform: 'translateY(0px)',
          },
          '50%': {
            transform: 'translateY(-20px)',
          },
        },
        slideInRight: {
          '0%': {
            transform: 'translateX(100%)',
            opacity: '0',
          },
          '100%': {
            transform: 'translateX(0)',
            opacity: '1',
          },
        },
      },
    },
  },
  plugins: [],
}
