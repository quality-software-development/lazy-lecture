/* eslint-disable */
/// <reference types="cypress" />
import { generateLatinUsername } from '../support/utils';

const username = generateLatinUsername();
const password = 'GoodP@ss123456#Aa';
const apiUrl = Cypress.env('apiUrl');

describe('5️⃣ Ограничения аудио: короткий / длинный / формат / размер', () => {
  let uid;

  before(() => {
    cy.registerAndPrepareUser(username, password).then(id => {
      uid = id;
    });
  });

  beforeEach(() => {
    cy.hashVisit('/log_in');
    cy.get('[data-test="ui-testing-auth-page-login-input"]').type(username);
    cy.get('[data-test="ui-testing-auth-page-password-input"]').type(password);
    cy.get('[data-test="ui-testing-auth-page-submit-btn"]').click();
    cy.location('hash').should('include', '#/transcripts');
  });

  const uploadFile = (filePath) => {
    cy.get('.q-uploader__input[type="file"]').selectFile(filePath, { force: true });
  };

  it('🧪 Проверка ошибок при загрузке неподходящих аудиофайлов', () => {
    cy.log('📥 Пытаемся загрузить слишком короткий файл');
    uploadFile('cypress/fixtures/too_short.mp3');
    cy.get('.q-notification__message').should('contain.text', 'Длина аудио должна быть больше 10 секунд.');

    cy.log('📥 Пытаемся загрузить слишком длинный файл');
    uploadFile('cypress/fixtures/too_long.mp3');
    cy.get('.q-notification__message').should('contain.text', 'Длина аудио должна быть меньше 2 часов.');

    cy.log('📥 Пытаемся загрузить файл неподдерживаемого формата (.wav)');
    uploadFile('cypress/fixtures/invalid_format.wav');
    cy.get('.q-uploader__list').find('.q-uploader__file').should('have.length', 0);

    cy.log('📥 Пытаемся загрузить слишком большой файл (>200MB)');
    cy.window().then(win => {
      const bigFile = new File([new ArrayBuffer(201 * 1024 * 1024)], 'too_big.mp3', { type: 'audio/mpeg' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(bigFile);

      cy.get('.q-uploader__input[type="file"]').then(input => {
        input[0].files = dataTransfer.files;
        input[0].dispatchEvent(new Event('change', { bubbles: true }));
      });
    });

    cy.get('.q-notification__message', { timeout: 5000 })
      .should('contain.text', 'Размер аудио должен быть меньше 200 Мбайт.');

    cy.log('📥 Загружаем правильный файл для проверки успешной обработки');

    cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: 1, total: 1,
        transcriptions: [{
          id: 1,
          creator_id: uid,
          audio_len_secs: 100,
          chunk_size_secs: 60,
          current_state: 'completed',
          create_date: new Date().toISOString(),
          update_date: new Date().toISOString(),
          description: 'sample_19m57s.mp3',
        }],
      },
    }).as('mockTranscriptions');

    cy.intercept('GET', `${apiUrl}/transcript?task_id=1&skip=0&limit=100`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: 1, total: 1,
        transcriptions: [{
          chunk_order: 0,
          chunk_size_secs: 60,
          id: 1,
          transcription: 'Тестовый текст чанка',
        }],
      },
    }).as('mockTranscript');

    cy.intercept('POST', '**/upload-audiofile', {
      statusCode: 200,
      body: { message: 'ok', task_id: 1, file: 'object_storage/sample_19m57s.mp3' },
    }).as('uploadGood');

    uploadFile('cypress/fixtures/sample_19m57s.mp3');
    cy.contains('i', 'cloud_upload').click();

    cy.wait('@uploadGood');
    cy.location('hash').should('include', '#/transcripts/1');
    cy.wait('@mockTranscript');
    cy.contains('Тестовый текст чанка').should('be.visible');

    cy.log('✅ Всё прошло корректно, файл загружен и обработан.');
  });
});
