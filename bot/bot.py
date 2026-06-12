"""
CoffeeShop Telegram Bot
Технологии: Python 3.10+, aiogram 3.x, FSM
Запуск: python bot.py
"""

import asyncio
import logging
import os
import aiohttp
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL   = os.getenv("API_URL", "https://your-project.vercel.app")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())


# ── Каталог ─────────────────────────────────────────────────────────────────
MENU = {
    "Эспрессо":       ["Эспрессо — 600 ₸", "Доппио — 800 ₸", "Американо — 700 ₸"],
    "Капучино":       ["Капучино — 900 ₸", "Капучино большой — 1100 ₸"],
    "Латте":          ["Латте — 950 ₸", "Латте шоколадный — 1050 ₸", "Матча латте — 1100 ₸"],
    "Раф":            ["Раф классический — 1100 ₸", "Раф медовый — 1200 ₸"],
    "Холодный кофе":  ["Айс латте — 1000 ₸", "Колд брю — 1100 ₸", "Кофе тоник — 1150 ₸"],
}

def parse_product(item_str: str) -> tuple[str, int]:
    """'Латте — 950 ₸' → ('Латте', 950)"""
    parts = item_str.split("—")
    name  = parts[0].strip()
    price = int("".join(filter(str.isdigit, parts[1]))) if len(parts) > 1 else 0
    return name, price


# ── FSM States ───────────────────────────────────────────────────────────────
class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_product  = State()
    entering_name     = State()
    entering_phone    = State()
    confirming        = State()


# ── Keyboards ────────────────────────────────────────────────────────────────
def categories_kb() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=cat, callback_data=f"cat:{cat}")]
               for cat in MENU]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def products_kb(category: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=item, callback_data=f"product:{item}")]
        for item in MENU[category]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back:categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Отмена",      callback_data="cancel"),
    ]])


# ── Handlers ─────────────────────────────────────────────────────────────────
@dp.message(F.text.in_({"/start", "/menu"}))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "☕ Добро пожаловать в <b>CoffeeShop</b>!\n\nВыберите категорию:",
        parse_mode="HTML",
        reply_markup=categories_kb()
    )
    await state.set_state(OrderStates.choosing_category)


@dp.callback_query(F.data.startswith("cat:"))
async def choose_category(cb: CallbackQuery, state: FSMContext):
    category = cb.data.split(":", 1)[1]
    await state.update_data(category=category)
    await cb.message.edit_text(
        f"Категория: <b>{category}</b>\nВыберите напиток:",
        parse_mode="HTML",
        reply_markup=products_kb(category)
    )
    await state.set_state(OrderStates.choosing_product)
    await cb.answer()


@dp.callback_query(F.data == "back:categories")
async def back_to_categories(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        "Выберите категорию:",
        reply_markup=categories_kb()
    )
    await state.set_state(OrderStates.choosing_category)
    await cb.answer()


@dp.callback_query(F.data.startswith("product:"))
async def choose_product(cb: CallbackQuery, state: FSMContext):
    item_str = cb.data.split(":", 1)[1]
    name, price = parse_product(item_str)
    await state.update_data(product_name=name, price=price)
    await cb.message.edit_text(
        f"Отлично! Вы выбрали <b>{name}</b>.\n\nВведите ваше имя:",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.entering_name)
    await cb.answer()


@dp.message(OrderStates.entering_name)
async def enter_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Имя слишком короткое. Попробуйте ещё раз:")
        return
    await state.update_data(customer_name=name)
    await message.answer(f"Отлично, {name}! Теперь введите ваш номер телефона:")
    await state.set_state(OrderStates.entering_phone)


@dp.message(OrderStates.entering_phone)
async def enter_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 10:
        await message.answer("Некорректный номер. Пример: +7 777 123 45 67")
        return

    await state.update_data(phone=phone)
    data = await state.get_data()

    summary = (
        f"📋 <b>Подтвердите заказ:</b>\n\n"
        f"☕ Напиток: <b>{data['product_name']}</b>\n"
        f"💰 Цена: <b>{data['price']} ₸</b>\n"
        f"👤 Имя: <b>{data['customer_name']}</b>\n"
        f"📱 Телефон: <b>{phone}</b>\n"
    )
    await message.answer(summary, parse_mode="HTML", reply_markup=confirm_kb())
    await state.set_state(OrderStates.confirming)


@dp.callback_query(F.data == "confirm")
async def confirm_order(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await cb.message.edit_reply_markup(reply_markup=None)

    payload = {
        "customer_name": data["customer_name"],
        "phone":         data["phone"],
        "product_name":  data["product_name"],
        "category":      data["category"],
        "price":         data["price"],
        "size":          "medium",
        "quantity":      1,
        "delivery_type": "pickup",
        "source":        "telegram",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/orders",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                result = await resp.json()
                if resp.status == 201 and result.get("success"):
                    await cb.message.answer(
                        "✅ <b>Заказ принят!</b>\n\n"
                        "Мы свяжемся с вами в ближайшее время.\n"
                        "Чтобы сделать новый заказ — /menu",
                        parse_mode="HTML"
                    )
                else:
                    raise ValueError(result.get("error", "Неизвестная ошибка"))
    except Exception as e:
        logging.error(f"Order error: {e}")
        await cb.message.answer(
            f"❌ Ошибка при отправке заказа: {e}\n\nПопробуйте позже или позвоните нам."
        )

    await state.clear()
    await cb.answer()


@dp.callback_query(F.data == "cancel")
async def cancel_order(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ Заказ отменён. Чтобы начать заново — /menu")
    await cb.answer()


@dp.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>CoffeeShop Bot</b>\n\n"
        "/start или /menu — сделать заказ\n"
        "/help — помощь",
        parse_mode="HTML"
    )


# ── Main ─────────────────────────────────────────────────────────────────────
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
