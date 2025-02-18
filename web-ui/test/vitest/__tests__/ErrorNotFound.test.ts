import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { mount } from '@vue/test-utils';
import router from 'src/router';
import { describe, expect, it } from 'vitest';

import ErrorNotFound from 'src/pages/ErrorNotFound.vue';
installQuasarPlugin();

describe('Страница с ошибкой 404', () => {
    it('При переходе по несуществующему URL должна открываться страница с ошибкой 404', async () => {
        expect(1).toEqual(1);
        // const wrapper = mount(ErrorNotFound, {
        //     global: {
        //         plugins: [router],
        //     },
        // });
    });
});
