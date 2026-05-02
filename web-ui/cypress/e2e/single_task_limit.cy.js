/* eslint-disable */
/// <reference types="cypress" />
//
// E2E-003 — Ограничение одной задачи и отмена
// см. docs/Курсовая_работа_ТРКПО_E2E.docx.pdf, раздел 2.3
//
import { generateLatinUsername } from '../support/utils';

const username   = generateLatinUsername();
const password   = 'GoodP@ss123456#Aa';
const fileA      = 'sample_ru_120s.mp3';
const fileB      = 'sample_ru_20s.mp3';
const taskA      = 1;
const taskB      = 2;
const apiUrl     = Cypress.env('apiUrl');
const iso        = new Date().toISOString();
const mockChunks = [
  { chunk_order: 0, chunk_size_secs: 60, id: 1, transcription: 'Здравствуйте, это пример транскрипции за первую минуту.' },
  { chunk_order: 1, chunk_size_secs: 0,  id: 2, transcription: null },
];

describe('E2E-003 3️⃣ Ограничение одной задачи + отмена', () => {
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

  it('🧪 Ограничение одной задачи + отмена', function() {
    cy.log('🎯 Настройка моков для первой транскрипции (A)');
    cy.then(() => {
      tasks = [{
        id: taskA, creator_id: uid, audio_len_secs: 120, chunk_size_secs: 60,
        current_state: 'queued', create_date: iso, update_date: iso, description: fileA,
      }];
      interceptList('list');

      cy.intercept('GET', `${apiUrl}/transcript?task_id=${taskA}*&limit=*`, {
        statusCode: 200,
        body: {
          page: 1, pages: 1, size: mockChunks.length, total: mockChunks.length,
          transcriptions: mockChunks,
        },
      }).as('chunksA');
    });

    cy.log('🔐 Логинимся в систему');
    cy.hashVisit('/log_in');
    cy.get('[data-test="ui-testing-auth-page-login-input"]').type(username);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').type(password);
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.wait('@list');
    cy.location('hash').should('include', '#/transcripts');

    cy.log('📤 Загружаем первый аудиофайл');
    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 200,
      body: { message: 'ok', task_id: taskA, file: 'object_storage/a.mp3' },
    }).as('uploadA');

    cy.intercept('GET', `${apiUrl}/transcription/info?task_id=${taskA}`, {
      statusCode: 200,
      body: {
        id: taskA, creator_id: uid, audio_len_secs: 120, chunk_size_secs: 60,
        current_state: 'in_progress', create_date: iso, update_date: iso, description: fileA,
      },
    }).as('infoA');

    cy.get('.q-uploader__input[type="file"]').selectFile(`cypress/fixtures/${fileA}`, { force: true });
    cy.contains('i', 'cloud_upload').click();

    cy.wait('@uploadA');
    cy.wait('@chunksA');
    cy.contains(mockChunks[0].transcription).should('be.visible');

    cy.location('hash').should('include', `#/transcripts/${taskA}`);
    cy.get('.ui-trancscript-page-progress-bar').should('exist');

    cy.log('📥 Пытаемся загрузить второй файл (ожидаем ошибку)');
    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 400,
      body: { detail: 'Already processing transcription.' },
    }).as('uploadB');

    cy.then(() => interceptList('list_again'));
    cy.hashVisit('/transcripts');
    cy.reload();
    cy.wait('@list_again');

    cy.get('.q-uploader__input[type="file"]').selectFile(`cypress/fixtures/${fileB}`, { force: true });
    cy.contains('i', 'cloud_upload').click();
    cy.wait('@uploadB');

    cy.get('.q-notification__message')
      .should('contain.text', 'Нельзя загрузить: уже обрабатывается другое аудио.');

    cy.log('🛑 Открываем меню и отменяем обработку A');
    cy.get('button[aria-label="Menu"]').click();
    cy.contains(fileA).click();
    cy.location('hash').should('include', `#/transcripts/${taskA}`);

    cy.intercept('POST', `${apiUrl}/transcriptions/${taskA}/cancel`, { statusCode: 200 }).as('cancelA');

    cy.contains('Отменить обработку').click();
    cy.wait('@cancelA');

    cy.log('🔄 Проверяем обновление статуса на отменённую задачу');
    cy.then(() => {
      tasks[0].current_state = 'cancelled';
      interceptList('list_cancelled');
    });
    cy.reload();
    cy.wait('@list_cancelled');
    cy.contains('Обработка отменена').should('be.visible');

    cy.log('📦 Закрываем транскрипцию и загружаем файл B');
    cy.get('[title="Закрыть транскрипцию"]').click();

    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 200,
      body: { message: 'ok', task_id: taskB, file: 'object_storage/b.mp3' },
    }).as('uploadC');

    cy.intercept('GET', `${apiUrl}/transcript?task_id=${taskB}&skip=0&limit=100`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: 2, total: 2,
        transcriptions: [
          { chunk_order: 0, chunk_size_secs: 20, id: 1, transcription: 'чанк 1' },
          { chunk_order: 1, chunk_size_secs: 0,  id: 2, transcription: null },
        ],
      },
    }).as('chunksB');

    cy.get('.q-uploader__input[type="file"]').selectFile(`cypress/fixtures/${fileB}`, { force: true });
    cy.contains('i', 'cloud_upload').click();
    cy.wait('@uploadC');
    cy.wait('@chunksB');

    cy.log('🔎 Проверяем переход на задачу B');
    cy.then(() => {
      tasks.push({
        id: taskB, creator_id: uid, audio_len_secs: 20, chunk_size_secs: 60,
        current_state: 'in_progress',
        create_date: new Date().toISOString(), update_date: new Date().toISOString(),
        description: fileB,
      });
      interceptList('list_with_b');
    });

    cy.reload();
    cy.wait('@list_with_b');
    cy.location('hash').should('include', `#/transcripts/${taskB}`);
  });
});
