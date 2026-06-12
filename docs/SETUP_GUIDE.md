# 🛠️ Пошаговая инструкция по запуску CoffeeShop

---

## ШАГ 1 — Создать таблицу в Supabase

1. Открыть браузер → перейти на **https://supabase.com**
2. Войти в аккаунт → открыть ваш проект
3. В левом меню нажать **"SQL Editor"** (иконка терминала)
4. Нажать **"New query"** (кнопка вверху)
5. Скопировать и вставить этот SQL:

```sql
CREATE TABLE orders (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_name text NOT NULL,
  phone text NOT NULL,
  product_name text NOT NULL,
  category text NOT NULL,
  price integer,
  size text DEFAULT 'medium',
  quantity integer DEFAULT 1,
  delivery_type text DEFAULT 'pickup',
  address text,
  comment text,
  status text DEFAULT 'new',
  source text DEFAULT 'web',
  created_at timestamptz DEFAULT now()
);
```

6. Нажать кнопку **"Run"** (или Ctrl+Enter)
7. Должно появиться: `Success. No rows returned`

**Проверка:** В левом меню → **"Table Editor"** → должна появиться таблица `orders`

---

## ШАГ 2 — Создать GitHub репозиторий

1. Открыть **https://github.com** → войти в аккаунт
2. Нажать зелёную кнопку **"New"** (вверху слева)
3. **Repository name:** `coffee-shop`
4. Выбрать **Public**
5. НЕ ставить галочки на README/gitignore (они уже есть)
6. Нажать **"Create repository"**

7. Открыть **Git Bash** (или терминал) в папке `coffee-shop`:
```bash
git init
git add .
git commit -m "initial: CoffeeShop MVP"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/coffee-shop.git
git push -u origin main
```

> ⚠️ **ВАЖНО:** перед `git add .` убедитесь что файл `.env` (не `.env.example`) НЕ существует.
> Файл `.gitignore` уже исключает его.

---

## ШАГ 3 — Деплой на Vercel

1. Открыть **https://vercel.com** → войти через GitHub
2. Нажать **"Add New Project"**
3. Выбрать репозиторий **coffee-shop** → нажать **"Import"**
4. На странице настроек найти раздел **"Environment Variables"**
5. Добавить по одной переменной (поле Name + Value):

| Name | Value |
|------|-------|
| `SUPABASE_URL` | `https://uwipcyoofbrdqsgsdhep.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3aXBjeW9vZmJyZHFzZ3NkaGVwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTAxOTExMywiZXhwIjoyMDk2NTk1MTEzfQ.6G2-HXX7rUAPfx2-pKY3Jt-_wL2W-u-DOoqNtYrynw8` |
| `ADMIN_TOKEN` | `coffee2024secret` (придумайте свой) |

6. Нажать **"Deploy"**
7. Дождаться деплоя (~1-2 минуты) → появится ссылка вида `coffee-shop-xxxx.vercel.app`

**Проверка:** Открыть `https://coffee-shop-xxxx.vercel.app` — должен открыться сайт.

---

## ШАГ 4 — Проверить API endpoint

Открыть браузер → перейти по адресу:
```
https://coffee-shop-xxxx.vercel.app/api/orders
```
Должен вернуться ответ: `{"success":false,"error":"Нет доступа"}`
Это значит API работает! (401 = токен не передан, это правильно)

---

## ШАГ 5 — Запустить Telegram-бот

1. Открыть папку `bot/` в терминале

2. Создать файл `.env` в папке `bot/`:
```
TELEGRAM_BOT_TOKEN=8057217473:AAEtzh_l0S72VYF4jWjsaSn7L4GXsTf25Fw
API_URL=https://coffee-shop-xxxx.vercel.app
```
> Замените `coffee-shop-xxxx.vercel.app` на вашу реальную ссылку Vercel

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Запустить бота:
```bash
python bot.py
```

5. Открыть Telegram → найти вашего бота → написать `/start`

---

## ШАГ 6 — Проверить что всё работает

1. **Сайт:** заполнить форму заказа → должно появиться "✅ Заказ принят!"
2. **Supabase:** Table Editor → orders → должна появиться строка
3. **Бот:** пройти весь сценарий → подтвердить заказ
4. **Supabase:** должна появиться вторая строка с `source = telegram`
5. **Админка:** открыть `https://coffee-shop-xxxx.vercel.app/admin` → ввести токен `coffee2024secret` → увидеть оба заказа

---

## ⚠️ БЕЗОПАСНОСТЬ — сделать СРАЗУ

Вы поделились ключами в чате — нужно их перегенерировать:

1. **Supabase** → Settings → API → нажать **"Regenerate"** рядом с service_role key
2. **Telegram** → написать @BotFather → `/mybots` → выбрать бота → **"API Token"** → **"Revoke current token"**
3. Обновить новые значения в Vercel (Settings → Environment Variables)
4. Обновить новый токен в файле `bot/.env`

---

## Что сдавать преподавателю

- **GitHub:** `https://github.com/ВАШ_ЛОГИН/coffee-shop`
- **Vercel:** `https://coffee-shop-xxxx.vercel.app`
- **README:** уже описывает что делает проект
- **Видео-демо 60-90 сек:** показать сайт → форма заказа → бот → запись в Supabase → админка
