import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_CODE
from loader import load_products, get_categories, get_by_category
from analytics import log_start, get_stats

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- PRODUCTS CACHE ----------
products = None


def get_products():
    global products

    if products is None:
        products = load_products()

    return products


# ---------- CATEGORY MENU ----------
async def show_categories(target):
    data = get_products()
    categories = get_categories(data)

    kb = InlineKeyboardBuilder()

    for c in categories:
        kb.button(
            text=f"✨ {c}",
            callback_data=f"cat:{c}"
        )

    kb.adjust(2)

    text = (
        "💖 Выберите категорию товаров\n\n"
        "Только популярные бьюти-находки ✨"
    )

    await target.answer(
        text,
        reply_markup=kb.as_markup()
    )


# ---------- START ----------
@dp.message(F.text == "/start")
async def start(message: Message):
    log_start(message.from_user.id)

    await show_categories(message)


# ---------- CATEGORIES COMMAND ----------
@dp.message(F.text == "/categories")
async def categories_command(message: Message):
    await show_categories(message)


# ---------- BACK TO CATEGORIES ----------
@dp.callback_query(F.data == "back_categories")
async def back_categories(call: CallbackQuery):
    await call.message.delete()

    data = get_products()
    categories = get_categories(data)

    kb = InlineKeyboardBuilder()

    for c in categories:
        kb.button(
            text=f"✨ {c}",
            callback_data=f"cat:{c}"
        )

    kb.adjust(2)

    await call.message.answer(
        "💖 Выберите категорию:",
        reply_markup=kb.as_markup()
    )


# ---------- CATEGORY ----------
@dp.callback_query(F.data.startswith("cat:"))
async def category(call: CallbackQuery):
    category_name = call.data.split(":")[1]

    data = get_products()
    items = get_by_category(data, category_name)

    kb = InlineKeyboardBuilder()

    for i, p in enumerate(items[:10]):

        name = p["name"]

        # сокращение длинных названий
        if len(name) > 35:
            name = name[:35] + "..."

        kb.button(
            text=f"🛍 {name}",
            callback_data=f"prod:{category_name}:{i}"
        )

    kb.button(
        text="⬅️ Назад к категориям",
        callback_data="back_categories"
    )

    kb.adjust(1)

    await call.message.delete()

    await call.message.answer(
        f"✨ Категория: {category_name}\n\nВыберите товар 👇",
        reply_markup=kb.as_markup()
    )


# ---------- PRODUCT ----------
@dp.callback_query(F.data.startswith("prod:"))
async def product(call: CallbackQuery):
    _, category_name, index = call.data.split(":")
    index = int(index)

    data = get_products()
    items = get_by_category(data, category_name)

    if index >= len(items):
        await call.answer("Товар не найден")
        return

    p = items[index]

    text = (
        f"💖 {p['name']}\n\n"
        f"{p['description']}\n\n"
        f"💰 Цена: {p['price']}₽\n\n"
        f"🔗 {p['url']}"
    )

    kb = InlineKeyboardBuilder()

    kb.button(
        text="⬅️ Назад",
        callback_data=f"cat:{category_name}"
    )

    kb.button(
        text="🏠 Категории",
        callback_data="back_categories"
    )

    kb.adjust(1)

    await call.message.delete()

    await call.message.answer_photo(
        photo=p["picture"],
        caption=text,
        reply_markup=kb.as_markup()
    )


# ---------- ANALYTICS ----------
@dp.message(F.text.startswith("/analytics"))
async def analytics(message: Message):
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Введите код доступа")
        return

    code = parts[1]

    if code != ADMIN_CODE:
        await message.answer("⛔ Доступ запрещён")
        return

    stats = get_stats()

    await message.answer(
        f"""
📊 АНАЛИТИКА

👤 Пользователей:
{stats['users']}

🛒 Переходов:
{stats['buy_clicks']}
"""
    )


# ---------- RUN ----------
async def main():
    print("BOT STARTED")

    await dp.start_polling(
        bot,
        skip_updates=True
    )