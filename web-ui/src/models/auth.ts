export interface LogInResDTO {
    access_token: string;
    refresh_token: string;
    token_type: string;
    detail?: any;
}

export interface SignUpResDTO {
    id: number;
    username: string;
    active: boolean;
    can_interact: boolean;
    role: string;
    create_date: string;
    update_date: string;
}

export interface UserInfo {
    id: number;
    username: string;
    active: boolean;
    canInteract: boolean;
    role: string;
    createDate: Date;
    updateDate: Date;
}
