from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import get_all_panel_buttons, get_custom_buttons


async def build_panel_keyboard(panel_type):
    from database import get_setting
    buttons = await get_all_panel_buttons(panel_type)
    setting = await get_setting(f"panel_type_{panel_type}")
    if setting == "keyboard":
        kb = ReplyKeyboardBuilder()
        rows = {}
        for b in buttons:
            if not b["visible"]:
                continue
            rows.setdefault(b["row"], []).append(b)
        for rn in sorted(rows.keys()):
            rb = sorted(rows[rn], key=lambda x: x["pos"])
            kb.row(*[KeyboardButton(text=b["text"]) for b in rb])
        return kb.as_markup(resize_keyboard=True)
    else:
        kb = InlineKeyboardBuilder()
        rows = {}
        for b in buttons:
            if not b["visible"]:
                continue
            rows.setdefault(b["row"], []).append(b)
        for rn in sorted(rows.keys()):
            rb = sorted(rows[rn], key=lambda x: x["pos"])
            kb.row(*[InlineKeyboardButton(text=b["text"], callback_data=b["callback"]) for b in rb])
        customs = await get_custom_buttons(panel_type)
        crows = {}
        for c in customs:
            crows.setdefault(c["row_number"], []).append(c)
        for rn in sorted(crows.keys()):
            cb = sorted(crows[rn], key=lambda x: x["position"])
            kb.row(*[InlineKeyboardButton(text=c["button_text"], callback_data=f"custom_{panel_type}_{c['id']}") for c in cb])
        return kb.as_markup()


