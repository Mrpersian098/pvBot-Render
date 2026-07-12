import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states import AdminStates
from database import (
    is_admin, get_user_count, get_users_count_period,
    get_top_users, get_message_count, get_messages_count_period,
    get_all_anon_links, get_setting,
)
from keyboards import admin_stats_kb, stats_period_kb, back_kb, cancel_kb
from utils import get_server_status, format_server_status, get_date_range, format_user_info

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "adm_stats")
async def adm_stats(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id): return
    await callback.message.edit_text("📊 آمار:", reply_markup=admin_stats_kb())
    await callback.answer()


@router.callback_query(F.data == "stats_server")
async def stats_server(callback: CallbackQuery):
    status = get_server_status()
    text = format_server_status(status)
    bot_enabled = await get_setting("bot_enabled")
    text += f"\n\n🤖 ربات: {'🟢 روشن' if bot_enabled == '1' else '🔴 خاموش'}"
    text += f"\n👥 کل کاربران: {await get_user_count()}"
    text += f"\n💬 کل پیام‌ها: {await get_message_count()}"
    await callback.message.edit_text(text, reply_markup=back_kb("adm_stats"), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "stats_users_menu")
async def stats_users_menu(callback: CallbackQuery):
    await callback.message.edit_text("👤 آمار کاربران — بازه:", reply_markup=stats_period_kb("stats_users"))
    await callback.answer()


@router.callback_query(F.data.startswith("stats_users_"))
async def stats_users_p(callback: CallbackQuery, state: FSMContext):
    period = callback.data.replace("stats_users_", "")
    if period == "custom":
        await state.set_state(AdminStates.custom_stats_start)
        await state.update_data(stats_type="users")
        await callback.message.edit_text("📅 تاریخ شروع (مثال: 2025-01-01):", reply_markup=cancel_kb())
        await callback.answer()
        return
    start, end = get_date_range(period)
    count = await get_users_count_period(start, end)
    total = await get_user_count()
    names = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}
    await callback.message.edit_text(
        f"👤 {names.get(period, period)}\n\nجدید: {count}\nکل: {total}",
        reply_markup=back_kb("stats_users_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "stats_top_users")
async def stats_top(callback: CallbackQuery):
    top = await get_top_users(10)
    text = "⭐ <b>۱۰ کاربر برتر:</b>\n\n"
    for i, u in enumerate(top, 1):
        text += f"{i}. {format_user_info(u)}\n"
    if not top:
        text += "کاربری نیست."
    await callback.message.edit_text(text, reply_markup=back_kb("adm_stats"), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "stats_msgs_menu")
async def stats_msgs_menu(callback: CallbackQuery):
    await callback.message.edit_text("💬 آمار پیام‌ها — بازه:", reply_markup=stats_period_kb("stats_msgs"))
    await callback.answer()


@router.callback_query(F.data.startswith("stats_msgs_"))
async def stats_msgs_p(callback: CallbackQuery, state: FSMContext):
    period = callback.data.replace("stats_msgs_", "")
    if period == "custom":
        await state.set_state(AdminStates.custom_stats_start)
        await state.update_data(stats_type="messages")
        await callback.message.edit_text("📅 تاریخ شروع:", reply_markup=cancel_kb())
        await callback.answer()
        return
    start, end = get_date_range(period)
    count = await get_messages_count_period(start, end)
    total = await get_message_count()
    names = {"daily": "روزانه", "weekly": "هفتگی", "monthly": "ماهانه", "yearly": "سالانه"}
    await callback.message.edit_text(
        f"💬 {names.get(period, period)}\n\nدر بازه: {count}\nکل: {total}",
        reply_markup=back_kb("stats_msgs_menu"),
    )
    await callback.answer()


@router.message(AdminStates.custom_stats_start, F.text)
async def custom_start(message: Message, state: FSMContext):
    await state.update_data(custom_start=message.text.strip())
    await state.set_state(AdminStates.custom_stats_end)
    await message.answer("📅 تاریخ پایان:", reply_markup=cancel_kb())


@router.message(AdminStates.custom_stats_end, F.text)
async def custom_end(message: Message, state: FSMContext):
    data = await state.get_data()
    start = data["custom_start"]
    end = message.text.strip()
    if data.get("stats_type") == "users":
        count = await get_users_count_period(start, end)
        total = await get_user_count()
        await message.answer(f"👤 سفارشی\nجدید: {count}\nکل: {total}", reply_markup=back_kb("stats_users_menu"))
    else:
        count = await get_messages_count_period(start, end)
        total = await get_message_count()
        await message.answer(f"💬 سفارشی\nدر بازه: {count}\nکل: {total}", reply_markup=back_kb("stats_msgs_menu"))
    await state.clear()


@router.callback_query(F.data == "stats_links")
async def stats_links(callback: CallbackQuery):
    links = await get_all_anon_links()
    text = "🔗 <b>لینک‌ها:</b>\n\n"
    active = inactive = 0
    for l in links:
        s = "🟢" if l["is_active"] else "🔴"
        if l["is_active"]: active += 1
        else: inactive += 1
        last = l.get("last_used") or "هرگز"
        text += f"• <code>{l['link_code']}</code> {s} | مالک: {l['owner_id']} | پیام: {l['message_count']} | {last}\n"
    if not links:
        text += "لینکی نیست."
    text += f"\n🟢 {active} | 🔴 {inactive} | کل {len(links)}"
    await callback.message.edit_text(text, reply_markup=back_kb("adm_stats"), parse_mode="HTML")
    await callback.answer()
