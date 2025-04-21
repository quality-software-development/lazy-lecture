/* eslint-disable */

/// <reference types="cypress" />

describe('1️⃣ Регистрация с валидацией + авто‑логин', () => {
  const uniqueUser = `user_${Date.now()}`;

  beforeEach(() => {
    // 🛡️ Мокаем отсутствие авторизации
    cy.intercept('GET', '/auth/info', {
      statusCode: 401,
      body: { detail: 'Invalid or expired token' },
    }).as('authInfo');

    cy.intercept('POST', '/auth/refresh', {
      statusCode: 401,
      body: { detail: 'Refresh token expired' },
    });

    cy.hashVisit('/sign_up');

    cy.get('[data-test="ui-testing-auth-page-login-input"]', { timeout: 10000 }).should('exist');
    cy.get('[data-test="ui-testing-auth-page-password-input"]', { timeout: 10000 }).should('exist');
  });

    it('Шаг 2: Пустой пароль — показывает "Введите пароль"', () => {
      cy.get('[data-test="ui-testing-auth-page-login-input"]')
        .clear()
        .type('someuser');

      cy.get('[data-test="ui-testing-auth-page-password-input"]')
        .clear(); // оставляем поле пустым

      cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

      cy.get('[data-test="ui-testing-auth-page-password-input"]')
        .parents('.q-field')
        .find('.q-field__messages')
        .should('contain.text', 'Введите пароль');
    });

    it('Шаг 3: Валидация пустого логина (client-side)', () => {
      cy.get('[data-test="ui-testing-auth-page-login-input"]')
        .click({ force: true })
        .clear(); // логин пустой

      cy.get('[data-test="ui-testing-auth-page-password-input"]')
        .click({ force: true })
        .clear()
        .type('GoodP@ss123', { force: true });

      cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

      cy.get('[data-test="ui-testing-auth-page-login-input"]')
        .parents('.q-field')
        .find('.q-field__messages')
        .should('contain.text', 'Введите логин');
    });

  it('Шаг 4: Успешная регистрация и авто‑логин', () => {
    cy.intercept('POST', '/auth/register', {
      statusCode: 200,
      body: {
        access_token: 'mocked-access-token',
        refresh_token: 'mocked-refresh-token',
      },
    }).as('register');

    cy.intercept('POST', '/auth/login', {
      statusCode: 200,
      body: {
        access_token: 'mocked-access-token',
        refresh_token: 'mocked-refresh-token',
      },
    }).as('login');

    cy.intercept('GET', '/auth/info', {
      statusCode: 200,
      body: {
        id: 1,
        username: uniqueUser,
        active: true,
        can_interact: true,
        role: 'user',
        create_date: new Date().toISOString(),
        update_date: new Date().toISOString(),
      },
    }).as('authInfo');

    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .click({ force: true })
      .clear()
      .type(uniqueUser, { force: true });

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .click({ force: true })
      .clear()
      .type('GoodP@ss123', { force: true });

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.wait('@register').its('response.statusCode').should('eq', 200);
    cy.wait('@login').its('response.statusCode').should('eq', 200);

    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });

  it('Шаг 5: Токен действует после перезагрузки защищённой страницы', () => {
    cy.intercept('GET', '/auth/info', {
      statusCode: 200,
      body: {
        id: 1,
        username: uniqueUser,
        role: 'user',
        active: true,
        can_interact: true,
        create_date: new Date().toISOString(),
        update_date: new Date().toISOString(),
      },
    }).as('authInfo');

    cy.visit('/transcripts');
    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });
});
