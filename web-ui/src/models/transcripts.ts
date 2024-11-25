export enum TranscriptStatus {
    QUEUED,
    IN_PROGRESS,
    COMPLETED,
    REJECTED,
}

export interface TranscriptGeneralDTO {
    task_id: number;
    transcription: string;
    timestamp: string;
    transcript_length_secs: number;
    status: TranscriptStatus;
}
export interface ITranscriptGeneral {
    taskId: number;
    text: string;
    timeStamp: Date;
    duration: number;
    status: TranscriptStatus;
}

export interface ChunkDTO {
    chunk_order: number;
    chunk_size_secs: number;
    transcription: string;
}
export interface TranscriptChunkedDTO {
    task_id: number;
    transcription_chunks: ChunkDTO[];
}
export interface IChunk {
    index: number;
    duration: number;
    text: string;
}
export interface ITranscriptChunked {
    taskId: number;
    chunks: IChunk[];
}

export interface ITranscriptsMapElement {
    taskId: number;
    text: string;
    timeStamp: Date;
    duration: number;
    status: TranscriptStatus;
    chunks: IChunk[];
    markXPositions: number[];
    timeStampViews: string[];
    chunksDurationArray: number[];
}
