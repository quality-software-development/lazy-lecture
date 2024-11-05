export enum TranscriptStatus {
    QUEUED,
    IN_PROGRESS,
    COMPLETED,
    REJECTED,
}

export interface TranscriptDTO {
    task_id: number;
    transcription: string;
    timestamp: string;
    transcript_length_secs: number;
    status: TranscriptStatus;
}

export interface ITranscript {
    taskId: number;
    text: string;
    timeStamp: Date;
    duration: number;
    status: TranscriptStatus;
}
