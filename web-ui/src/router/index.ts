import { route } from 'quasar/wrappers';
import {
    createMemoryHistory,
    createRouter,
    createWebHashHistory,
    createWebHistory,
} from 'vue-router';

import routes from './routes';

import { verifyToken } from 'src/api/auth';

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
                    top: 182,
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

    Router.beforeEach(async (to) => {
        if (
            // make sure the user is authenticated
            /*!(await verifyToken())*/ false &&
            // ❗️ Avoid an infinite redirect
            to.path !== '/log_in' &&
            to.path !== '/sign_up'
        ) {
            // redirect the user to the login page
            return { path: 'log_in' };
        }
    });

    return Router;
});
