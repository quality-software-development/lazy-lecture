import { defineStore } from 'pinia';
import { getTranscripts } from 'src/api/transcripts';
import { ITranscript } from 'src/models/transcripts';

export const useTranscriptStore = defineStore('transcripts', {
    state: () => ({
        transcripts: [] as ITranscript[],
    }),
    actions: {
        async loadTranscripts(skip: number, limit: number) {
            this.transcripts =
                (await getTranscripts(skip, limit)) || ([] as ITranscript[]);
        },
    },
});
