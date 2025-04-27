/* eslint-disable */
/// <reference types="cypress" />

function generateLatinUsername(length = 16) {
  const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  let username = '';
  while (username.length < length) {
    username += letters[Math.floor(Math.random() * letters.length)];
  }
  return username;
}

const uniqueUser = generateLatinUsername();

describe('1️⃣ Регистрация с валидацией + авто‑логин (реальный API)', () => {
  beforeEach(() => {
    cy.hashVisit('/sign_up');

    cy.get('[data-test="ui-testing-auth-page-login-input"]', { timeout: 10000 }).should('exist');
    cy.get('[data-test="ui-testing-auth-page-password-input"]', { timeout: 10000 }).should('exist');
  });

  it('Шаг 2: Пустой пароль — показывает "Введите пароль"', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear()
      .type('someuser');

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear(); // оставляем пустым

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .parents('.q-field')
      .find('.q-field__messages')
      .should('contain.text', 'Введите пароль');
  });

  it('Шаг 3: Пустой логин — показывает "Введите логин"', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear();

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear()
      .type('GoodP@ss123');

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .parents('.q-field')
      .find('.q-field__messages')
      .should('contain.text', 'Введите логин');
  });

  it('Шаг 4: Некорректный пароль — ошибка в тултипе', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear()
      .type('ValidLogin');

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear()
      .type('short');

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.contains('Ошибка регистрации.')
      .should('be.visible')
      .realHover();

    cy.get('.q-tooltip')
      .should('exist')
      .invoke('text')
      .should('include', 'Password must be 8-256 characters');
  });

  it('Шаг 5: Некорректный логин — ошибка в тултипе', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear()
      .type('ru'); // невалидный логин

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear()
      .type('GoodP@ss123');

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.contains('Ошибка регистрации.')
      .should('be.visible')
      .realHover();

    cy.get('.q-tooltip')
      .should('exist')
      .invoke('text')
      .should('include', 'Username must consist');
  });

  it('Шаг 6: Успешная регистрация и авто‑логин', () => {
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear()
      .type(uniqueUser);

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear()
      .type('GoodP@ss123456#Aa');

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });

  it('Шаг 7: Токен работает после перезагрузки защищённой страницы', () => {
    cy.visit('/transcripts');
    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });
});
