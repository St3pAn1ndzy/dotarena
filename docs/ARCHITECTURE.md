# DOTARENA — Архитектура и технические решения

**Версия:** 0.4  
**Последнее обновление:** 22.11.26

---

## 1. Общая архитектура

```
Пользователь → Telegram → Mini App (React) → FastAPI → OpenDota API
                                      ↕
                               PostgreSQL / Redis
                                      ↕
                             Bot (aiogram) → Push
```

Два процесса в одном репозитории, общаются через общую БД и Redis:

- **Telegram Bot** (aiogram 3) — /start, открытие Mini App, пуш-уведомления.
- **Backend API** (FastAPI) — запросы из Mini App, OpenDota, подсчёт баттлов.
- **Frontend** (React + TypeScript) — статика, отдаётся через Nginx.

---

## 2. Стек

| Слой | Технология | Зачем |
|------|------------|-------|
| Бот | aiogram 3 | Async, роутеры, нативная TMA-интеграция |
| API | FastAPI | Async, Pydantic, автодокументация |
| ORM | SQLAlchemy 2.0 (async) | Уже знаком |
| База данных | PostgreSQL | Основное хранилище |
| Кэш | Redis | Кэш OpenDota, состояние баттлов |
| Фоновые задачи | ARQ 0.28 (проверен на Python 3.14) | Async-native, Redis-only |
| OpenDota клиент | Кастомный на aiohttp | Полный контроль, rate limit |
| Frontend | React + TypeScript + Vite | Официальный TMA-шаблон |
| TMA SDK | @telegram-apps/sdk-react | Тема, BackButton, initData |
| Валидация initData | Кастомная HMAC-проверка | Безопасность |
| Деплой | Docker Compose на VPS | |
| Reverse proxy | Nginx | SSL, статика, прокси |
| HTTPS для тестов | Ngrok / Cloudflare Tunnel | Бесплатно, без домена |

---

## 3. Структура репозитория

```
dotarena/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI-роутеры (тонкие, только HTTP)
│   │   ├── bot/              # aiogram-роутеры, handlers, keyboards
│   │   ├── services/         # Бизнес-логика (баттлы, подсчёт)
│   │   ├── integrations/     # OpenDota-клиент, Telegram API
│   │   ├── models/           # SQLAlchemy-модели
│   │   ├── schemas/          # Pydantic-схемы (запросы/ответы)
│   │   ├── tasks/            # ARQ-задачи (опрос, пуши)
│   │   └── core/             # Конфиг, зависимости, безопасность
│   ├── migrations/           # Alembic
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── nginx/
├── .env.example
├── Makefile
└── README.md
```

### Ключевое правило слоёв

Роутеры не содержат бизнес-логики. Сервис не знает про HTTP. Репозиторий не знает про бизнес-правила.

**Важно:** не создавай слой `repositories/` заранее. Если в сервисе меньше 3 прямых запросов к одной таблице — пиши SQLAlchemy-запросы прямо в сервисе. Репозиторий появляется, когда запросов становится больше.

### Запуск в разработке

```bash
# Терминал 1: БД
docker-compose up -d db redis

# Терминал 2: API
cd backend && uvicorn app.api.main:app --reload

# Терминал 3: Фронт
cd frontend && npm run dev
```

В Docker Compose — два сервиса API и Bot (разные процессы). Для разработки можно запускать всё вместе через `asyncio.gather` в `backend/main.py`, но в продакшне они разделены.

---

## 4. Схема базы данных

### 4.1 Обзор

4 таблицы:

```
users
  └── battles
        └── battle_match_events
```

**Принцип:** все сырые данные матчей — в `battle_match_events`. Счётчики не денормализованы, считаются через `COUNT(*)`. Денормализация — только когда COUNT(*) станет узким местом (тысячи баттлов).

### 4.2 Таблица users

