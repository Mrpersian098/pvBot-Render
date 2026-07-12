import asyncio, json, io, logging
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, MAIN_ADMINS, PORT
from database import init_db, get_setting
from middlewares import ThrottlingMiddleware, UserCheckMiddleware, ForceJoinMiddleware, AntiSpamMiddleware
from handlers import all_routers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def scheduled_backup(bot):
    while True:
        try:
            enabled = await get_setting("backup_enabled")
            interval = int(await get_setting("backup_interval") or "3600")
            channel = await get_setting("backup_channel")
            if enabled == "1" and channel and channel != "0":
                from database import export_backup
                data = await export_backup()
                jb = json.dumps(data, ensure_ascii=False, indent=2, default=str).encode()
                await bot.send_document(int(channel), document=io.BytesIO(jb), caption=f"🔄 بکاپ خودکار — {datetime.utcnow().isoformat()[:19]}", filename=f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
                logger.info("بکاپ خودکار ارسال شد")
            await asyncio.sleep(max(interval, 60))
        except Exception as e:
            logger.error(f"بکاپ: {e}")
            await asyncio.sleep(300)


# ─── وب سرور ساده (فقط برای Render) ───
async def handle_health(request):
    return web.Response(text="🤖 Bot is running!", status=200)


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 وب سرور روی پورت {PORT}")


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده!")
    if not MAIN_ADMINS:
        raise ValueError("MAIN_ADMINS تنظیم نشده!")

    await init_db()
    logger.info("✅ دیتابیس آماده")

    # وب سرور ساده (Render پورت میخواد)
    await start_web_server()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(UserCheckMiddleware())
    dp.message.middleware(AntiSpamMiddleware())
    dp.message.middleware(ForceJoinMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    for r in all_routers:
        dp.include_router(r)

    asyncio.create_task(scheduled_backup(bot))

    me = await bot.me()
    logger.info(f"🤖 @{me.username} فعال!")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
