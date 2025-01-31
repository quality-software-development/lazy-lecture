import { ResSuccess, ResError } from 'src/models/responses';
import { api } from 'src/boot/axios';
import { AxiosResponse } from 'axios';

export class BaseApi {
    static async runRequest<ResDataType, DTO>(
        method: 'get' | 'post',
        url: string,
        callback: (response: AxiosResponse<DTO, any>) => ResDataType,
        errorMsg?: string,
        body?: object
    ): Promise<ResSuccess<ResDataType> | ResError> {
        try {
            const res = await (body
                ? api[method]<DTO>(url, body)
                : api[method]<DTO>(url));
            return {
                successful: true,
                data: callback(res),
            };
        } catch (e: any) {
            const serverMsg =
                e.status === 422
                    ? e.response.data.detail.reduce(
                        (concatedErrs: string, err: string) =>
                            `${concatedErrs}\n${err}`,
                        ''
                    )
                    : e.status && e.status !== 418
                        ? e.response.data.detail
                        : '';
            return {
                successful: false,
                message: `${errorMsg ? `${errorMsg}\n` : ''}${serverMsg}`,
            };
        }
    }
}
