/* eslint-disable */
/// <reference types="cypress" />

function generateUsername(length = 16) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

const username = generateUsername();
const password = 'GoodP@ss123456#Aa';
const filename = 'sample_ru_20s.mp3';
const downloadFileName = 'sample_ru_20s.txt';

const mockTranscript = {
  id: 1,
  status: 'completed',
  chunks: [
    {
      start: 0,
      end: 900,
      text: 'Здравствуйте, это пример транскрипции за первые 15 минут.',
    },
    {
      start: 900,
      end: 1800,
      text: 'Следующий фрагмент продолжается, и вот его текст.',
    },
  ],
  full_text:
    'Здравствуйте, это пример транскрипции за первые 15 минут. Следующий фрагмент продолжается, и вот его текст.',
};

describe('2️⃣ Happy‑path: Web → API → Worker → Web', () => {
  const apiUrl = Cypress.env('apiUrl');
  const adminToken = Cypress.env('admin_secret_token');

  it('🧪 Полный happy-path', () => {
    cy.log('🔐 Регистрируем пользователя');
    cy.request('POST', `${apiUrl}/auth/register`, { username, password }).then((res) => {
      expect(res.status).to.eq(201);

      cy.log('🔑 Логинимся');
      return cy.request('POST', `${apiUrl}/auth/login`, { username, password });
    }).then((loginRes) => {
      const access_token = loginRes.body.access_token;

      cy.log('👤 Получаем ID пользователя');
      return cy.request({
        method: 'GET',
        url: `${apiUrl}/auth/info`,
        headers: { Authorization: `Bearer ${access_token}` },
      }).then((infoRes) => {
        const userId = infoRes.body.id;

        cy.log('🛠️ Выдаем can_interact');
        return cy.request({
          method: 'PATCH',
          url: `${apiUrl}/auth/patch?user_id=${userId}&secret_admin_token=${adminToken}`,
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
          body: { can_interact: true },
          failOnStatusCode: false,
        }).then(() => ({ access_token }));
      });
    }).then(({ access_token }) => {
      cy.log('🌐 Переход на логин');
      cy.hashVisit('/log_in');
      cy.get('[data-test="ui-testing-auth-page-login-input"]').clear().type(username);
      cy.get('[data-test="ui-testing-auth-page-password-input"]').clear().type(password);
      cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();

      cy.log('➡️ Переход на /transcripts');
      cy.location('hash', { timeout: 10000 }).should('include', '#/transcripts');

      cy.log('📤 Загружаем файл');
      cy.intercept('POST', '**/upload-audiofile', { statusCode: 200 }).as('uploadAudio');
      cy.get('.q-uploader__input[type="file"]', { timeout: 10000 }).selectFile(`cypress/fixtures/${filename}`, { force: true });
      cy.get('.q-uploader__title', { timeout: 5000 }).should('contain.text', filename);

      cy.log('🚀 Отправляем на транскрипцию');
      cy.intercept('POST', `${apiUrl}/transcriptions/*/start`, { statusCode: 200 }).as('startTranscription');
      cy.contains('i', 'cloud_upload').click();

      cy.log('🌐 Мокаем прогресс и детали транскрипции');
      cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
        statusCode: 200,
        body: { items: [], total: 0 },
      }).as('getTranscriptsList');

      cy.intercept('GET', `${apiUrl}/transcriptions/1/status`, {
        statusCode: 200,
        body: { status: 'processing', progress: 100 },
      }).as('progressCheck');

      // ❗ ВАЖНО: мок результата транскрипции до visit!
      cy.intercept('GET', `${apiUrl}/transcriptions/1`, {
        statusCode: 200,
        body: mockTranscript,
      }).as('getTranscript');

      cy.log('📍 Переход на страницу прогресса');
      cy.hashVisit('/transcripts/1');
      cy.wait('@progressCheck');

      cy.log('⏳ Проверка прогресс-бара');
      cy.get('[data-test="ui-testing-progress-bar"]', { timeout: 10000 }).should('exist');
      cy.get('[data-test="ui-testing-progress-bar"]').should('contain.text', '100');

      cy.log('📥 Проверка списка и переход в деталку');
      cy.wait('@getTranscript');
      cy.get('[data-test="ui-testing-transcript-list"]')
        .find('.transcript-item')
        .first()
        .click();

      cy.log('🧾 Проверяем чанки');
      cy.get('[data-test="ui-testing-transcript-chunk"]').each(($chunk, index) => {
        expect($chunk.text().trim()).to.include(mockTranscript.chunks[index].text);
      });

      cy.log('📄 Проверка экспорта');
      cy.get('[data-test="ui-testing-export-btn"]').click();
      const downloadsFolder = Cypress.config('downloadsFolder');
      cy.readFile(`${downloadsFolder}/${downloadFileName}`, { timeout: 10000 }).then((txt) => {
        expect(txt.trim()).to.eq(mockTranscript.full_text.trim());
      });
    });
  });
});
