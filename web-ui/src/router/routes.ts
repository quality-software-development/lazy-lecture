import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
    {
        path: '',
        redirect: '/transcripts',
    },
    {
        path: '/transcripts',
        component: () => import('layouts/MainLayout.vue'),
        children: [
            { path: '', component: () => import('pages/UploadAudioPage.vue') },
            {
                path: ':taskId',
                component: () => import('pages/TranscriptPage.vue'),
            },
        ],
    },
    {
        path: '/log_in',
        component: () => import('pages/AuthPage.vue'),
    },
    {
        path: '/sign_up',
        component: () => import('pages/AuthPage.vue'),
        props: {
            signUp: true,
        },
    },
    {
        path: '/:catchAll(.*)*',
        component: () => import('pages/ErrorNotFound.vue'),
    },
];

export default routes;
