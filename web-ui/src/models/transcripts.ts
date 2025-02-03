//Состояния обработки аудио
export enum TranscriptionState {
    queued,
    in_progress,
    processing_error,
    completed,
    completed_partially,
    processing_fail,
    cancelled,
}

//Запрос api/transcription/info
export interface TranscriptionInfoQueryDTO {
    id: number;
    creator_id: number;
    audio_len_secs: number;
    chunk_size_secs: number;
    current_state:
        | 'queued'
        | 'in_progress'
        | 'processing_error'
        | 'completed'
        | 'completed_partially'
        | 'processing_fail'
        | 'cancelled';
    create_date: string;
    update_date: string;
    description: string;
}

//Запрос api/transcriptions
export interface TranscriptionsQueryDTO {
    page: number;
    pages: number;
    size: number;
    total: number;
    transcriptions: TranscriptionInfoQueryDTO[];
}
export interface Transcription {
    id: number;
    creatorId: number;
    audioLenSecs: number;
    chunkSizeSecs: number;
    currentState: TranscriptionState;
    createDate: Date;
    updateDate: Date;
    description: string;
}
export interface Transcriptions {
    page: number;
    pages: number;
    size: number;
    total: number;
    transcriptions: Transcription[];
}

//Запрос api/transcript
export interface TranscriptionQueryDTO {
    page: number;
    pages: number;
    size: number;
    total: number;
    transcriptions: {
        chunk_order: number;
        chunk_size_secs: number;
        id: number;
        transcription: string;
    }[];
}
export interface Chunk {
    index: number;
    duration: number;
    text: string;
}
export interface ChunkedTranscription {
    taskId: number;
    chunks: Chunk[];
}

//Элемент словаря транскрипций
export interface TranscriptionsMapElement extends Transcription {
    chunks: Chunk[];
    markXPositions: number[];
    timeStampViews: string[];
    chunksDurationArray: number[];
}
