/* eslint-disable */
/// <reference types="cypress" />

import { generateLatinUsername } from '../support/utils';

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
    cy.get('[data-test="ui-testing-auth-page-login-input"]')
      .clear()
      .type(generateLatinUsername());

    cy.get('[data-test="ui-testing-auth-page-password-input"]')
      .clear()
      .type('GoodP@ss123456#Aa');

    cy.log('🚀 Отправляем форму регистрации');
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.log('✅ Проверяем успешный редирект на /transcripts');
    cy.url({ timeout: 10000 }).should('include', '/transcripts');

    cy.log('🔄 Перезагружаем защищённую страницу');
    cy.hashVisit('/transcripts');

    cy.log('✅ Проверяем, что остались на /transcripts');
    cy.url({ timeout: 10000 }).should('include', '/transcripts');
  });

  it('Шаг 8: Попытка регистрации с уже существующим логином — ошибка', () => {
    const takenUsername = 'existingUser';

    // Подставляем фиктивного юзера, который "уже есть"
    cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type(uniqueUser);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type('GoodP@ss123');

    // Мокаем ответ сервера — 400 Bad Request
    cy.intercept('POST', '**/auth/register', {
      statusCode: 400,
      body: { detail: 'Пользователь уже существует' }
    }).as('registerFail');

    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();
    cy.wait('@registerFail');

    cy.contains('Ошибка регистрации.').should('be.visible').realHover();
    cy.get('.q-tooltip').should('contain.text', 'Пользователь уже существует');
  });
});
