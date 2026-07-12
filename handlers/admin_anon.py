import uuid
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AdminStates
from database import (
    is_admin, get_setting, set_setting, get_all_anon_links,
    get_anon_message_count, get_anon_unique_senders, create_anon_link,
    toggle_anon_link, delete_anon_link, get_recent_anon_messages,
    get_all_recent_anon_messages, block_anon_sender, unblock_anon_sender,
    get_anon_blocks, get_user_anon_links,
)
from keyboards import (
    admin_anon_kb, admin_anon_link_kb, admin_anon_detail_kb,
    anon_recent_kb, anon_msg_detail_kb, cancel_kb, back_kb,
)

logger = logging.getLogger(__name__)
router = Router()


async def show_anon(m: Message):
    enabled = await get_setting("anon_enabled")
    mc = await get_anon_message_count()
    us = await get_anon_unique_senders()
    await m.answer("🔒 مدیریت ناشناس:", reply_markup=admin_anon_kb(enabled, mc, us))


@router.callback_query(F.data == "adm_anon")
async def adm_anon(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    enabled = await get_setting("anon_enabled")
    mc = await get_anon_message_count()
    us = await get_anon_unique_senders()
    await cb.message.edit_text("🔒 مدیریت ناشناس:", reply_markup=admin_anon_kb(enabled, mc, us))
    await cb.answer()


@router.callback_query(F.data == "anon_toggle_global")
async def anon_toggle_global(cb: CallbackQuery):
    cur = await get_setting("anon_enabled")
    await set_setting("anon_enabled", "0" if cur == "1" else "1")
    enabled = await get_setting("anon_enabled")
    mc = await get_anon_message_count()
    us = await get_anon_unique_senders()
    await cb.message.edit_text("🔒 مدیریت ناشناس:", reply_markup=admin_anon_kb(enabled, mc, us))
    await cb.answer("✅ تغییر کرد")


@router.callback_query(F.data == "admin_my_links")
async def admin_my_links(cb: CallbackQuery):
    links = await get_user_anon_links(cb.from_user.id)
    if not links:
        await cb.message.edit_text("🔗 لینکی ندارید.", reply_markup=back_kb("adm_anon"))
    else:
        await cb.message.edit_text("🔗 لینک‌های شما:", reply_markup=admin_anon_link_kb(links))
    await cb.answer()


@router.callback_query(F.data == "admin_create_link")
async def admin_create_link(cb: CallbackQuery):
    code = uuid.uuid4().hex[:8]
    bot_username = (await cb.bot.me()).username
    await create_anon_link(cb.from_user.id, code)
    link = f"https://t.me/{bot_username}?start={code}"
    await cb.message.edit_text(f"✅ لینک ساخته شد:\n\n<code>{link}</code>", reply_markup=back_kb("admin_my_links"), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin_anon_det_"))
async def admin_anon_det(cb: CallbackQuery):
    code = cb.data.replace("admin_anon_det_", "")
    links = await get_user_anon_links(cb.from_user.id)
    link = next((l for l in links if l["link_code"] == code), None)
    if not link:
        await cb.answer("❌ یافت نشد", show_alert=True); return
    s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
    bot_username = (await cb.bot.me()).username
    await cb.message.edit_text(
        f"🔗 جزئیات:\n\nکد: <code>{code}</code>\n"
        f"لینک: <code>https://t.me/{bot_username}?start={code}</code>\n"
        f"وضعیت: {s}\nپیام: {link['message_count']}",
        reply_markup=admin_anon_detail_kb(code, link["is_active"]), parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("admin_anon_tog_"))
async def admin_anon_tog(cb: CallbackQuery):
    code = cb.data.replace("admin_anon_tog_", "")
    await toggle_anon_link(code)
    await cb.answer("✅ تغییر کرد")
    links = await get_user_anon_links(cb.from_user.id)
    link = next((l for l in links if l["link_code"] == code), None)
    if link:
        s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
        bot_username = (await cb.bot.me()).username
        await cb.message.edit_text(
            f"🔗 جزئیات:\n\nکد: <code>{code}</code>\n"
            f"لینک: <code>https://t.me/{bot_username}?start={code}</code>\n"
            f"وضعیت: {s}\nپیام: {link['message_count']}",
            reply_markup=admin_anon_detail_kb(code, link["is_active"]), parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("admin_anon_del_"))
async def admin_anon_del(cb: CallbackQuery):
    code = cb.data.replace("admin_anon_del_", "")
    await delete_anon_link(code)
    await cb.answer("🗑 حذف شد")
    await admin_my_links(cb)


@router.callback_query(F.data == "anon_recent")
async def anon_recent(cb: CallbackQuery):
    msgs = await get_all_recent_anon_messages(20)
    if not msgs:
        await cb.message.edit_text("📋 پیامی نیست.", reply_markup=back_kb("adm_anon"))
    else:
        await cb.message.edit_text("📋 پیام‌های اخیر:", reply_markup=anon_recent_kb(msgs))
    await cb.answer()


@router.callback_query(F.data.startswith("anon_msg_"))
async def anon_msg_detail(cb: CallbackQuery):
    mid = int(cb.data.replace("anon_msg_", ""))
    from database import get_db
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM anon_messages WHERE id=?", (mid,))
        msg = dict(rows[0]) if rows else None
    finally:
        await db.close()
    if not msg:
        await cb.answer("❌ یافت نشد", show_alert=True); return
    txt = msg.get("message_text", "")[:200]
    ts = msg.get("timestamp", "?")
    await cb.message.edit_text(
        f"📩 پیام #{mid}\n\n"
        f"فرستنده: <code>{msg['sender_id']}</code>\n"
        f"مالک لینک: <code>{msg['link_owner_id']}</code>\n"
        f"نوع: {msg['content_type']}\n"
        f"زمان: {ts}\n\n"
        f"متن: {txt}",
        reply_markup=anon_msg_detail_kb(mid, msg["sender_id"]), parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("anon_block_"))
async def anon_block(cb: CallbackQuery):
    sid = int(cb.data.replace("anon_block_", ""))
    await block_anon_sender(cb.from_user.id, sid)
    await cb.answer(f"🚫 {sid} بلاک شد")


@router.callback_query(F.data == "anon_blocks_list")
async def anon_blocks_list(cb: CallbackQuery):
    blocks = await get_anon_blocks(cb.from_user.id)
    text = "🚫 <b>لیست بلاک‌ها:</b>\n\n"
    if not blocks:
        text += "کسی بلاک نشده."
    for b in blocks:
        text += f"• <code>{b['blocked_user_id']}</code> — {b['blocked_at']}\n"
    await cb.message.edit_text(text, reply_markup=back_kb("adm_anon"), parse_mode="HTML")
    await cb.answer()
