import { date } from 'quasar';

export const formatTimestamp = (timestamp: number) =>
    date.formatDate(
        new Date(timestamp * 1000 + new Date().getTimezoneOffset() * 60000),
        'HH:mm:ss'
    );
