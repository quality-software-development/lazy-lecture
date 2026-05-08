/* eslint-disable */
/// <reference types="cypress" />
//
// E2E-001 — Регистрация с валидацией и авто-логином
// см. docs/Курсовая_работа_ТРКПО_E2E.docx.pdf, раздел 2.1
//
import { generateLatinUsername } from '../support/utils';

const uniqueUser = generateLatinUsername();

describe('E2E-001 1️⃣ Регистрация с валидацией + авто-логин (реальный API)', () => {
  beforeEach(() => {
    cy.clearLocalStorage();
    cy.clearCookies();
    cy.hashVisit('/sign_up');

    cy.get('[data-test="ui-testing-auth-page-login-input"]', { timeout: 10000 }).should('exist');
    cy.get('[data-test="ui-testing-auth-page-password-input"]', { timeout: 10000 }).should('exist');
  });

  it('Шаг 2: Пустой пароль — показывает "Введите пароль"', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type('someuser');
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear();
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .parents('.q-field').find('.q-field__messages')
      .should('contain.text', 'Введите пароль');
  });

  it('Шаг 3: Пустой логин — показывает "Введите логин"', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear();
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .parents('.q-field').find('.q-field__messages')
      .should('contain.text', 'Введите логин');
  });

  it('Шаг 4: Некорректный пароль — ошибка в тултипе', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type('ValidLogin');
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('short');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.contains('Ошибка регистрации.').should('be.visible').realHover();
    cy.get('.q-tooltip').should('exist').invoke('text')
      .should('include', 'Password must be 8-256 characters');
  });

  it('Шаг 5: Некорректный логин — ошибка в тултипе', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type('ru');
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.contains('Ошибка регистрации.').should('be.visible').realHover();
    cy.get('.q-tooltip').should('exist').invoke('text')
      .should('include', 'Username must consist');
  });

  it('Шаг 6: Успешная регистрация и авто‑логин', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type(uniqueUser);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123456#Aa');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });

  it('Шаг 7: Токен работает после перезагрузки защищённой страницы', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type(generateLatinUsername());
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123456#Aa');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();
    cy.url({ timeout: 10000 }).should('include', '/transcripts');

    cy.hashVisit('/transcripts');
    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });

  it('Шаг 8: Регистрация с уже существующим логином — ошибка', () => {
    // Сначала регистрируем уникального пользователя через прямой API-вызов,
    // чтобы оставаться на странице /sign_up без редиректов.
    const dup = generateLatinUsername();
    const apiUrl = Cypress.env('apiUrl');
    cy.request('POST', `${apiUrl}/auth/register`, { username: dup, password: 'GoodP@ss123456#Aa' });

    // Теперь пробуем зарегистрироваться через UI с тем же логином
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type(dup);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123456#Aa');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.contains('Ошибка регистрации.').should('be.visible');
  });
});
