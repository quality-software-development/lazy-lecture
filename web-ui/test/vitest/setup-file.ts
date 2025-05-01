import {vi} from 'vitest';
import {api} from 'src/boot/axios';
import {AxiosError} from 'axios';
import {messages} from 'test/vitest/messages';
import {createRouter, createWebHistory} from 'vue-router';
import routes from 'src/router/routes';
import {TranscriptionsApi} from 'src/api/transcripts';

export const router = createRouter({
    history: createWebHistory(),
    routes,
});

export const getMockUser = (canInteract: boolean, id = 0) => ({
    id,
    username: 'mockUser',
    active: true,
    canInteract,
    role: 'admin',
    createDate: new Date(),
    updateDate: new Date(),
});

export const ok = <T>(data: T) => ({
    successful: true,
    data,
});

const getAxiosError = (code: number, msg: string) => {
    const error = new AxiosError(
        '',
        `${code}`,
        undefined,
        null,
        code !== 418
            ? ({
                data: {
                    detail:
                        code === 422
                            ? [
                                {
                                    msg,
                                },
                            ]
                            : msg,
                },
            } as any)
            : null
    );
    error.status = code;
    return error;
};

// ========== MOCK API.GET ==========
const mockGet = vi.spyOn(api, 'get');
const now = new Date().toISOString().slice(0, -1);

mockGet.mockImplementation((url) => {
    switch (url) {
        case '/transcriptions?page=1&size=100':
            return Promise.resolve({
                data: {
                    page: 1,
                    size: 100,
                    total: 1,
                    pages: 1,
                    transcriptions: [
                        {
                            id: 1,
                            creator_id: 0,
                            audio_len_secs: 100,
                            chunk_size_secs: 900,
                            current_state: 'in_progress',
                            create_date: now,
                            update_date: now,
                            description: 'string',
                            error_count: 0,
                        },
                    ],
                },
            });

        case '/transcript?task_id=1&skip=0&limit=100':
        case '/transcript?task_id=999&skip=0&limit=100':
            return Promise.resolve({
                data: {
                    page: 1,
                    size: 100,
                    total: 1,
                    pages: 1,
                    transcriptions: [
                        {
                            chunk_order: 0,
                            chunk_size_secs: 900,
                            id: 1,
                            transcription: 'Mock chunk text.',
                        },
                    ],
                },
            });

        case '/transcript/info?transcript_id=1':
            return Promise.resolve({
                data: {
                    audio_len_secs: 100,
                    id: 1,
                    update_date: now,
                    current_state: 'completed',
                    error_count: 0,
                    chunk_size_secs: 900,
                    creator_id: 0,
                    create_date: now,
                },
            });

        default:
            return Promise.reject();
    }
});

// ========== MOCK API.POST ==========
const mockPost = vi.spyOn(api, 'post');

const rejectInvalidCreds = (username: string, password: string) => {
    if (
        username.length < 5 ||
        username.length > 64 ||
        !/[A-Za-z]+/.test(username)
    ) {
        return Promise.reject(
            getAxiosError(422, messages.incorrectLoginCaption)
        );
    } else if (
        password.length < 8 ||
        password.length > 256 ||
        !/[A-Za-z]/.test(password) ||
        !/[A-Z]/.test(password) ||
        !/[a-z]/.test(password) ||
        !/\d/.test(password) ||
        !/[!@#$%^&*(),.?":{}|<>=_]/.test(password)
    ) {
        return Promise.reject(
            getAxiosError(422, messages.incorrectPasswordCaption)
        );
    }
};

mockPost.mockImplementation((url, data) => {
    switch (url) {
        case '/auth/login': {
            const {username, password} = data as {
                username: string;
                password: string;
            };
            return (
                rejectInvalidCreds(username, password) ||
                Promise.resolve({
                    data: {
                        access_token: 'string',
                        refresh_token: 'string',
                        token_type: 'bearer',
                    },
                })
            );
        }

        case '/auth/register': {
            const {username, password} = data as {
                username: string;
                password: string;
            };
            return (
                rejectInvalidCreds(username, password) ||
                Promise.resolve({
                    data: {
                        id: 0,
                        username,
                        active: true,
                        can_interact: true,
                        role: 'admin',
                        create_date: now,
                        update_date: now,
                    },
                })
            );
        }

        case '/transcript/cancel?transcript_id=1':
            return Promise.resolve('OK');

        default:
            return Promise.reject(null);
    }
});

// ========== MOCK TRANSCRIPTIONS API ==========

vi.spyOn(TranscriptionsApi, 'cancelTranscriptionProcess').mockImplementation(() =>
    Promise.resolve({successful: true, data:null})
);
