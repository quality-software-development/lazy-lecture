import { api } from 'src/boot/axios';

interface LogInResType {
    message: string;
    token: string;
    error: string;
}

export async function logIn(login: string, password: string) {
    const res = await api.post<LogInResType>(
        '/auth/login',
        {
            login,
            password,
        },
        {
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );
    switch (res.status) {
        case 200:
            localStorage.setItem('accessToken', res.data.token);
    }
}

interface SignUpResType {
    message?: string;
    error?: string;
}

export async function signUp(login: string, password: string) {
    const res = await api.post<SignUpResType>(
        '/auth/register',
        {
            login,
            password,
        },
        {
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );
    switch (res.status) {
        case 201:
            return {
                successful: true,
                message: res.data.message,
            };
        case 409:
            return {
                successful: false,
                error: res.data.error,
            };
        default:
            return {
                successful: false,
            };
    }
}

export async function verifyToken() {
    try {
        const res = await api.get('/auth', {
            headers: {
                Authorization: localStorage.getItem('accessToken'),
            },
        });
        return res.data.auth;
    } catch (e) {
        return false;
    }
}
