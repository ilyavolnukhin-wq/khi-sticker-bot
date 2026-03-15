import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, ADMIN_ID, TOTAL_NUMERIC, TOTAL_LETTER, RENDER_EXTERNAL_URL, PORT
from database.db import db
from keyboards.keyboards import main_menu_keyboard

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
WEBHOOK_PATH = "/webhook"

async def on_startup(bot: Bot):
    await db.create_pool()
    await db.init_tables()
    async with db.pool.acquire() as conn:
        album_exists = await conn.fetchval("SELECT COUNT(*) FROM albums")
        if album_exists == 0:
            await conn.execute(
                "INSERT INTO albums (name, total_numeric, total_letter) VALUES ($1, $2, $3)",
                "КХЛ 2025/2026", TOTAL_NUMERIC, TOTAL_LETTER
            )
            print("✅ Альбом создан")
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await db.close()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE telegram_id = $1", user_id)
        if not user:
            album = await conn.fetchrow("SELECT id, name FROM albums WHERE is_active = true LIMIT 1")
            if album:
                await conn.execute(
                    "INSERT INTO users (telegram_id, username, album_id) VALUES ($1, $2, $3)",
                    user_id, message.from_user.username, album['id']
                )
                await message.answer(
                    f"🏒 Добро пожаловать в KHL Sticker Tracker!\n\n"
                    f"📖 Альбом: {album['name']}\n"
                    f"📊 Всего карточек: {TOTAL_NUMERIC} числовых + {TOTAL_LETTER} буквенных",
                    reply_markup=main_menu_keyboard()
                )
        else:
            await message.answer(
                f"👋 С возвращением, {message.from_user.first_name}!",
                reply_markup=main_menu_keyboard()
            )

@dp.message(F.text == "📊 Прогресс")
async def show_progress(message: Message):
    user_id = message.from_user.id
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE telegram_id = $1", user_id)
        if user:
            have = await conn.fetchval("SELECT COUNT(*) FROM user_stickers WHERE user_id = $1 AND status = 'have'", user['id'])
            dup = await conn.fetchval("SELECT COUNT(*) FROM user_stickers WHERE user_id = $1 AND status = 'duplicate'", user['id'])
            percent = round((have / TOTAL_NUMERIC) * 100, 2) if TOTAL_NUMERIC > 0 else 0
            await message.answer(
                f"📊 ВАШ ПРОГРЕСС\n\n"
                f"✅ Заполнено: {have}/{TOTAL_NUMERIC} ({percent}%)\n"
                f"🔁 Дубликаты: {dup}\n"
                f"❌ Не хватает: {TOTAL_NUMERIC - have}"
            )

@dp.message(F.text == "📋 Мой альбом")
async def my_album(message: Message):
    await message.answer("📚 Выберите раздел:", reply_markup=album_sections_keyboard())

@dp.message(F.text == "➕ Добавить карточки")
async def add_stickers(message: Message):
    await message.answer("📝 Введите номера через запятую (пример: 1, 5, 12-20):")

@dp.message(F.text, ~Command("start"))
async def handle_text(message: Message):
    if message.text and message.text.replace(',', '').replace('-', '').isdigit():
        numbers = []
        for part in message.text.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(part))
        
        user_id = message.from_user.id
        added = 0
        dups = 0
        
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT id FROM users WHERE telegram_id = $1", user_id)
            if user:
                for num in numbers:
                    sticker = await conn.fetchrow("SELECT id FROM stickers WHERE number = $1", str(num))
                    if sticker:
                        exists = await conn.fetchrow("SELECT id, status FROM user_stickers WHERE user_id = $1 AND sticker_id = $2", user['id'], sticker['id'])
                        if exists:
                            await conn.execute("UPDATE user_stickers SET status = 'duplicate' WHERE id = $1", exists['id'])
                            dups += 1
                        else:
                            await conn.execute("INSERT INTO user_stickers (user_id, sticker_id, status) VALUES ($1, $2, 'have')", user['id'], sticker['id'])
                            added += 1
        
        await message.answer(f"✅ Добавлено!\n🆕 Новых: {added}\n🔁 Дубликатов: {dups}")

async def main():
    print("🚀 Бот запускается...")
    if not RENDER_EXTERNAL_URL:
        await on_startup(bot)
        await dp.start_polling(bot)
    else:
        app = web.Application()
        router = SimpleRequestHandler(dispatcher=dp, bot=bot)
        router.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"✅ Сервер запущен на порту {PORT}")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

