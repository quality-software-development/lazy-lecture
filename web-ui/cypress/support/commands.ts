/// <reference types="cypress" />

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

Cypress.Commands.add('hashVisit', (hashPath: string) => {
    // Получаем baseUrl только ВНУТРИ цепочки Cypress
    cy.then(() => {
        const baseUrl = Cypress.config('baseUrl');
        if (!baseUrl) {
            throw new Error('[hashVisit] baseUrl is not defined in Cypress config');
        }

        // Посещаем путь
        return cy.visit(`${baseUrl}/#${hashPath}`);
    });
});

Cypress.Commands.add('registerAndPrepareUser', (username: string, password: string) => {
    const apiUrl = Cypress.env('apiUrl');
    const adminToken = Cypress.env('admin_secret_token');
    cy.request('POST', `${apiUrl}/auth/register`, {username, password});
    return cy.request('POST', `${apiUrl}/auth/login`, {username, password})
        .then(loginRes => {
            const token = loginRes.body.access_token;
            return cy.request({
                method: 'GET',
                url: `${apiUrl}/auth/info`,
                headers: {Authorization: `Bearer ${token}`},
            }).then(infoRes => {
                const userId = infoRes.body.id;
                cy.request({
                    method: 'PATCH',
                    url: `${apiUrl}/auth/patch?user_id=${userId}&secret_admin_token=${adminToken}`,
                    headers: {Authorization: `Bearer ${token}`},
                    body: {can_interact: true},
                });
                return cy.wrap(userId);
            });
        });
});

export {};
