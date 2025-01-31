import { api } from 'src/boot/axios';
import type { LogInResDTO, SignUpResDTO, UserInfo } from 'src/models/auth';
import type { ResError, ResSuccess } from 'src/models/responses';

export class AuthApi {
    static async logIn(
        username: string,
        password: string
    ): Promise<ResSuccess<null> | ResError> {
        let logInRes;
        try {
            const res = await api.post<LogInResDTO>(
                '/auth/login',
                {
                    username,
                    password,
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );
            if (res.status === 200) {
                localStorage.setItem('accessToken', res.data.access_token);
                localStorage.setItem('refreshToken', res.data.refresh_token);
                logInRes = {
                    successful: true,
                    data: null,
                };
            }
        } catch (e: any) {
            switch (e.status) {
                case 401:
                    logInRes = {
                        successful: false,
                        message: e.response.data.detail,
                    };
                case 422:
                    logInRes = {
                        successful: false,
                        message: e.response.data.detail[0].msg,
                    };
            }
        }
        return (
            logInRes || {
                successful: false,
                message: 'Ошибка входа.',
            }
        );
    }

    static async signUp(
        username: string,
        password: string
    ): Promise<ResSuccess<SignUpResDTO> | ResError> {
        let signUpRes;
        try {
            const res = await api.post<SignUpResDTO>(
                '/auth/register',
                {
                    username,
                    password,
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );
            if (res.status === 201) {
                signUpRes = {
                    successful: true,
                    data: res.data,
                };
            }
        } catch (e: any) {
            switch (e.status) {
                case 409:
                    signUpRes = {
                        successful: false,
                        message: e.response.data.detail,
                    };
                case 422:
                    signUpRes = {
                        successful: false,
                        message: e.response.data.detail.msg,
                    };
            }
        }
        return (
            signUpRes || {
                successful: false,
                message: 'Ошибка регистрации.',
            }
        );
    }

    static async getUserInfo(): Promise<ResSuccess<UserInfo> | ResError> {
        const fetchUserInfo = async (): Promise<
            ResSuccess<UserInfo> | undefined
        > => {
            try {
                const res = await api.get('/auth/info');
                if (res.status === 200) {
                    return {
                        successful: true,
                        data: {
                            id: res.data.id,
                            username: res.data.username,
                            active: res.data.active,
                            canInteract: res.data.can_interact,
                            role: res.data.role,
                            createDate: new Date(res.data.create_date),
                            updateDate: new Date(res.data.update_date),
                        } as UserInfo,
                    };
                }
            } catch (e) {
                throw e;
            }
        };
        let userInfo;
        try {
            userInfo = await fetchUserInfo();
        } catch (e: any) {
            if (
                e.status === 401 &&
                e.response?.data?.detail === 'Invalid or expired token'
            ) {
                try {
                    const res = await api.post('/auth/refresh', {
                        refresh_token: localStorage.getItem('refreshToken'),
                    });
                    if (res.status === 200) {
                        localStorage.setItem(
                            'accessToken',
                            res.data.access_token
                        );
                        localStorage.setItem(
                            'refreshToken',
                            res.data.refresh_token
                        );
                        userInfo = await fetchUserInfo();
                    }
                } catch (e: any) {
                    if (e.status === 401) {
                        return {
                            successful: false,
                            message: e.response.data.detail,
                        };
                    }
                }
            }
        }
        return (
            userInfo || {
                successful: false,
                message: 'Пожалуйста, войдите в систему.',
            }
        );
    }
}
