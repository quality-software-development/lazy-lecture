/* eslint-disable */
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:9000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,ts}',
  },
  env: {
    fullBaseUrl: 'http://localhost:9000',
  },
});
