# ADR-001: Python/Django + React/TypeScript

Статус: принято для стартового шаблона, 2026-11-20.

Контекст: один автор, расчётный прототип, фиксированные данные, будущие AI-эксперименты. Важнее повторяемость и короткий цикл изменений, чем высокая пропускная способность. Переносится подход к разработке, а не код другого сервиса.

Проверены публичные варианты:

| Вариант | Что полезно | Решение |
| --- | --- | --- |
| [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) | Python, React, PostgreSQL, Docker, CI | Хорошая альтернатива для API-first команды. Не копируем целиком: серверные сессии и миграции проще взять из Django. |
| [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django) | Зрелая структура Django-проектов, практики эксплуатации | Используем подход к настройкам/тестам, но не генерацию всего SaaS/email/cloud набора. |
| [go-clean-template](https://github.com/evrone/go-clean-template) | Чёткие границы архитектуры Go-сервиса | Подходит Go-команде. Для текущего расчётного/AI проекта второй язык для экспериментов не даёт явного выигрыша. |

Выбор: Django [5.2 LTS](https://docs.djangoproject.com/en/5.2/releases/5.2/) + Django Ninja для типизированных схем/OpenAPI, PostgreSQL, React/TypeScript/Vite. Django даёт auth, серверные сессии, CSRF, ORM и миграции; [официальное описание защиты](https://docs.djangoproject.com/en/5.2/topics/security/). UI — семантические native-компоненты и небольшой общий CSS, без привязки к закрытому design system. [React описывает Vite как один из вариантов SPA toolchain](https://react.dev/learn/build-a-react-app-from-scratch).

Последствия: нет SSR/SEO-инфраструктуры и глобального state framework. Для личного кабинета это достаточно; публичный маркетинговый сайт можно добавить отдельно. Python-ядро использует Decimal и не требует LLM-библиотек. Возможная смена UI не затронет математическое ядро.

Это самостоятельный scaffold, а не форк сравниваемых проектов. Лицензирование собственного приложения остаётся за владельцем. Версии зависимостей воспроизводятся lock-файлами; обновление patch-версий проходит CI.
