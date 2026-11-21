# API

Все вызовы с того же origin; credentials `same-origin`. Публичный машинный контракт бизнес-API: `contracts/openapi.json`. Личные ответы `Cache-Control: no-store, private`. JSON requests <=64KiB.

## Сессия (обычные Django views)

- `GET /api/auth/session` → `200 {"user":null}` либо `{"user":{"username":"..."}}`; устанавливает/обновляет CSRF cookie.
- `POST /api/auth/login` с `{ "username": "...", "password": "..." }` и `X-CSRFToken` из cookie → 200 с user, 400 некорректный JSON/поля, 401 общий отказ, 403 CSRF, 429 ограничение попыток. При успехе session id и CSRF token ротируются Django; читать актуальную cookie перед каждым изменением.
- `POST /api/auth/logout` с `{}` и CSRF → `200 {"user":null}`; серверная сессия уничтожается.

Не хранить password/CSRF/session в localStorage. Логин требует CSRF до аутентификации. Публичной регистрации, восстановления и провайдера OIDC пока нет.

## Цели /api/v1

- `GET /goals?offset=0` → `{items:[...],has_more:false}`, не более 50. Нужна сессия.
- `POST /goals` → 201 новый черновик; `monthly_income`, `initial_capital`, `monthly_contribution` — decimal strings; basis `today|future`; payout_start — ISO первый день текущего/будущего месяца; payout_months целое 1..1200; risk_notes непустая строка <=1000. Лишние поля запрещены. Owner назначается сервером.
- `POST /goals/{uuid}/confirm` с `{"confirmed":true}` → 200, подтверждение idempotent; 404 чужая/отсутствующая цель, 409 устаревший месяц, 422 неподтверждённый/ошибочный ввод.

После подтверждения объект не редактируется. В этой версии нет DELETE/PUT/PATCH и маршрута расчёта. Повтор POST создания намеренно создаёт новый черновик: не делать автоматический retry мутаций. Для будущей автоматической интеграции понадобится сохранённый idempotency key.

Любые API-данные сессии принадлежат одному пользователю; доступ не определяется UUID или фронтендом. Перед расширением ответа обновить Schema, экспорт и frontend types.
