import { defineConfig } from 'vite'

export default defineConfig({
    base: './',
    build: {
        rollupOptions: {
            input: {
                main: 'templates/index.html',
                editor: 'templates/editor.html',
                auth: 'templates/auth.html',
                rooms: 'templates/rooms.html',
            }
        }
    },
    server: {
        open: '/templates/editor.html'
    }
})