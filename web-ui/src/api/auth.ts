import { api } from 'src/boot/axios';
import { LogInResDTO, SignUpResDTO, UserInfo } from 'src/models/auth';

export class AuthApi {
    static async logIn(username: string, password: string) {
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
                return {
                    successful: true,
                };
            }
        } catch (e: any) {
            switch (e.status) {
                case 401:
                    return {
                        successful: false,
                        message: e.response.data.detail,
                    };
                case 422:
                    return {
                        successful: false,
                        message: e.response.data.detail.msg,
                    };
            }
        }
    }

    static async signUp(username: string, password: string) {
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
                return {
                    successful: true,
                    data: res.data,
                };
            }
        } catch (e: any) {
            switch (e.status) {
                case 409:
                    return {
                        successful: false,
                        message: e.response.data.detail,
                    };
                case 422:
                    return {
                        successful: false,
                        message: e.response.data.detail.msg,
                    };
            }
        }
    }

    static async getUserInfo() {
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
