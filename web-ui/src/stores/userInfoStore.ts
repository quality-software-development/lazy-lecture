import { defineStore } from 'pinia';
import { AuthApi } from 'src/api/auth';

import type { UserInfo } from 'src/models/auth';
import type { ResError, ResSuccess } from 'src/models/responses';

export const useUserInfoStore = defineStore('userInfo', {
    state: () => ({
        userInfo: null as UserInfo | null,
    }),
    actions: {
        async updateUserInfo(): Promise<ResSuccess<UserInfo> | ResError> {
            try {
                const userInfoRes = await AuthApi.getUserInfo();
                if (userInfoRes?.successful) {
                    this.userInfo = (userInfoRes as ResSuccess<UserInfo>)
                        .data as UserInfo;
                    return userInfoRes;
                } else {
                    throw new Error((userInfoRes as ResError)?.message);
                }
            } catch (e: any) {
                return {
                    successful: false,
                    message: e.response?.data?.detail || 'Ошибка авторизации',
                };
            }
        },
        clearUserInfo() {
            this.userInfo = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        },
    },
});
