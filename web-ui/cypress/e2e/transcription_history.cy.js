/* eslint-disable */
/// <reference types="cypress" />
//
// E2E-004 — История транскрипций и просмотр чанков
// см. docs/Курсовая_работа_ТРКПО_E2E.docx.pdf, раздел 2.4
//
import { generateLatinUsername } from '../support/utils';

const username = generateLatinUsername();
const password = 'GoodP@ss123456#Aa';
const fileA    = 'sample_ru_120s.mp3';
const fileB    = 'sample_ru_20s.mp3';
const taskA    = 1;
const taskB    = 2;
const apiUrl   = Cypress.env('apiUrl');
const now      = new Date();
const isoNow      = now.toISOString();
const isoEarlier  = new Date(now.getTime() - 5 * 60_000).toISOString();

const chunksA = [
  {
    chunk_order: 0,
    chunk_size_secs: 60,
    id: 1,
    transcription: 'Текст первой части. Здесь идёт длинный фрагмент транскрипции для проверки отображения.',
  },
  { chunk_order: 1, chunk_size_secs: 60, id: 2, transcription: 'Текст второй части.' },
  { chunk_order: 2, chunk_size_secs: 0,  id: 3, transcription: null },
];

describe('E2E-004 4️⃣ История транскрипций + просмотр чанков', () => {
  let uid;
  let tasks = [];

  const interceptList = (alias = 'list') => {
    cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
      statusCode: 200,
      body: { page: 1, pages: 1, size: 100, total: tasks.length, transcriptions: tasks },
    }).as(alias);
  };

  before(() => {
    cy.registerAndPrepareUser(username, password).then(id => { uid = id; });
  });

  it('🧪 Проверка истории транскрипций и чанков', function () {
    cy.then(() => {
      tasks = [
        {
          id: taskA, creator_id: uid, audio_len_secs: 120, chunk_size_secs: 60,
          current_state: 'completed', create_date: isoEarlier, update_date: isoEarlier,
          description: fileA,
        },
        {
          id: taskB, creator_id: uid, audio_len_secs: 20, chunk_size_secs: 60,
          current_state: 'completed', create_date: isoNow, update_date: isoNow,
          description: fileB,
        },
      ];
      interceptList('list');
    });

    cy.log('➡️ Логинимся в систему');
    cy.hashVisit('/log_in');
    cy.get('[data-test="ui-testing-auth-page-login-input"]').type(username);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').type(password);
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.wait('@list');
    cy.location('hash').should('include', '#/transcripts');

    cy.log('➡️ Проверяем отображение истории транскрипций');
    cy.get('button[aria-label="Menu"]').click();
    cy.contains(fileB).should('be.visible');
    cy.contains(fileA).should('be.visible');

    cy.intercept('GET', `${apiUrl}/transcript?task_id=${taskA}*&limit=*`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: chunksA.length, total: chunksA.length,
        transcriptions: chunksA,
      },
    }).as('chunksA');

    cy.log('➡️ Открываем транскрипцию A');
    cy.contains(fileA).click();
    cy.location('hash').should('include', `#/transcripts/${taskA}`);
    cy.wait('@chunksA');

    cy.log('✅ Проверяем что видны только заполненные чанки');
    cy.get('[data-test="ui-testing-transcript-chunk"]').filter(':has(p)').should('have.length', 2);
    cy.contains('Текст первой части').should('be.visible');
    cy.contains('Текст второй части.').should('be.visible');

    cy.log('➡️ Переход к чанку через клик на прогресс-метку');
    cy.get('[rect-idx="1"]').click();

    cy.log('✅ Проверяем что скроллинг на чанк прошёл');
    cy.get(`#chunk-2`).should('be.visible');
  });
});