def tools_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💰 ارز دیجیتال", callback_data="tool_crypto"), InlineKeyboardButton(text="🪙 طلا و سکه", callback_data="tool_gold"))
    kb.row(InlineKeyboardButton(text="📐 تبدیل واحدها", callback_data="tool_unit"), InlineKeyboardButton(text="⚖️ محاسبه BMI", callback_data="tool_bmi"))
    kb.row(InlineKeyboardButton(text="🍎 شمارش کالری", callback_data="tool_calorie"), InlineKeyboardButton(text="📅 تقویم شمسی", callback_data="tool_calendar"))
    kb.row(InlineKeyboardButton(text="📱 اطلاعات گوشی", callback_data="tool_phone"), InlineKeyboardButton(text="📝 متن تصادفی", callback_data="tool_random_text"))
    kb.row(InlineKeyboardButton(text="🎮 بازی‌ها", callback_data="tool_games"), InlineKeyboardButton(text="🔗 لینک کوتاه", callback_data="tool_shorturl"))
    kb.row(InlineKeyboardButton(text="🔮 فال حافظ", callback_data="tool_hafez"))
    kb.row(InlineKeyboardButton(text="🖼️ عکس → PDF", callback_data="tool_img2pdf"), InlineKeyboardButton(text="🔄 تبدیل فرمت عکس", callback_data="tool_convert"))
    kb.row(InlineKeyboardButton(text="📊 QR Code", callback_data="tool_qr"), InlineKeyboardButton(text="🔐 رمز عبور", callback_data="tool_password"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_panel"))
    return kb.as_markup()


def admin_channels_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📋 لیست کانال‌ها", callback_data="adm_channels_list"))
    kb.row(InlineKeyboardButton(text="➕ افزودن کانال", callback_data="adm_channels_add"), InlineKeyboardButton(text="➖ حذف کانال", callback_data="adm_channels_remove"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_stats_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🖥️ وضعیت سرور", callback_data="stats_server"))
    kb.row(InlineKeyboardButton(text="👤 آمار کاربران", callback_data="stats_users_menu"), InlineKeyboardButton(text="💬 آمار پیام‌ها", callback_data="stats_msgs_menu"))
    kb.row(InlineKeyboardButton(text="🔗 لینک‌های ناشناس", callback_data="stats_links"), InlineKeyboardButton(text="⭐ کاربران برتر", callback_data="stats_top_users"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def stats_period_kb(prefix):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📅 روزانه", callback_data=f"{prefix}_daily"), InlineKeyboardButton(text="📅 هفتگی", callback_data=f"{prefix}_weekly"))
    kb.row(InlineKeyboardButton(text="📅 ماهانه", callback_data=f"{prefix}_monthly"), InlineKeyboardButton(text="📅 سالانه", callback_data=f"{prefix}_yearly"))
    kb.row(InlineKeyboardButton(text="📅 بازه سفارشی", callback_data=f"{prefix}_custom"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_stats"))
    return kb.as_markup()


def admin_manage_kb(kind):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📋 لیست", callback_data=f"adm_{kind}_list"), InlineKeyboardButton(text="➕ افزودن", callback_data=f"adm_{kind}_add"))
    kb.row(InlineKeyboardButton(text="➖ حذف", callback_data=f"adm_{kind}_remove"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_texts_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="👋 خوش‌آمدگویی", callback_data="edit_text_welcome"), InlineKeyboardButton(text="✅ پاسخ خودکار", callback_data="edit_text_auto_reply"))
    kb.row(InlineKeyboardButton(text="⛔ متن بن", callback_data="edit_text_ban"), InlineKeyboardButton(text="⚠️ جوین اجباری", callback_data="edit_text_force_join"))
    kb.row(InlineKeyboardButton(text="📩 متن دریافت پیام ادمین", callback_data="edit_text_admin_msg"))
    kb.row(InlineKeyboardButton(text="🚫 متن لینک غیرفعال", callback_data="edit_text_inactive"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_messaging_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📤 ارسال تکی", callback_data="msg_single"), InlineKeyboardButton(text="📢 ارسال همگانی", callback_data="msg_broadcast"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_buttons_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🎨 ویرایش گرافیکی کاربر", callback_data="graph_edit_user"), InlineKeyboardButton(text="🎨 ویرایش گرافیکی ادمین", callback_data="graph_edit_admin"))
    kb.row(InlineKeyboardButton(text="➕ افزودن دکمه کاربر", callback_data="btn_add_user"), InlineKeyboardButton(text="➕ افزودن دکمه ادمین", callback_data="btn_add_admin"))
    kb.row(InlineKeyboardButton(text="🔄 ریست کاربر", callback_data="btn_reset_user"), InlineKeyboardButton(text="🔄 ریست ادمین", callback_data="btn_reset_admin"))
    kb.row(InlineKeyboardButton(text="🎨 نوع پنل کاربر", callback_data="btn_panel_user"), InlineKeyboardButton(text="🎨 نوع پنل ادمین", callback_data="btn_panel_admin"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_bot_status_kb(current):
    kb = InlineKeyboardBuilder()
    st = "🟢 روشن" if current == "1" else "🔴 خاموش"
    tg = "🔴 خاموش" if current == "1" else "🟢 روشن"
    kb.row(InlineKeyboardButton(text=f"وضعیت: {st}", callback_data="noop"))
    kb.row(InlineKeyboardButton(text=tg, callback_data="adm_toggle_bot"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_backup_kb(enabled, interval, channel):
    kb = InlineKeyboardBuilder()
    st = "🟢 فعال" if enabled == "1" else "🔴 غیرفعال"
    tg = "🔴 غیرفعال" if enabled == "1" else "🟢 فعال"
    kb.row(InlineKeyboardButton(text=f"بکاپ خودکار: {st}", callback_data="noop"))
    kb.row(InlineKeyboardButton(text=tg, callback_data="backup_toggle"))
    kb.row(InlineKeyboardButton(text=f"⏱️ هر {interval} ثانیه", callback_data="backup_set_interval"))
    kb.row(InlineKeyboardButton(text=f"📁 کانال: {channel}", callback_data="backup_set_channel"))
    kb.row(InlineKeyboardButton(text="📥 دریافت بکاپ", callback_data="backup_export"), InlineKeyboardButton(text="📤 بازیابی بکاپ", callback_data="backup_import"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_antispam_kb(enabled, interval, limit, period, action, duration):
    kb = InlineKeyboardBuilder()
    st = "🟢 فعال" if enabled == "1" else "🔴 غیرفعال"
    tg = "🔴 غیرفعال" if enabled == "1" else "🟢 فعال"
    kb.row(InlineKeyboardButton(text=f"وضعیت: {st}", callback_data="noop"))
    kb.row(InlineKeyboardButton(text=tg, callback_data="antispam_toggle"))
    kb.row(InlineKeyboardButton(text=f"⏱️ فاصله: {interval} ثانیه", callback_data="antispam_set_interval"), InlineKeyboardButton(text=f"📊 حداکثر: {limit} پیام", callback_data="antispam_set_limit"))
    kb.row(InlineKeyboardButton(text=f"⏰ بازه: {period} ثانیه", callback_data="antispam_set_period"), InlineKeyboardButton(text=f"⏳ مدت: {duration} ثانیه", callback_data="antispam_set_duration"))
    act_label = "🔨 بن" if action == "ban" else "🔇 محدود"
    kb.row(InlineKeyboardButton(text=f"رفتار: {act_label}", callback_data="antispam_toggle_action"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def admin_anon_kb(enabled, mc, us):
    kb = InlineKeyboardBuilder()
    st = "🟢 فعال" if enabled == "1" else "🔴 غیرفعال"
    tg = "🔴 غیرفعال" if enabled == "1" else "🟢 فعال"
    kb.row(InlineKeyboardButton(text=f"وضعیت: {st}", callback_data="noop"))
    kb.row(InlineKeyboardButton(text=tg, callback_data="anon_toggle_global"))
    kb.row(InlineKeyboardButton(text=f"📩 پیام‌ها: {mc}", callback_data="noop"), InlineKeyboardButton(text=f"👤 افراد: {us}", callback_data="noop"))
    kb.row(InlineKeyboardButton(text="🔗 لینک‌های من", callback_data="admin_my_links"), InlineKeyboardButton(text="➕ ساخت لینک", callback_data="admin_create_link"))
    kb.row(InlineKeyboardButton(text="📋 پیام‌های اخیر", callback_data="anon_recent"))
    kb.row(InlineKeyboardButton(text="🚫 لیست بلاک‌ها", callback_data="anon_blocks_list"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    return kb.as_markup()


def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="cancel_action")]
    ])


def back_kb(cb="adm_main"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت", callback_data=cb)]])


def anon_links_kb(links):
    kb = InlineKeyboardBuilder()
    for link in links:
        s = "🟢" if link["is_active"] else "🔴"
        kb.row(InlineKeyboardButton(text=f"{s} {link['link_code']} ({link['message_count']} پیام)", callback_data=f"anon_detail_{link['link_code']}"))
    kb.row(InlineKeyboardButton(text="➕ ساخت لینک جدید", callback_data="create_anon_link"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_panel"))
    return kb.as_markup()


def anon_detail_kb(code, is_active):
    kb = InlineKeyboardBuilder()
    tg = "🔴 غیرفعال" if is_active else "🟢 فعال"
    kb.row(InlineKeyboardButton(text=tg, callback_data=f"anon_toggle_{code}"), InlineKeyboardButton(text="🗑 حذف", callback_data=f"anon_delete_{code}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="my_links"))
    return kb.as_markup()


def admin_anon_link_kb(links):
    kb = InlineKeyboardBuilder()
    for link in links:
        s = "🟢" if link["is_active"] else "🔴"
        kb.row(InlineKeyboardButton(text=f"{s} {link['link_code']} ({link['message_count']})", callback_data=f"admin_anon_det_{link['link_code']}"))
    kb.row(InlineKeyboardButton(text="➕ ساخت لینک جدید", callback_data="admin_create_link"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_anon"))
    return kb.as_markup()


def admin_anon_detail_kb(code, is_active):
    kb = InlineKeyboardBuilder()
    tg = "🔴 غیرفعال" if is_active else "🟢 فعال"
    kb.row(InlineKeyboardButton(text=tg, callback_data=f"admin_anon_tog_{code}"), InlineKeyboardButton(text="🗑 حذف", callback_data=f"admin_anon_del_{code}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_my_links"))
    return kb.as_markup()


def anon_recent_kb(messages):
    kb = InlineKeyboardBuilder()
    for msg in messages[:10]:
        txt = msg.get("message_text", msg.get("content_type", "?"))
        if len(txt) > 25:
            txt = txt[:25] + "..."
        ts = str(msg.get("timestamp", "?"))[:16]
        kb.row(InlineKeyboardButton(text=f"📩 {txt} ({ts})", callback_data=f"anon_msg_{msg['id']}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_anon"))
    return kb.as_markup()


def anon_msg_detail_kb(msg_id, sender_id):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💬 پاسخ", callback_data=f"anon_reply_{sender_id}"), InlineKeyboardButton(text="🚫 بلاک", callback_data=f"anon_block_{sender_id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="anon_recent"))
    return kb.as_markup()


def password_level_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🟢 آسان", callback_data="pass_easy"), InlineKeyboardButton(text="🟡 متوسط", callback_data="pass_medium"))
    kb.row(InlineKeyboardButton(text="🟠 سخت", callback_data="pass_hard"), InlineKeyboardButton(text="🔴 قوی", callback_data="pass_strong"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu"))
    return kb.as_markup()


def force_join_check_kb(channels):
    kb = InlineKeyboardBuilder()
    for ch in channels:
        title = ch.get("button_title") or ch.get("channel_title", "کانال")
        un = ch.get("channel_username")
        if un:
            kb.row(InlineKeyboardButton(text=title, url=f"https://t.me/{un}"))
    kb.row(InlineKeyboardButton(text="✅ عضو شدم", callback_data="check_join"))
    return kb.as_markup()


def remove_channel_kb(channels):
    kb = InlineKeyboardBuilder()
    for ch in channels:
        title = ch.get("button_title") or ch.get("channel_title", str(ch["channel_id"]))
        kb.row(InlineKeyboardButton(text=f"🗑 {title}", callback_data=f"remove_ch_{ch['channel_id']}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_channels"))
    return kb.as_markup()


def graph_editor_kb(panel_type, buttons, selected=None):
    kb = InlineKeyboardBuilder()
    rows = {}
    for b in buttons:
        rows.setdefault(b["row"], []).append(b)
    for rn in sorted(rows.keys()):
        rb = sorted(rows[rn], key=lambda x: x["pos"])
        row_btns = []
        for btn in rb:
            vis = "👁" if btn.get("visible", 1) else "🚫"
            sel = "✅ " if btn["key"] == selected else ""
            row_btns.append(InlineKeyboardButton(text=f"{sel}{btn['text']} {vis}", callback_data=f"gsel_{btn['key']}"))
        kb.row(*row_btns)
    if selected:
        kb.row(InlineKeyboardButton(text="⬆️", callback_data="gup"))
        kb.row(InlineKeyboardButton(text="⬅️", callback_data="glft"), InlineKeyboardButton(text="👁", callback_data="gvis"), InlineKeyboardButton(text="➡️", callback_data="grgt"))
        kb.row(InlineKeyboardButton(text="⬇️", callback_data="gdn"))
    kb.row(InlineKeyboardButton(text="💾 ذخیره", callback_data=f"gsav_{panel_type}"), InlineKeyboardButton(text="🔄 ریست", callback_data=f"grst_{panel_type}"), InlineKeyboardButton(text="❌ لغو", callback_data="gcnl"))
    return kb.as_markup()
