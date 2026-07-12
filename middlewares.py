import time
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Dict, Any
from database import is_banned, add_user, is_admin, update_admin_activity, get_setting
from config import THROTTLE_RATE

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_times: Dict[int, float] = {}

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]):
        if isinstance(event, (Message, CallbackQuery)):
            uid = event.from_user.id
            now = time.time()
            if now - self.user_times.get(uid, 0) < THROTTLE_RATE:
                if isinstance(event, CallbackQuery):
                    await event.answer("⏳ کمی صبر کنید...", show_alert=True)
                return
            self.user_times[uid] = now
        return await handler(event, data)


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_msgs: Dict[int, list] = {}
        self.muted: Dict[int, float] = {}

    async def __call__(self, handler, event: Message, data: Dict[str, Any]):
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)
        if await get_setting("antispam_enabled") != "1":
            return await handler(event, data)
        uid = event.from_user.id
        if await is_admin(uid):
            return await handler(event, data)
        now = time.time()
        if uid in self.muted:
            if now < self.muted[uid]:
                try:
                    remain = int(self.muted[uid] - now)
                    await event.answer(f"⏳ شما محدود شده‌اید. {remain} ثانیه صبر کنید.", show_alert=True)
                except:
                    pass
                return
            else:
                del self.muted[uid]
        interval = float(await get_setting("antispam_interval") or "3")
        limit = int(await get_setting("antispam_limit") or "10")
        period = float(await get_setting("antispam_period") or "60")
        action = await get_setting("antispam_action") or "mute"
        duration = float(await get_setting("antispam_duration") or "3600")
        if uid not in self.user_msgs:
            self.user_msgs[uid] = []
        if self.user_msgs[uid]:
            last = self.user_msgs[uid][-1]
            if now - last < interval:
                self.muted[uid] = now + duration
                if action == "ban":
                    await event.bot.ban_chat_member(event.chat.id, uid)
                try:
                    await event.answer(f"⚠️ اسپم! محدود به مدت {int(duration)} ثانیه.", show_alert=True)
                except:
                    pass
                return
        self.user_msgs[uid].append(now)
        cutoff = now - period
        self.user_msgs[uid] = [t for t in self.user_msgs[uid] if t > cutoff]
        if len(self.user_msgs[uid]) > limit:
            self.muted[uid] = now + duration
            if action == "ban":
                await event.bot.ban_chat_member(event.chat.id, uid)
            try:
                await event.answer(f"⚠️ اسپم! محدود به مدت {int(duration)} ثانیه.", show_alert=True)
            except:
                pass
            return
        return await handler(event, data)


class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]):
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)
        user = event.from_user
        await add_user(user.id, user.username, user.first_name)
        if await is_banned(user.id):
            await event.answer(await get_setting("ban_text"))
            return
        if await is_admin(user.id):
            await update_admin_activity(user.id)
        data["is_user_admin"] = await is_admin(user.id)
        return await handler(event, data)


class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]):
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)
        if data.get("is_user_admin") or await is_admin(event.from_user.id):
            return await handler(event, data)
        from database import get_force_channels
        channels = await get_force_channels()
        if not channels:
            return await handler(event, data)
        not_joined = []
        for ch in channels:
            try:
                member = await event.bot.get_chat_member(chat_id=ch["channel_id"], user_id=event.from_user.id)
                if member.status in ("left", "kicked"):
                    not_joined.append(ch)
            except:
                continue
        if not_joined:
            from keyboards import force_join_check_kb
            await event.answer(await get_setting("force_join_text"), reply_markup=force_join_check_kb(not_joined))
            return
        return await handler(event, data)
