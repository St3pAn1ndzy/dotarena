# DOTARENA — Agent Instructions

## О проекте
Telegram Mini App — карманный справочник по Dota 2 + баттлы 1v1 между друзьями.
FastAPI + React + PostgreSQL + Redis.

Документация: `docs/CONCEPT.md` — концепт, `docs/ARCHITECTURE.md` — технические решения, `docs/OPEN_QUESTIONS.md` — TODO.

## Стек
- Бэкенд: Python 3.14, FastAPI, SQLAlchemy 2.0 (async), aiogram 3, ARQ 0.28
- Фронтенд: React + TypeScript + Vite, @telegram-apps/sdk-react
- БД: PostgreSQL + Redis
- Инфраструктура: Docker Compose, Nginx

## Структура репозитория
```
dotarena/
├── backend/          # Python-бэкенд (FastAPI + aiogram)
│   ├── app/
│   │   ├── api/      # FastAPI-роутеры (тонкие, без бизнес-логики)
│   │   ├── bot/      # Aiogram: /start, пуши, открытие Mini App
│   │   ├── services/ # Бизнес-логика (баттлы, подсчёт побед)
│   │   ├── integrations/ # OpenDota-клиент (aiohttp)
│   │   ├── models/   # SQLAlchemy-модели
│   │   ├── schemas/  # Pydantic-схемы (запросы/ответы API)
│   │   ├── tasks/    # ARQ-задачи (poll_battle, finish_expired)
│   │   └── core/     # Конфиг, зависимости, безопасность (HMAC, initData)
│   ├── migrations/   # Alembic
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/         # React-фронтенд
│   ├── src/
│   │   ├── app/      # Провайдеры, роутер (react-router-dom)
│   │   ├── pages/    # HomePage, ProfilePage, BattlePage
│   │   ├── features/ # profile/, battle/ (components, hooks, api)
│   │   └── shared/   # ui/, lib/, api/, telegram/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── nginx/            # nginx.conf для dev и prod
├── docs/             # CONCEPT.md, ARCHITECTURE.md, OPEN_QUESTIONS.md, README.md
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

## Ключевые архитектурные решения
- **Счётчики не денормализованы.** Считаются через `COUNT(*)` из `battle_match_events`. Добавить денормализацию — только когда станет узким местом.
- **game_mode_filter** — константа в Python: `VALID_GAME_MODES = {1, 22}` (All Pick, Ranked All Pick). Не хранить в БД.
- **4 статуса баттла:** `pending → active → finished` / `pending → cancelled`. Ничья = `finished` + NULL `winner_id`. Истекшее приглашение = `cancelled`.
- **On-demand опрос OpenDota:** при открытии экрана баттла (если прошло > 10 мин с `last_polled_at`) + кнопка «Обновить» + фоновый fallback каждые 45 мин (ARQ).
- **Серверный троттлинг** для кнопки «Обновить» — проверять `last_polled_at` на бэкенде, не на клиенте.
- **Lock для polling:** `redis.setnx(f"polling:{battle_id}", "1", ex=60)` — второй одновременный запрос пропускается.
- **Совместные матчи:** если оба участника баттла в одной команде (`players[].account_id`) — матч не засчитывается ни одному.
- **Бот и API — два Docker-сервиса**, но shared код лежит в `app/`. В разработке можно запускать вместе через `asyncio.gather`.
- **Защита от двойного счёта:** `UNIQUE(battle_id, match_id)` + `ON CONFLICT DO NOTHING` в `battle_match_events`.
- **Окно баттла — 48 часов** от момента принятия приглашения (`starts_at`).
- **Приглашение через invite_token** — случайная строка, нельзя перебрать.
- **Валидация initData** на каждом запросе (HMAC-SHA256). Без этого — подделка `telegram_id`.

## Запреты (не предлагать)
- Celery (ARQ уже работает на Python 3.14, план Б — кастомный asyncio-планировщик)
- Микросервисы (один разработчик, монолит с чёткими слоями)
- Kubernetes
- Redux, Zustand, Next.js, SSR
- Tailwind CSS (на старте — CSS-модули)
- UI-библиотеки (MUI, Ant Design)
- GraphQL
- Node.js для отдачи фронта (фронт — статика, отдаётся Nginx)
- Слой `repositories/` и абстрактный `StatsProvider` заранее — только когда появятся реальные потребности

## Правила для агента
- Отвечать на русском. Код-стайл: Python — black, TypeScript — prettier (2 пробела).
- При изменениях схемы БД — создавать миграцию Alembic, не редактировать существующие миграции.
- Все временные метки — UTC (TIMESTAMPTZ).
- Перед архитектурными изменениями — сверяться с `docs/ARCHITECTURE.md`.
- При работе с OpenDota:
  - Лимиты: 2000 запросов/день, 60/мин (без ключа)
  - game_mode может быть NULL (отменённые матчи)
  - Steam ID нормализовывать в 32-битный `account_id` (account_id = steamid64 - 76561197960265728)
  - Параметр `project` в запросе матчей: `?project=players` чтобы получить полную информацию об игроках
  - При вставке `battle_match_events` — `INSERT ... ON CONFLICT DO NOTHING RETURNING id`, обработать случай когда конфликт (пустой результат)

## Ход разработки (сейчас)
- Этап 1 (Прототип): настроить Vite + TMA-шаблон, один экран с фейковыми данными
- Активные файлы: `frontend/`, `docs/`
- Следующий шаг: создать фронтенд-проект через create-vite с TMA-шаблоном