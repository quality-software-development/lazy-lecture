/* eslint-disable */
/// <reference types="cypress" />

function genUser(n = 16) {
  const a = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return Array.from({ length: n }, () => a[Math.floor(Math.random() * a.length)]).join('');
}

const username      = genUser();
const password      = 'GoodP@ss123456#Aa';
const fileName      = 'sample_19m57s.mp3';
const downloadName  = 'Транскрипция №1.txt';
const taskId        = 1;
const iso           = new Date().toISOString();
const audio_len_secs = 1197;
const mockChunks = [
  { chunk_order: 0, chunk_size_secs: 900, id: 1, transcription: 'Здравствуйте, это пример транскрипции за первые 15 минут.' },
  { chunk_order: 1, chunk_size_secs: 297, id: 2, transcription: 'Следующий фрагмент продолжается, и вот его текст.' },
];

describe('2️⃣ Happy-path: Web → API → Worker → Web', () => {
  const apiUrl     = Cypress.env('apiUrl');
  const adminToken = Cypress.env('admin_secret_token');

  it('🧪 Полный happy-path', () => {

    cy.log('🔐 Регистрируем пользователя');
    cy.request('POST', `${apiUrl}/auth/register`, { username, password });

    cy.log('🔑 Логинимся');
    cy.request('POST', `${apiUrl}/auth/login`, { username, password })
      .its('body.access_token')
      .as('token');

    cy.get('@token').then(token => {
      cy.log('👤 Получаем информацию о пользователе');
      cy.request({
        method: 'GET',
        url: `${apiUrl}/auth/info`,
        headers: { Authorization: `Bearer ${token}` },
      }).then(res => {
        const uid = res.body.id;
        cy.wrap(uid).as('userId')

        cy.log('🛠️ Выдаём доступ can_interact');
        cy.request({
          method: 'PATCH',
          url: `${apiUrl}/auth/patch?user_id=${uid}&secret_admin_token=${adminToken}`,
          headers: { Authorization: `Bearer ${token}` },
          body: { can_interact: true },
        });
      });
    });

    /* ─── Мокаем ВСЁ перед загрузкой страницы ───────────────────── */

    cy.log('🛠️ Настраиваем моки API');
    cy.get('@userId').then(userId => {
        cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
            statusCode: 200,
            body: {
                page: 1, pages: 1, size: 100, total: 1,
                transcriptions: [{
                    id: taskId, creator_id: userId, audio_len_secs: audio_len_secs,
                    chunk_size_secs: 900, current_state: 'completed',
                    create_date: iso, update_date: iso, description: fileName,
                }],
            },
        }).as('listReq');
    });

    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 200,
      body: { message: 'ok', task_id: taskId, file: 'object_storage/1.mp3' },
    }).as('uploadAudio');

    cy.intercept('GET', `${apiUrl}/transcript?task_id=${taskId}&skip=0&limit=100`, {
      statusCode: 200,
      body: { page: 1, pages: 1, size: 50, total: 2, transcriptions: mockChunks },
    }).as('chunksReq');

    cy.intercept('POST', `${apiUrl}/transcriptions/*/start`, { statusCode: 200 }).as('startReq');

    /* ─── Логинимся в UI ────────────────────────────────────────── */

    cy.log('🌐 Открываем логин-страницу');
    cy.hashVisit('/log_in');

    cy.log('📋 Вводим логин и пароль');
    cy.get('[data-test="ui-testing-auth-page-login-input"]').type(username);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').type(password);
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

    cy.log('➡️ Проверяем переход на страницу транскрипций');
    cy.wait('@listReq');
    cy.location('hash', { timeout: 10_000 }).should('include', '#/transcripts');

    /* ─── Загружаем аудио ───────────────────────────────────────── */

    cy.log('📤 Загружаем файл');
    cy.get('.q-uploader__input[type="file"]').selectFile(`cypress/fixtures/${fileName}`, { force: true });

    cy.log('🚀 Отправляем на транскрипцию');
    cy.contains('i', 'cloud_upload').click();

    cy.log('📍 Ждём переход на страницу транскрипции');
    cy.location('hash', { timeout: 10_000 }).should('include', `#/transcripts/${taskId}`);
    cy.wait('@chunksReq');

    /* ─── Проверяем отрисовку ───────────────────────────────────── */

    cy.log('✅ Проверяем прогресс-бар');
    cy.get('.ui-trancscript-page-progress-bar');


    cy.log('🧾 Проверяем чанки транскрипции');
    cy.get('[data-test="ui-testing-transcript-chunk"]').should('have.length', 2)
      .first().should('contain.text', mockChunks[0].transcription);

    /* ─── Проверяем экспорт ─────────────────────────────────────── */

    cy.log('📄 Проверяем экспорт в текстовый файл');
    cy.get('[title="Экспорт в .txt"]').click();
    cy.readFile(`${Cypress.config('downloadsFolder')}/${downloadName}`, { timeout: 10_000 })
      .should('include', mockChunks[0].transcription);
  });
});