```sql
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    steam_account_id INTEGER UNIQUE,
    bot_started_at  TIMESTAMPTZ,   -- NULL → пуш не доставить
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Индексы:** `telegram_id` (UNIQUE), `steam_account_id` (UNIQUE).

- Steam ID нормализуется на входе: все форматы (SteamID64, URL, account_id) → 32-битный `account_id`.
- Имя пользователя не хранится — вытаскивается из initData при каждом запросе.

### 4.3 Таблица battles

```sql
CREATE TABLE battles (
    id                BIGSERIAL PRIMARY KEY,
    creator_id        BIGINT NOT NULL REFERENCES users(id),
    opponent_id       BIGINT REFERENCES users(id),    -- NULL пока pending
    status            VARCHAR(16) NOT NULL DEFAULT 'pending',
                      -- pending / active / finished / cancelled
    metric            VARCHAR(16) NOT NULL DEFAULT 'wins',
    duration_hours    SMALLINT NOT NULL DEFAULT 48,
    invite_token      VARCHAR(64) UNIQUE NOT NULL,
    starts_at         TIMESTAMPTZ,
    ends_at           TIMESTAMPTZ,   -- starts_at + duration_hours
    winner_id         BIGINT REFERENCES users(id),     -- NULL = ничья
    invite_expires_at TIMESTAMPTZ NOT NULL,             -- created_at + 24ч
    last_polled_at    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Индексы:** `(creator_id, opponent_id)`, `(status, ends_at)`, `(status, last_polled_at)`, `invite_token` (UNIQUE).

**Жизненный цикл:**
```
pending → (оппонент принял) → active → (ends_at) → finished
pending → (отменён / истекло приглашение) → cancelled
```

- `draw` = `finished` + NULL winner_id
- `expired` = `cancelled` (нет отдельного статуса)
- Нет денормализованных счётчиков (creator_wins / opponent_wins)
- `game_mode_filter` — константа в коде, не в БД

### 4.4 Таблица battle_match_events

```sql
CREATE TABLE battle_match_events (
    id                BIGSERIAL PRIMARY KEY,
    battle_id         BIGINT NOT NULL REFERENCES battles(id),
    user_id           BIGINT NOT NULL REFERENCES users(id),
    match_id          BIGINT NOT NULL,
    is_win            BOOLEAN NOT NULL,
    match_started_at  TIMESTAMPTZ NOT NULL,
    counted_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(battle_id, match_id)
);
```

**Индексы:** `(battle_id, user_id)`, `match_id`.

- `UNIQUE(battle_id, match_id)` — защита от двойного счёта.
- `ON CONFLICT DO NOTHING` при вставке.

**Подсчёт счётчика:**
```sql
SELECT COUNT(*) FROM battle_match_events
WHERE battle_id = X AND user_id = Y AND is_win = true;
```

### 4.5 Удалены из MVP (по сравнению с v0.3)

- **challenges / challenge_match_events** — перенесены в после-валидацию. Не проверяют основную гипотезу (социальные соревнования).
- **push_log** — заменён на `logging.warning()` при неудачной отправке.

---

## 5. Фоновые задачи (ARQ)

### 5.1 Задачи

1. **`poll_battle(battle_id)`** — on-demand при открытии экрана (если прошло > 10 мин с `last_polled_at`) + фоновый опрос каждые 45 мин.
    - Запрашивает матчи обоих игроков за период баттла.
    - Фильтрует по `game_mode IN (1, 22)`.
    - Проверяет, не играли ли участники в одной команде (по `players[].account_id`).
    - Вставляет в `battle_match_events` (ON CONFLICT DO NOTHING).
    - Обновляет `last_polled_at`.

2. **`send_battle_notification(battle_id, event)`** — старт, результат, напоминание. Проверяет `bot_started_at IS NOT NULL`.

3. **`finish_expired_battles()`** — cron раз в час: находит `active` баттлы с истёкшим `ends_at`, фиксирует результат, отправляет пуш.

### 5.2 Lock для on-demand опроса

Без блокировки два одновременных запроса сделают 4 вызова к OpenDota вместо 2.

```python
import aioredis

redis = await aioredis.from_url("redis://...")
locked = await redis.setnx(f"polling:{battle_id}", "1")
if locked:
    await redis.expire(f"polling:{battle_id}", 60)
    # делать опрос
else:
    # вернуть кэш
```

### 5.3 План Б (если ARK-а не будет)

Кастомный asyncio-планировщик на ~150 строк:
- Бесконечный цикл `asyncio.sleep(60)`.
- Проверяет в Redis, какие баттлы пора опрашивать (сравнивает `last_polled_at` с текущим временем).
- Запускает задачи через `asyncio.create_task`.
- Блокировка через `redis.setnx`.

---

## 6. Интеграция с OpenDota

### 6.1 Лимиты

- Без ключа: 2 000 запросов/день, 60/мин.
- On-demand подход: при 200 пользователях и 3 открытиях в день → ~400 запросов/день (20% лимита).

### 6.2 Слой абстракции

На старте — только OpenDotaClient. Никакого протокола/интерфейса. Абстракция выделяется, когда появляется вторая имплементация (STRATZ).

```python
class OpenDotaClient:
    async def get_player_profile(self, steam_id: int) -> dict: ...
    async def get_player_matches(self, steam_id: int, **params) -> list[dict]: ...
```

**Важно:** game_mode в ответе API может быть null (для отменённых матчей). Проверь на реальных данных до написания логики.

### 6.3 Фильтрация матчей

```python
VALID_GAME_MODES = {1, 22}  # All Pick, Ranked All Pick
```

Константа в коде, не в БД. Фильтр — бизнес-правило, его изменение требует тестирования.

### 6.4 Кэширование

| Тип данных | TTL |
|------------|-----|
| Профиль игрока | 5–15 минут |
| Список матчей | 10 минут (on-demand) / 45 мин (фоновый) |

Кэш — только Redis. Postgres не используется для кэша.

---

## 7. Telegram-интеграция

### 7.1 Валидация initData

На каждом запросе из Mini App. Без этого можно подделать `telegram_id`.

```python
import hashlib, hmac

def validate_init_data(init_data: str, bot_token: str) -> bool:
    # Разобрать строку, проверить hash через HMAC-SHA256
    # Подробно: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
```

### 7.2 /start для пушей

Пользователь должен нажать `/start` у бота до того, как бот сможет отправить пуш. В `users.bot_started_at` — NULL, если не нажал.

**UX:** при входе — экран «Нажми /start у бота, иначе уведомления не придут».

---

## 8. Фронтенд-архитектура

### 8.1 Принципы

1. **Тонкий клиент.** Фронт не считает, не фильтрует, не решает. Только рендерит.
2. **Feature-based структура.** Код по фичам.
3. **Минимум глобального состояния.** `useState` + React Context. Никакого Redux/Zustand.

### 8.2 Структура

```
src/
├── app/                  # Провайдеры, роутер
├── pages/                # Страницы
│   ├── HomePage/
│   ├── ProfilePage/
│   └── BattlePage/
├── features/             # Фичи
│   ├── profile/
│   └── battle/
├── shared/               # Общее
│   ├── ui/               # Button, Card, Spinner
│   ├── lib/              # Форматирование
│   ├── api/              # HTTP-клиент
│   └── telegram/         # Обёртки SDK
└── main.tsx
```

### 8.3 Роутинг

- `react-router-dom` + `@telegram-apps/react-router-integration`
- Маршруты: `/` (главная), `/profile/:steamId`, `/battle/:id`
- BackButton: показывать на всех экранах, кроме главного

### 8.4 Telegram-специфика

- **MainButton** — основное действие на экране. Не дублировать обычной кнопкой.
- **Тема** — CSS-переменные из `themeParams.bindCssVars()`. Без ручного переключения.
- **Скелетоны** — на каждый экран с данными. Не спиннеры.

### 8.5 Что не используем

- Redux / Zustand — избыточно для MVP
- Next.js / SSR — не даёт выгоды в TMA
- UI-библиотеки (MUI, Ant Design) — тяжелые
- Tailwind — не запрещён, но лучше CSS-модули на старте

---

## 9. Деплой

### 9.1 Схема

```yaml
# docker-compose.yml
services:
  api:      # FastAPI
  bot:      # aiogram
  db:       # PostgreSQL
  redis:    # Redis
  nginx:    # статика + прокси
```

### 9.2 HTTPS

- Telegram требует HTTPS.
- На этапах 1–3: Ngrok (бесплатно, временный URL) или Cloudflare Tunnel (постоянный, бесплатно).
- Для продакшна: домен + Let's Encrypt.

### 9.3 Nginx config (prod)

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    root /var/www/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://api:8000/;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 10. Ключевые архитектурные решения (с обоснованием)

| Решение | Почему |
|---------|--------|
| Нет денормализованных счётчиков | Для MVP COUNT(*) быстрее, чем возиться с рассинхроном. Денормализация — потом. |
| game_mode_filter в коде | Фильтр — бизнес-правило. Менять без деплоя — опасно. |
| Названия статусов: 4, а не 6 | Меньше ветвлений, проще отладка. Draw = finished + NULL. Expired = cancelled. |
| Нет слоя repositories заранее | Избыточно для 3-х запросов к БД. Появляется, когда нужно. |
| Нет абстрактного StatsProvider | Пока одна имплементация — интерфейс не нужен. |
| Бот и API — разные Docker-сервисы | Не мешают друг другу, можно перезапускать отдельно. В dev — вместе для простоты. |
| On-demand опрос | Пользователь получает актуальные данные, когда они нужны. Лимиты API не страдают. |
| Серверный троттлинг | Клиентский троттлинг легко обходится. |
| Two-phase insert (INSERT + проверка) | ON CONFLICT DO NOTHING + RETURNING может вернуть пустой результат. |

---

## 11. Что сознательно НЕ используем

| Технология | Почему |
|------------|--------|
| Celery | Тяжёлый, синхронный, отдельный процесс. ARQ на asyncio — легче и роднее. |
| Микросервисы | Один разработчик. Монолит с чёткими слоями. |
| GraphQL | REST достаточно. |
| Kubernetes | Для одного VPS — дичь. |
| Node.js для фронта | Фронт — статика после сборки. Отдаётся Nginx. |
| Tailwind CSS | Добавляет абстракцию на старте. CSS-модули — прозрачнее для изучения. |

---

## 12. TODO (tech debt)

- [ ] Проверить реальный ответ OpenDota `GET /players/{id}/matches` — game_mode не null?
- [ ] Уточнить условия коммерческого ключа OpenDota до этапа 7
- [ ] Настроить Ngrok / Cloudflare Tunnel до этапа 2
- [ ] Продумать стратегию миграций: одна папка `migrations/` для всего бэкенда
- [ ] Проверить ARQ на финальной версии Python в Docker-образе