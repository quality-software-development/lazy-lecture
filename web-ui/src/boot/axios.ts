import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';

declare module '@vue/runtime-core' {
    interface ComponentCustomProperties {
        $axios: AxiosInstance;
        $api: AxiosInstance;
    }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});
api.interceptors.request.use((config) => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});
api.interceptors.response.use(null, async (error) => {
    if (
        error.status === 401 &&
        error.response?.data?.detail === 'Invalid or expired token' &&
        error.config.url !== '/auth/refresh'
    ) {
        const res = await api.post('/auth/refresh', {
            refresh_token: localStorage.getItem('refreshToken'),
        });
        if (res.status === 200) {
            localStorage.setItem('accessToken', res.data.access_token);
            localStorage.setItem('refreshToken', res.data.refresh_token);
        }
    } else {
        throw error;
    }
});

export default boot(({ app }) => {
    // for use inside Vue files (Options API) through this.$axios and this.$api

    app.config.globalProperties.$axios = axios;
    // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
    //       so you won't necessarily have to import axios in each vue file

    app.config.globalProperties.$api = api;
    // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
    //       so you can easily perform requests against your app's API
});

export { api };
