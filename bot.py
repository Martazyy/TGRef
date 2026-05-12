import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_CODE
from loader import load_products, get_categories, get_by_category
from analytics import log_start, log_buy_click, get_stats

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

products = load_products()


# ---------- START ----------
@dp.message(F.text == "/start")
async def start(message: Message):
    log_start(message.from_user.id)

    categories = get_categories(products)

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c, callback_data=f"cat:{c}")

    kb.adjust(2)

    await message.answer("Выбери категорию:", reply_markup=kb.as_markup())


# ---------- CATEGORY ----------
@dp.callback_query(F.data.startswith("cat:"))
async def category(call: CallbackQuery):
    category_name = call.data.split(":")[1]

    items = get_by_category(products, category_name)

    kb = InlineKeyboardBuilder()

    for i, p in enumerate(items[:10]):
        kb.button(
            text=f"{p['name']} — {p['price']}₽",
            callback_data=f"prod:{category_name}:{i}"
        )

    kb.adjust(1)

    await call.message.delete()

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=f"📦 Категория: {category_name}",
        reply_markup=kb.as_markup()
    )


# ---------- PRODUCT ----------
@dp.callback_query(F.data.startswith("prod:"))
async def product(call: CallbackQuery):
    _, category_name, index = call.data.split(":")
    index = int(index)

    items = get_by_category(products, category_name)
    p = items[index]

    text = f"""
{p['name']}

{p['description']}

💰 {p['price']}₽
"""

    kb = InlineKeyboardBuilder()

    # BUY BUTTON (теперь трекаем клик)
    kb.button(
        text="🛒 Купить",
        callback_data=f"buy:{p['url']}"
    )

    kb.button(
        text="⬅️ Назад",
        callback_data=f"cat:{category_name}"
    )

    kb.adjust(1)

    await call.message.delete()

    await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=p["picture"],
        caption=text,
        reply_markup=kb.as_markup()
    )


# ---------- BUY CLICK ----------
@dp.callback_query(F.data.startswith("buy:"))
async def buy(call: CallbackQuery):
    url = call.data.replace("buy:", "")

    log_buy_click()

    await call.answer("Открываю товар...")

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=f"🛒 Ссылка на товар:\n{url}"
    )


# ---------- ANALYTICS ----------
@dp.message(F.text.startswith("/analytics"))
async def analytics(message: Message):
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Нужен код доступа")
        return

    code = parts[1]

    if code != ADMIN_CODE:
        await message.answer("⛔ Доступ запрещён")
        return

    stats = get_stats()

    await message.answer(
        f"""
📊 АНАЛИТИКА

👤 Уникальные пользователи (START):
{stats['users']}

🛒 Клики "Купить":
{stats['buy_clicks']}
"""
    )


# ---------- RUN ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())