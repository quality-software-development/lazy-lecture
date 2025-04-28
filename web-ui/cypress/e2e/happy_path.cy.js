/* eslint-disable */
/// <reference types="cypress" />
import { generateLatinUsername } from '../support/utils';

const username = generateLatinUsername();
const password      = 'GoodP@ss123456#Aa';
const fileName      = 'sample_19m57s.mp3';
const downloadName  = 'Транскрипция №1.txt';
const taskId        = 1;
const iso           = new Date().toISOString();
const audioLenSecs  = 1197;
const mockChunks = [
  { chunk_order: 0, chunk_size_secs: 900, id: 1, transcription: 'Здравствуйте, это пример транскрипции за первые 15 минут.' },
  { chunk_order: 1, chunk_size_secs: 297, id: 2, transcription: 'Следующий фрагмент продолжается, и вот его текст.' },
];

describe('2️⃣ Happy-path: Web → API → Worker → Web', () => {
  const apiUrl     = Cypress.env('apiUrl');
  const adminToken = Cypress.env('admin_secret_token');
  let uid;
  before(() => {
    cy.registerAndPrepareUser(username, password).then(id => {
      uid = id;
    });
  });

  it('🧪 Полный happy-path', () => {
    /* ─── Мокаем ВСЁ перед загрузкой страницы ───────────────────── */

    cy.log('🛠️ Настраиваем моки API');

    cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: 100, total: 1,
        transcriptions: [{
          id: taskId, creator_id: uid, audio_len_secs: audioLenSecs,
          chunk_size_secs: 900, current_state: 'completed',
          create_date: iso, update_date: iso, description: fileName,
        }],
      },
    }).as('listReq');

    cy.intercept('GET', `${apiUrl}/transcript?task_id=${taskId}&skip=0&limit=100`, {
      statusCode: 200,
      body: { page: 1, pages: 1, size: 50, total: 2, transcriptions: mockChunks },
    }).as('chunksReq');

    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 200,
      body: { message: 'ok', task_id: taskId, file: 'object_storage/1.mp3' },
    }).as('uploadAudio');
    cy.intercept('POST', `${apiUrl}/transcriptions/*/start`, { statusCode: 200 }).as('startReq');

    /* ─── UI: Логинимся ─────────────────────────────────────────── */

    cy.log('🌐 Открываем логин-страницу');
    cy.hashVisit('/log_in');

    cy.log('📋 Вводим логин и пароль');
    cy.get('[data-test="ui-testing-auth-page-login-input"]').type(username);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').type(password);
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.log('➡️ Ждём загрузку транскрипций');
    cy.wait('@listReq');
    cy.location('hash', { timeout: 10_000 }).should('include', '#/transcripts');

    /* ─── UI: Загружаем файл ────────────────────────────────────── */

    cy.log('📤 Загружаем файл для транскрипции');
    cy.get('.q-uploader__input[type="file"]').selectFile(`cypress/fixtures/${fileName}`, { force: true });

    cy.log('🚀 Нажимаем на отправку файла');
    cy.contains('i', 'cloud_upload').click();

    cy.log('📍 Ждём переход на страницу транскрипции');
    cy.location('hash', { timeout: 10_000 }).should('include', `#/transcripts/${taskId}`);
    cy.wait('@chunksReq');

    /* ─── Проверяем UI ───────────────────────────────────────────── */

    cy.log('✅ Проверяем, что прогресс-бар появился');
    cy.get('.ui-trancscript-page-progress-bar');

    cy.log('🧾 Проверяем текст всех чанков');
    cy.get('[data-test="ui-testing-transcript-chunk"]')
      .should('have.length', mockChunks.length)
      .each((chunkEl, idx) => {
        cy.wrap(chunkEl).should('contain.text', mockChunks[idx].transcription);
      });

    /* ─── Проверяем Экспорт ─────────────────────────────────────── */

    cy.log('📄 Проверяем экспорт транскрипции в TXT');
    cy.get('[title="Экспорт в .txt"]').click();
    cy.readFile(`${Cypress.config('downloadsFolder')}/${downloadName}`, { timeout: 10_000 })
      .should('include', mockChunks[0].transcription)
      .and('include', mockChunks[1].transcription);
  });
});
