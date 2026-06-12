# ☕ CoffeeShop MVP

Онлайн-магазин кофе с каталогом по категориям, формой заказа, Telegram-ботом и админ-панелью.

**Vercel:** _ссылка появится после деплоя_  
**GitHub:** _ссылка появится после создания репо_

---

## Что делаю и что уже работает

- [x] Структура репозитория
- [x] Фронтенд: лендинг с категориями + форма заказа
- [x] API endpoint `POST /api/orders` + `GET /api/orders`
- [x] Страница админки `/admin`
- [x] Telegram-бот (FSM, Python)
- [ ] Supabase: создать проект и таблицы (вручную)
- [ ] Деплой на Vercel
- [ ] Добавить env переменные в Vercel

---

## Сценарии

### Web-сценарий
1. Пользователь заходит на сайт
2. Видит категории кофе: Эспрессо, Капучино, Латте, Раф, Холодный кофе
3. Выбирает напиток, кликает «Заказать»
4. Заполняет форму: имя, телефон, тип доставки (самовывоз / доставка), адрес, комментарий
5. Нажимает «Оформить заказ» → форма отправляет `POST /api/orders`
6. Получает подтверждение на экране

### Telegram-сценарий
1. Пользователь пишет боту `/start`
2. Бот показывает категории кофе (кнопки)
3. Пользователь выбирает категорию → бот показывает напитки
4. Пользователь выбирает напиток → бот спрашивает имя
5. Бот спрашивает номер телефона
6. Бот показывает итог с кнопками «Подтвердить» / «Отмена»
7. При подтверждении: `POST /api/orders` с `source=telegram`
8. Пользователь получает сообщение «Заказ принят!»

---

## Таблицы Supabase

### Таблица `orders`
```sql
CREATE TABLE orders (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_name text NOT NULL,
  phone text NOT NULL,
  product_name text NOT NULL,
  category text NOT NULL,
  size text DEFAULT 'medium',
  quantity integer DEFAULT 1,
  delivery_type text DEFAULT 'pickup',  -- 'pickup' | 'delivery'
  address text,
  comment text,
  status text DEFAULT 'new',           -- 'new' | 'processing' | 'done' | 'cancelled'
  source text DEFAULT 'web',           -- 'web' | 'telegram'
  created_at timestamptz DEFAULT now()
);
```

### SQL для вставки в Supabase SQL Editor:
```sql
-- Вставить тестовый заказ
INSERT INTO orders (customer_name, phone, product_name, category, source)
VALUES ('Тест Тестов', '+7 999 000 00 00', 'Капучино', 'Капучино', 'web');
```

---

## API Endpoints

### `POST /api/orders` — создать заказ
**Request:**
```json
{
  "customer_name": "Алибек",
  "phone": "+7 777 123 45 67",
  "product_name": "Латте",
  "category": "Латте",
  "size": "large",
  "quantity": 2,
  "delivery_type": "delivery",
  "address": "ул. Абая 10",
  "comment": "Без сахара",
  "source": "web"
}
```
**Response:** `{ "success": true, "id": "uuid" }`

---

### `GET /api/orders` — список заказов (для админки)
**Headers:** `Authorization: Bearer <ADMIN_TOKEN>`  
**Response:** `{ "orders": [...] }`

---

## ENV переменные

| Переменная | Где взять |
|---|---|
| `SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | Supabase → Settings → API → service_role key |
| `TELEGRAM_BOT_TOKEN` | @BotFather в Telegram |
| `ADMIN_TOKEN` | Придумать самому (любая строка) |
| `API_URL` | URL вашего деплоя на Vercel |

> ⚠️ Никогда не коммитить `.env` в GitHub! Только `.env.example`.

---

## План реализации (9 шагов)

**Шаг 1 — Репозиторий**
Создать GitHub repo, загрузить структуру проекта, добавить `.gitignore`.

**Шаг 2 — Supabase**
Зарегистрироваться на [supabase.com](https://supabase.com), создать проект, выполнить SQL для создания таблицы `orders`, вставить тестовую запись через Table Editor.

**Шаг 3 — API (центр записи)**
Создать `api/orders.js` — Vercel serverless endpoint. POST принимает заказ и пишет в Supabase. GET возвращает список заказов с проверкой ADMIN_TOKEN.

**Шаг 4 — Фронтенд**
`frontend/index.html` — лендинг с категориями кофе и формой заказа. При submit отправляет `fetch` на `POST /api/orders`.

**Шаг 5 — Админка**
`frontend/admin.html` — страница с таблицей заказов. Загружает данные через `GET /api/orders` с токеном.

**Шаг 6 — Telegram-бот**
`bot/bot.py` — Python + aiogram 3. FSM: выбор категории → напитка → имя → телефон → подтверждение → POST на API.

**Шаг 7 — Интеграция**
Проверить: сайт пишет в Supabase, бот пишет в Supabase, админка показывает обе записи.

**Шаг 8 — Деплой**
Push в GitHub → Import в Vercel → добавить env переменные → Deploy → проверить endpoint через браузер.

**Шаг 9 — Тестирование (QA-чеклист)**
- [ ] Сайт: пустые поля → ошибка валидации
- [ ] Сайт: валидный заказ → «Заказ принят!» + запись в Supabase
- [ ] Бот: `/start` → сценарий → подтверждение → запись в Supabase
- [ ] Админка: показывает обе записи (web + telegram)
- [ ] Безопасность: нет `.env` в репо, service key не во фронте
- [ ] Мобилка: сайт корректно отображается на 360px

---

## Структура проекта

```
coffee-shop/
├── frontend/
│   ├── index.html       ← лендинг + форма заказа
│   └── admin.html       ← админ-панель
├── api/
│   └── orders.js        ← POST /api/orders, GET /api/orders
├── bot/
│   ├── bot.py           ← Telegram-бот (Python)
│   └── requirements.txt
├── .env.example
├── .gitignore
├── vercel.json
└── README.md
```

## Поток данных

```
Пользователь (сайт)
  └──→ POST /api/orders (Vercel serverless)
         └──→ Supabase (таблица orders)
                └──→ GET /api/orders (админка)

Пользователь (Telegram)
  └──→ Bot (Python, local/server)
         └──→ POST /api/orders (Vercel serverless)
                └──→ Supabase (таблица orders)
```
