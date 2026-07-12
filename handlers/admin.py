import io, json, logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from states import AdminStates
from database import (
    is_admin, get_setting, set_setting, get_all_admins, add_admin, remove_admin,
    get_force_channels, add_force_channel, remove_force_channel, export_backup, import_backup,
)
from keyboards import (
    build_panel_keyboard, admin_stats_kb, admin_manage_kb, admin_texts_kb,
    admin_bot_status_kb, admin_backup_kb, admin_messaging_kb, admin_buttons_kb,
    admin_channels_kb, cancel_kb, back_kb, remove_channel_kb,
)
from config import MAIN_ADMINS

logger = logging.getLogger(__name__)
router = Router()

TEXT_MAP = {
    "edit_text_welcome": ("welcome_text", AdminStates.edit_welcome),
    "edit_text_auto_reply": ("auto_reply_text", AdminStates.edit_auto_reply),
    "edit_text_ban": ("ban_text", AdminStates.edit_ban),
    "edit_text_force_join": ("force_join_text", AdminStates.edit_force_join),
    "edit_text_admin_msg": ("admin_new_msg_text", AdminStates.edit_admin_msg),
    "edit_text_inactive": ("inactive_link_text", AdminStates.edit_inactive_link),
}


@router.callback_query(F.data == "adm_main")
async def adm_main(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    await cb.message.edit_text("🛡️ <b>پنل مدیریت</b>", reply_markup=await build_panel_keyboard("admin"), parse_mode="HTML")
    await cb.answer()


@router.message(F.text == "📊 آمار و وضعیت")
async def t_stats(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("📊", reply_markup=admin_stats_kb())

@router.message(F.text == "👥 مدیریت ادمین‌ها")
async def t_admins(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("👥", reply_markup=admin_manage_kb("admins"))

@router.message(F.text == "📢 مدیریت چنل‌ها")
async def t_channels(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("📢", reply_markup=admin_channels_kb())

@router.message(F.text == "✏️ مدیریت متن‌ها")
async def t_texts(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("✏️", reply_markup=admin_texts_kb())

@router.message(F.text == "📨 ارسال پیام")
async def t_msg(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("📨", reply_markup=admin_messaging_kb())

@router.message(F.text == "🔧 مدیریت دکمه‌ها")
async def t_btns(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("🔧", reply_markup=admin_buttons_kb())

@router.message(F.text == "🛡️ ضد اسپم")
async def t_antispam(m: Message):
    if not await is_admin(m.from_user.id): return
    from handlers.admin_antispam import show_antispam
    await show_antispam(m)

@router.message(F.text == "🔒 ناشناس")
async def t_anon(m: Message):
    if not await is_admin(m.from_user.id): return
    from handlers.admin_anon import show_anon
    await show_anon(m)

@router.message(F.text == "⚙️ وضعیت ربات")
async def t_status(m: Message):
    if not await is_admin(m.from_user.id): return
    await m.answer("⚙️", reply_markup=admin_bot_status_kb(await get_setting("bot_enabled")))

@router.message(F.text == "📁 بکاپ")
async def t_backup(m: Message):
    if not await is_admin(m.from_user.id): return
    await _show_backup(m)


@router.callback_query(F.data == "adm_admins")
async def adm_admins(cb: CallbackQuery):
    await cb.message.edit_text("👥 مدیریت ادمین‌ها:", reply_markup=admin_manage_kb("admins"))
    await cb.answer()

@router.callback_query(F.data == "adm_admins_list")
async def adm_admins_list(cb: CallbackQuery):
    admins = await get_all_admins()
    text = "👥 <b>لیست ادمین‌ها:</b>\n\n"
    for a in admins:
        u = f"@{a['username']}" if a.get("username") else "ندارد"
        text += f"• <code>{a['user_id']}</code> — {u}\n  آخرین فعالیت: {a.get('last_activity', '?')}\n\n"
    await cb.message.edit_text(text, reply_markup=back_kb("adm_admins"), parse_mode="HTML")

@router.callback_query(F.data == "adm_admins_add")
async def adm_admins_add(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_admin)
    await cb.message.edit_text("➕ آیدی عددی ادمین:", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.add_admin, F.text)
async def adm_admins_add_p(m: Message, state: FSMContext):
    try: new_id = int(m.text.strip())
    except ValueError:
        await m.answer("❌ آیدی نامعتبر."); return
    await add_admin(new_id, added_by=m.from_user.id)
    await m.answer(f"✅ ادمین <code>{new_id}</code> اضافه شد.", reply_markup=back_kb("adm_admins"), parse_mode="HTML")
    await state.clear()

@router.callback_query(F.data == "adm_admins_remove")
async def adm_admins_rm(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.remove_admin)
    await cb.message.edit_text("➖ آیدی ادمین برای حذف:", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.remove_admin, F.text)
async def adm_admins_rm_p(m: Message, state: FSMContext):
    try: rm_id = int(m.text.strip())
    except ValueError:
        await m.answer("❌ آیدی نامعتبر."); return
    if rm_id in MAIN_ADMINS:
        await m.answer("⛔ ادمین اصلی قابل حذف نیست."); return
    await remove_admin(rm_id)
    await m.answer("✅ حذف شد.", reply_markup=back_kb("adm_admins"))
    await state.clear()


@router.callback_query(F.data == "adm_channels")
async def adm_channels(cb: CallbackQuery):
    await cb.message.edit_text("📢 <b>مدیریت کانال‌های اسپانسری</b>", reply_markup=admin_channels_kb(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "adm_channels_list")
async def adm_channels_list(cb: CallbackQuery):
    channels = await get_force_channels()
    text = "📢 <b>کانال‌های اسپانسری:</b>\n\n" if channels else "📢 کانالی ثبت نشده.\n\n"
    for ch in channels:
        text += f"• {ch.get('button_title', '?')} | <code>{ch['channel_id']}</code>\n"
    if channels:
        text += f"\n📊 تعداد: {len(channels)} کانال"
    await cb.message.edit_text(text, reply_markup=back_kb("adm_channels"), parse_mode="HTML")

@router.callback_query(F.data == "adm_channels_add")
async def adm_channels_add(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_channel_id)
    await cb.message.edit_text(
        "➕ آیدی یا یوزرنیم کانال رو بفرست:\n\n"
        "مثال‌ها:\n"
        "• <code>@mychannel</code>\n"
        "• <code>-1001234567890</code>\n\n"
        "💡 برای پیدا کردن آیدی عددی:\n"
        "ربات @userinfobot رو استارت کن و پیام فورواردی از کانال رو بفرست",
        reply_markup=cancel_kb(), parse_mode="HTML",
    )
    await cb.answer()

@router.message(AdminStates.add_channel_id, F.text)
async def ch_add_id(m: Message, state: FSMContext):
    cid = m.text.strip()
    await state.update_data(channel_id=cid)
    await state.set_state(AdminStates.add_channel_title)
    await m.answer(
        f"✅ آیدی: <code>{cid}</code>\n\n"
        f"📝 حالا عنوان کانال رو بنویس\n"
        f"(مثال: کانال خبری من)",
        reply_markup=cancel_kb(), parse_mode="HTML",
    )

@router.message(AdminStates.add_channel_title, F.text)
async def ch_add_title(m: Message, state: FSMContext):
    await state.update_data(channel_title=m.text.strip())
    await state.set_state(AdminStates.add_channel_button)
    await m.answer("🔘 عنوان دکمه‌ای که کاربر ببینه رو بنویس\n(مثال: عضویت در کانال)", reply_markup=cancel_kb())

@router.message(AdminStates.add_channel_button, F.text)
async def ch_add_btn(m: Message, state: FSMContext):
    d = await state.get_data()
    cid = d["channel_id"]
    un = cid.lstrip("@") if cid.startswith("@") else None
    await add_force_channel(cid, un, d["channel_title"], m.text.strip())
    await m.answer("✅ کانال اسپانسری اضافه شد.\n\n⚠️ مطمئن شو ربات ادمین کانال هست تا بتونه عضویت رو چک کنه.", reply_markup=back_kb("adm_channels"))
    await state.clear()

@router.callback_query(F.data == "adm_channels_remove")
async def adm_channels_rm(cb: CallbackQuery):
    ch = await get_force_channels()
    if not ch:
        await cb.message.edit_text("📢 کانالی نیست.", reply_markup=back_kb("adm_channels"))
    else:
        await cb.message.edit_text("🗑 کانال مورد نظر رو انتخاب کن:", reply_markup=remove_channel_kb(ch))
    await cb.answer()

@router.callback_query(F.data.startswith("remove_ch_"))
async def rm_ch_p(cb: CallbackQuery):
    await remove_force_channel(cb.data.replace("remove_ch_", ""))
    await cb.answer("✅ حذف شد")
    ch = await get_force_channels()
    if ch:
        await cb.message.edit_reply_markup(reply_markup=remove_channel_kb(ch))
    else:
        await cb.message.edit_text("📢 کانالی نیست.", reply_markup=back_kb("adm_channels"))


@router.callback_query(F.data == "adm_texts")
async def adm_texts(cb: CallbackQuery):
    await cb.message.edit_text("✏️ متن‌ها:", reply_markup=admin_texts_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("edit_text_"))
async def edit_text_start(cb: CallbackQuery, state: FSMContext):
    key = cb.data
    if key not in TEXT_MAP:
        await cb.answer("❌", show_alert=True); return
    sk, fs = TEXT_MAP[key]
    cur = await get_setting(sk)
    await state.set_state(fs)
    await state.update_data(edit_key=sk)
    await cb.message.edit_text(f"✏️ متن فعلی:\n<code>{cur}</code>\n\nمتن جدید:", reply_markup=cancel_kb(), parse_mode="HTML")
    await cb.answer()

@router.message(AdminStates.edit_welcome)
@router.message(AdminStates.edit_auto_reply)
@router.message(AdminStates.edit_ban)
@router.message(AdminStates.edit_force_join)
@router.message(AdminStates.edit_admin_msg)
@router.message(AdminStates.edit_inactive_link)
async def edit_text_p(m: Message, state: FSMContext):
    d = await state.get_data()
    k = d.get("edit_key")
    if k:
        await set_setting(k, m.text)
        await m.answer("✅ ذخیره شد.", reply_markup=back_kb("adm_texts"))
    await state.clear()


@router.callback_query(F.data == "adm_bot_status")
async def adm_bot_status(cb: CallbackQuery):
    await cb.message.edit_text("⚙️ وضعیت:", reply_markup=admin_bot_status_kb(await get_setting("bot_enabled")))
    await cb.answer()

@router.callback_query(F.data == "adm_toggle_bot")
async def adm_toggle_bot(cb: CallbackQuery):
    cur = await get_setting("bot_enabled")
    await set_setting("bot_enabled", "0" if cur == "1" else "1")
    await cb.message.edit_reply_markup(reply_markup=admin_bot_status_kb(await get_setting("bot_enabled")))
    await cb.answer("تغییر کرد")


async def _show_backup(target):
    enabled = await get_setting("backup_enabled")
    interval = await get_setting("backup_interval")
    channel = await get_setting("backup_channel")
    if isinstance(target, Message):
        await target.answer("📁 بکاپ:", reply_markup=admin_backup_kb(enabled, interval, channel))
    else:
        await target.message.edit_text("📁 بکاپ:", reply_markup=admin_backup_kb(enabled, interval, channel))

@router.callback_query(F.data == "adm_backup")
async def adm_backup(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    await _show_backup(cb)
    await cb.answer()

@router.callback_query(F.data == "backup_toggle")
async def backup_toggle(cb: CallbackQuery):
    cur = await get_setting("backup_enabled")
    await set_setting("backup_enabled", "0" if cur == "1" else "1")
    await _show_backup(cb)
    await cb.answer("✅ تغییر کرد")

@router.callback_query(F.data == "backup_set_interval")
async def backup_set_interval(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.backup_interval)
    await cb.message.edit_text("⏱️ فاصله بکاپ (ثانیه):\nمثال: 3600 = هر ساعت", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.backup_interval, F.text)
async def backup_interval_p(m: Message, state: FSMContext):
    try:
        val = int(m.text.strip())
        if val < 60: raise ValueError
    except ValueError:
        await m.answer("❌ حداقل 60 ثانیه.")
        return
    await set_setting("backup_interval", str(val))
    await m.answer(f"✅ فاصله: {val} ثانیه", reply_markup=back_kb("adm_backup"))
    await state.clear()

@router.callback_query(F.data == "backup_set_channel")
async def backup_set_ch(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.set_backup_channel)
    await cb.message.edit_text("📁 آیدی کانال بکاپ:\n(0 = غیرفعال)", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.set_backup_channel, F.text)
async def backup_set_ch_p(m: Message, state: FSMContext):
    await set_setting("backup_channel", m.text.strip())
    await m.answer("✅ کانال تنظیم شد.", reply_markup=back_kb("adm_backup"))
    await state.clear()

@router.callback_query(F.data == "backup_export")
async def backup_export(cb: CallbackQuery):
    await cb.answer("⏳ در حال ساخت...")
    data = await export_backup()
    jb = json.dumps(data, ensure_ascii=False, indent=2, default=str).encode()
    await cb.message.answer_document(BufferedInputFile(jb, filename="backup.json"), caption=f"✅ بکاپ — {data.get('_exported_at', '')}")

@router.callback_query(F.data == "backup_import")
async def backup_import_s(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.restore_backup)
    await cb.message.edit_text("📤 فایل بکاپ JSON:", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.restore_backup, F.document)
async def backup_import_p(m: Message, state: FSMContext):
    file = await m.bot.get_file(m.document.file_id)
    buf = io.BytesIO()
    await m.bot.download_file(file.file_path, buf)
    try:
        data = json.loads(buf.getvalue().decode())
        await import_backup(data)
        await m.answer("✅ بازیابی شد!", reply_markup=back_kb("adm_backup"))
    except Exception as e:
        await m.answer(f"❌ خطا: {e}", reply_markup=back_kb("adm_backup"))
    await state.clear()
