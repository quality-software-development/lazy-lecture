declare namespace Cypress {
  interface Chainable {
    /**
     * Навигация с hash-роутом через baseUrl
     * @example cy.hashVisit('/sign_up')
     */
    hashVisit(path: string): Chainable<void>;
    registerAndPrepareUser(username: string, password: string): Chainable<JQuery<any>>;

  }
}
