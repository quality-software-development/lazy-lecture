# Lazy Lecture Web UI

Веб-фронтенд проекта

## Запуск

Понадобится Docker.

-   В директории проекта выполнить:

    ```
    $ docker-compose up -d web-ui
    ```

-   Перейти по адресу: http://localhost:9000

## Тестирование

В директории `web-ui` выполнить нижеописанное.

-   для CI:
    ```
    $ npm run test:unit:ci
    ```
-   для просмотра прохождения тестов в UI:
    ```
    $ npm run test:unit:ui
    ```
    затем перейти по адресу: http://localhost:51204/\_\_vitest__/#/

-   для расчета покрытия кода тестами:
    ```
    $ npm run test:unit:coverage
    ```
    затем ознакомиться с расчетами в консоли либо открыть в браузере файл `web-ui/coverage/index.html`
