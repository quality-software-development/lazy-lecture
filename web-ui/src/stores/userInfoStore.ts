import { defineStore } from 'pinia';
import { UserInfo } from 'src/models/auth';
import { AuthApi } from 'src/api/auth';

export const useUserInfoStore = defineStore('userInfo', {
    state: () => ({
        userInfo: {} as UserInfo | null,
    }),
    actions: {
        async updateUserInfo() {
            try {
                const userInfo = await AuthApi.getUserInfo();
                if (userInfo?.successful) {
                    this.userInfo = userInfo.data as UserInfo;
                    return userInfo;
                } else {
                    throw new Error(userInfo?.message);
                }
            } catch (e) {
                return {
                    successful: false,
                    message: e || 'Ошибка авторизации',
                };
            }
        },
        async clearUserInfo() {
            this.userInfo = null;
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        },
    },
});
