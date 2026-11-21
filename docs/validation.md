# Проверка стартового шаблона

Дата: 2026-11-20. Локально macOS/arm64; проверки выполнены, а не только описаны в CI.

| Проверка | Результат |
| --- | --- |
| `make check` | Пройден: Ruff, формат, mypy чистого ядра, Django checks, отсутствие новых миграций, pytest, Prettier, ESLint, Vitest, TS/build, API drift и переносимость |
| Backend / SQLite | 48 тестов; покрытие приложения 94,64%, domain/capital 100%; порог CI 85% |
| Backend / PostgreSQL 17 | Те же 48 тестов на отдельной одноразовой БД, пройдены |
| Frontend unit | 3 теста: точная передача денежных строк, сохранение формы при отказе, CSRF/cookies и отсутствие автоматического повтора записи |
| Browser / PostgreSQL | Вход → сохранить → подтвердить → reload → выход; пройден |
| Полный Docker Compose | БД healthy, migration job exit 0, API/web healthy; локально Python 3.12.16 в образе, Django 5.2.19 |
| Browser через Nginx + Compose | Пройден тот же сценарий; CSP присутствует; нет ошибок JS и горизонтального overflow на 390px; desktop 1280px |
| Визуальный просмотр | Проверены desktop/mobile скриншоты, см. ниже |
| npm audit | Известных уязвимостей не найдено на дату проверки |
| Python runtime / pip-audit 2.10.1 | Известных уязвимостей не найдено на дату проверки |
| Публичные зависимости / секреты | Portability guard и staged diff check пройдены; .env, CA bundle, окружения, test traces и БД не входят в поставку |
| Build-only CA | Для локальной сети использован optional build secret; отсутствие `/run/secrets/build_ca` в обоих runtime-контейнерах проверено |
| Production `check --deploy` | Только ожидаемые W005/W021: HSTS includeSubDomains и preload выключены до выбора и контроля всего домена; предупреждения не подавлены |

[Desktop](assets/desktop.png) · [Mobile](assets/mobile.png). На изображениях только синтетическая цель отдельного тестового аккаунта.

GitHub Actions подготовлен, но не запускался на удалённом хостинге: remote не создан. Production-развёртывание, защищённая основная ветка, DNS/TLS, внешняя идентификация и продуктовые FR из backlog не считаются выполненными. Инструкция настройки находится в `repository-setup.md` и `operations.md`.

Не заявляется полное типовое покрытие Django ORM-кода: mypy strict применяется к чистому ядру, API проверяется Pydantic, тестами и генерацией TypeScript. Финансовые функции — эталонные части FR-2, не готовый алгоритм рекомендаций. Ни одна проверка не подтверждает рыночную доходность или продуктовые метрики.
