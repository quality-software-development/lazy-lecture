import { route } from 'quasar/wrappers';
import {
    createMemoryHistory,
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from 'vue-router';

import routes from './routes';
import { useUserInfoStore } from 'src/stores/userInfoStore';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
    const createHistory = process.env.SERVER
        ? createMemoryHistory
        : process.env.VUE_ROUTER_MODE === 'history'
            ? createWebHistory
            : createWebHashHistory;

    const Router = createRouter({
        scrollBehavior(to) {
            if (to.hash) {
                return {
                    el: to.hash,
                    top:
                        (+(
                            document.querySelector(
                                '.ui-transcript-page-progress-container'
                            ) as HTMLElement
                        )?.clientHeight || 0) + 92,
                    behavior: 'smooth',
                };
            }
        },
        routes,

        // Leave this as is and make changes in quasar.conf.js instead!
        // quasar.conf.js -> build -> vueRouterMode
        // quasar.conf.js -> build -> publicPath
        history: createHistory(process.env.VUE_ROUTER_BASE),
    });

    Router.beforeEach(async (to, from) => {
        const userInfoStore = useUserInfoStore();
        if (
            !userInfoStore.userInfo?.id &&
            !(to.path === '/log_in' && from.path === '/sign_up') &&
            !(to.path === '/sign_up' && from.path === '/log_in')
        ) {
            await userInfoStore.updateUserInfo();
        }
        const isAuthorized = userInfoStore.userInfo?.id;

        if (!isAuthorized && to.path !== '/log_in' && to.path !== '/sign_up') {
            return { path: 'log_in' };
        } else if (
            isAuthorized &&
            ((to.path === '/log_in' && from.path !== '/log_in') ||
                (to.path === '/sign_up' && from.path !== '/sign_up'))
        ) {
            return { path: from.path };
        }
    });

    return Router;
});
