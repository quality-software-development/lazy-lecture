/* eslint-disable */
/// <reference types="cypress" />
import { generateLatinUsername } from '../support/utils';


const username = generateLatinUsername();
const password = 'GoodP@ss123456#Aa';
const fileA = 'sample_19m57s.mp3';
const fileB = 'sample_ru_120s.mp3';
const taskA = 1;
const taskB = 2;
const apiUrl = Cypress.env('apiUrl');
const adminToken = Cypress.env('admin_secret_token');
const now = new Date();
const isoNow = now.toISOString();
const isoEarlier = new Date(now.getTime() - 5 * 60000).toISOString(); // 5 мин назад

const chunksA = [
  {
    chunk_order: 0,
    chunk_size_secs: 900,
    id: 1,
    transcription: `Текст первой части. Дальше текст из Алисы в стране чудес. Алисе наскучило сидеть с сестрой без дела на берегу реки; разок-другой она заглянула в книжку, которую читала сестра, но там не было ни картинок, ни разговоров. - Что толку в книжке, - подумала Алиса, - если в ней нет ни картинок, ни разговоров? Она сидела и размышляла, не встать ли ей и не нарвать ли цветов для венка; мысли ее текли медленно и несвязно - от жары ее клонило в сон. Конечно, сплести венок было бы очень приятно, но стоит ли ради этого подыматься? Вдруг мимо пробежал белый кролик с красными глазами. Конечно, ничего удивительного в этом не было. Правда, Кролик на бегу говорил: - Ах, боже мой, боже мой! Я опаздываю. Но и это не показалось Алисе особенно странным. (Вспоминая об этом позже, она подумала, что ей следовало бы удивиться, однако в тот миг все казалось ей вполне естественным.) Но, когда Кролик вдруг вынул часы из жилетного кармана и, взглянув на них, помчался дальше, Алиса вскочила на ноги. Ее тут осенило: ведь никогда раньше она не видела кролика с часами, да еще с жилетным карманом в придачу! Сгорая от любопытства, она побежала за ним по полю и только-только успела заметить, что он юркнул в нору под изгородью. В тот же миг Алиса юркнула за ним следом, не думая о том, как же она будет выбираться обратно. Нора сначала шла прямо, ровная, как туннель, а потом вдруг круто обрывалась вниз. Не успела Алиса и глазом моргнуть, как она начала падать, словно в глубокий колодец. То ли колодец был очень глубок, то ли падала она очень медленно, только времени у нее было достаточно, чтобы прийти в себя и подумать, что же будет дальше. Сначала она попыталась разглядеть, что ждет ее внизу, но там было темно, и она ничего не увидела. Тогда она принялась смотреть по сторонам. Стены колодца были уставлены шкафами и книжными полками; кое-где висели на гвоздиках картины и карты. Пролетая мимо одной из полок, она прихватила с нее банку с вареньем. На банке было написано «АПЕЛЬСИНОВОЕ», но увы! она оказалась пустой. Алиса побоялась бросить банку вниз - как бы не убить кого-нибудь! На лету она умудрилась засунуть ее в какой-то шкаф.`,
  },
  { chunk_order: 1, chunk_size_secs: 100, id: 2, transcription: 'Текст второй части.' },
  { chunk_order: 2, chunk_size_secs: 0, id: 3, transcription: null },
];

const chunksB = [
  { chunk_order: 0, chunk_size_secs: 60, id: 5, transcription: 'Чанк 1.' },
  { chunk_order: 1, chunk_size_secs: 60, id: 6, transcription: 'Чанк 2' },
];

describe('4️⃣ История транскрипций + просмотр чанков', () => {
  let uid;
  let tasks = [];

  const interceptList = (alias = 'list') => {
    cy.intercept('GET', `${apiUrl}/transcriptions?page=1&size=100`, {
      statusCode: 200,
      body: {
        page: 1, pages: 1, size: 100, total: tasks.length,
        transcriptions: tasks,
      },
    }).as(alias);
  };

  before(() => {
    cy.registerAndPrepareUser(username, password).then(id => {
      uid = id;
    });
  });

  it('🧪 Проверка истории транскрипций и чанков', function () {
    cy.then(() => {
      tasks = [
        {
          id: taskA,
          creator_id: uid,
          audio_len_secs: 1200,
          chunk_size_secs: 900,
          current_state: 'completed',
          create_date: isoEarlier,
          update_date: isoEarlier,
          description: fileA,
        },
        {
          id: taskB,
          creator_id: uid,
          audio_len_secs: 120,
          chunk_size_secs: 900,
          current_state: 'completed',
          create_date: isoNow,
          update_date: isoNow,
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
