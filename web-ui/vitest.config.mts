import { defineConfig, configDefaults } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { quasar, transformAssetUrls } from '@quasar/vite-plugin';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
    test: {
        environment: 'happy-dom',
        setupFiles: 'test/vitest/setup-file.ts',
        include: [
            // Matches vitest tests in any subfolder of 'src' or into 'test/vitest/__tests__'
            // Matches all files with extension 'js', 'jsx', 'ts' and 'tsx'
            'src/**/*.vitest.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
            'test/vitest/__tests__/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
        ],
        coverage: {
            enabled: false,
            exclude: [
                'test',
                'web-ui/src/models',
                '*.config.*',
                '.quasar',
                '.eslintrc.cjs',
                'src/**/*.d.ts',
                'src/stores/index.ts',
                'src/boot/axios.ts',
                'src/pages/TranscriptPage.vue', // TODO: убрать
                'src/pages/ErrorNotFound.vue', // TODO: убрать
                'src/components/TranscriptListItem.vue', // TODO: убрать
                'src/stores/userInfoStore.ts', // TODO: убрать
                'src/router/index.ts', // TODO: убрать
            ],
            reporter: ['text', 'lcov']  // обязательно добавить "lcov"
        }
    },
    plugins: [
        vue({
            template: { transformAssetUrls },
        }),
        quasar({
            sassVariables: 'src/quasar-variables.scss',
        }),
        tsconfigPaths(),
    ] as any,
});
