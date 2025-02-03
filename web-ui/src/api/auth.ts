import { api } from 'src/boot/axios';
import type { LogInResDTO, SignUpResDTO, UserInfo } from 'src/models/auth';
import type { ResError, ResSuccess } from 'src/models/responses';
import { BaseApi } from './baseApi';

export class AuthApi extends BaseApi {
    static async logIn(
        username: string,
        password: string
    ): Promise<ResSuccess<null> | ResError> {
        return this.runRequest<null, LogInResDTO>(
            'post',
            '/auth/login',
            (res) => {
                localStorage.setItem('accessToken', res.data.access_token);
                localStorage.setItem('refreshToken', res.data.refresh_token);
                return null;
            },
            'Ошибка входа.',
            {
                username,
                password,
            },
        )
    }

    static async signUp(
        username: string,
        password: string
    ): Promise<ResSuccess<SignUpResDTO> | ResError> {
        return this.runRequest<SignUpResDTO, SignUpResDTO>(
            'post',
            '/auth/register',
            (res) => res.data,
            'Ошибка регистрации.',
            {
                username,
                password,
            },
        )
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
