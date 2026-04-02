/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/templates/**/*.html",
        "./app/**/*.py",
        "./app/static/js/**/*.js"
    ],
    theme: {
        extend: {
            colors: {
                // Semantic Primary Color (Mapped to Green)
                primary: {
                    50: 'var(--color-green-50)',
                    100: 'var(--color-green-100)',
                    200: 'var(--color-green-200)',
                    300: 'var(--color-green-300)',
                    400: 'var(--color-green-400)',
                    500: 'var(--color-green-500)',
                    600: 'var(--color-green-600)',
                    700: 'var(--color-green-700)',
                    800: 'var(--color-green-800)',
                    900: 'var(--color-green-900)',
                    950: 'var(--color-green-950)',
                },

                // Semantic Layout Colors
                backgroundh: 'var(--color-gray-200)',
                backgroundl: 'var(--color-gray-100)',
                surface: 'var(--color-white)',

                // Contrast color
                contrast: 'var(--color-black)',
                contrasttext: 'var(--color-white)',

                // Semantic Text Colors
                text: {
                    main: 'var(--color-gray-900)',
                    bright: 'var(--color-gray-200)',
                    muted: 'var(--color-gray-600)',
                    light: 'var(--color-gray-400)',
                    inverse: 'var(--color-white)',
                },

                // Semantic Border
                border: {
                    main: 'var(--color-gray-300)',
                },

                // Semantic Alerts
                danger: {
                    50: 'var(--color-red-50)',
                    200: 'var(--color-red-200)',
                    800: 'var(--color-red-800)',
                },
                success: {
                    50: 'var(--color-green-50)',
                    200: 'var(--color-green-200)',
                    800: 'var(--color-green-800)',
                },
                info: {
                    50: 'var(--color-blue-50)',
                    200: 'var(--color-blue-200)',
                    800: 'var(--color-blue-800)',
                }
            }
        },
    },
    plugins: [],
}
