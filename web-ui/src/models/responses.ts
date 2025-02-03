interface ApiResponseType<T> {
    successful: boolean;
    data: T;
    message: string;
    caption?: string;
}

export type ResSuccess<T> = Omit<ApiResponseType<T>, 'message' | 'caption'>;

export type ResError = Omit<ApiResponseType<null>, 'data'>;
