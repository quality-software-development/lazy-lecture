interface ApiResponseType<T> {
    successful: boolean;
    data: T;
    message: string;
}

export type ResSuccess<T> = Omit<ApiResponseType<T>, 'message'>;

export type ResError = Omit<ApiResponseType<null>, 'data'>;
