# Разработка локально

## Инструменты

Python 3.12, Node 24 LTS, uv 0.13.9, Docker Compose v2, make. Установить из публичных официальных источников. `make install` читает зафиксированные lock-файлы. Не отключать TLS verification; если локальная сеть использует дополнительный CA, добавьте его в доверенное хранилище только на своей машине, не в приложение.

## Hot reload

Проще всего для первого старта `make up`. Для редактирования API/UI вне контейнеров:

1. `make init-env` (один раз), `make install`.
2. Поднимите отдельный локальный PostgreSQL с отдельными кредами и loopback-портом либо создайте compose override, публикующий порт БД только на 127.0.0.1. В базовом Compose порт специально не опубликован.
3. Передайте переменные из `.env` в процесс средствами IDE/dotenv runner. Поменяйте **только в локальном процессе** `POSTGRES_HOST=127.0.0.1`, порт согласно вашему PostgreSQL, `APP_ENV=local`, `CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173`. Не коммитьте локальный override с секретами.
4. `cd backend && uv run python manage.py migrate && uv run python manage.py runserver 127.0.0.1:8000`.
5. В другом терминале `cd frontend && npm run dev`. Откройте http://127.0.0.1:5173. Vite проксирует /api на локальный backend; сессия same-origin сохраняется.
6. Создать пользователя: `cd backend && uv run python manage.py createsuperuser` с теми же переменными окружения.

Настройки не загружают `.env` неявно: Docker Compose передаёт её явно, IDE должна делать то же. Не использовать окружение рабочей БД для pytest.

## Перед коммитом

`make check` — быстрые SQLite API-тесты, чистая математика, формат, lint, строгие TS-типы, mypy ядра, сборка, проверка миграций и API. `TEST_POSTGRES=1 ... make backend-check` проверяет реальный PostgreSQL. CI всегда использует PostgreSQL; SQLite — только быстрый локальный режим тестов.

Изменили Schema → `make contract` → проверить diff JSON и generated d.ts. Изменили модель → `uv run --directory backend python manage.py makemigrations` с настроенным окружением → проверить миграцию на копии/тестовой БД.

`make e2e` запускается против уже поднятого стенда. Переменные `E2E_USERNAME` и `E2E_PASSWORD` задайте через секреты локального процесса, не в команде, попадающей в shell history. При использовании уже установленного Chromium можно задать `E2E_CHROMIUM_PATH` абсолютным путём только в локальном окружении; CI использует загруженный Playwright Chromium. Скриншоты/trace могут содержать данные тестового аккаунта; в Git они исключены.

## Если сеть использует дополнительный доверенный CA

Не выключать TLS и не добавлять сертификат в Git или runtime image. Укажите абсолютный путь к доверенному PEM bundle (обычные корневые сертификаты + дополнительный CA) через `BUILD_CA_FILE`, затем:

```sh
docker compose -f compose.yaml -f compose.build-ca.yaml build
docker compose up --wait
```

BuildKit монтирует bundle как временный secret только в шаг установки зависимостей. Без overlay используется обычное публичное хранилище CA. Доверять можно только проверенному локальному bundle; сертификат в шаблон/архив не входит.

Новые версии Buildx могут потребовать разрешение чтения файла CA вне build context. Не расширяйте разрешение на весь диск. Используйте выведенный Buildx точный путь:

```sh
docker compose -f compose.yaml -f compose.build-ca.yaml build --print > /tmp/pension-bake.json
docker buildx bake --file /tmp/pension-bake.json --allow="fs.read=$BUILD_CA_FILE" --load
docker compose up --wait
```

`BUILD_CA_FILE` должен содержать канонический абсолютный путь, без symlink-алиаса. Build configuration из `/tmp` не коммитить.
