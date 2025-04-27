/* eslint-disable */
// cypress/support/utils.ts

export function generateLatinUsername(length = 16): string {
  const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return Array.from({ length }, () => letters[Math.floor(Math.random() * letters.length)]).join('');
}
