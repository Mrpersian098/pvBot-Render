import io
import uuid
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from states import UserStates
from database import (
    get_user_anon_links, create_anon_link, delete_anon_link,
    toggle_anon_link, get_setting, get_custom_buttons,
)
from keyboards import (
    tools_menu_kb, anon_links_kb, anon_detail_kb,
    password_level_kb, cancel_kb, back_kb, build_panel_keyboard,
)
from utils import image_to_pdf, convert_image, generate_qr, generate_password

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "my_links")
async def my_links_cb(callback: CallbackQuery):
    links = await get_user_anon_links(callback.from_user.id)
    text = "🔗 <b>لینک‌های ناشناس شما:</b>\n\n"
    if not links:
        text += "هنوز لینکی نساخته‌اید."
    else:
        for link in links:
            s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
            text += f"• <code>{link['link_code']}</code> — {s} — {link['message_count']} پیام\n"
    await callback.message.edit_text(text, reply_markup=anon_links_kb(links), parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "🔗 لینک ناشناس من")
async def my_links_text(message: Message):
    links = await get_user_anon_links(message.from_user.id)
    text = "🔗 <b>لینک‌های ناشناس شما:</b>\n\n"
    if not links:
        text += "هنوز لینکی نساخته‌اید."
    else:
        for link in links:
            s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
            text += f"• <code>{link['link_code']}</code> — {s} — {link['message_count']} پیام\n"
    await message.answer(text, reply_markup=anon_links_kb(links), parse_mode="HTML")


@router.callback_query(F.data == "create_anon_link")
async def create_link(callback: CallbackQuery):
    code = uuid.uuid4().hex[:8]
    bot_username = (await callback.bot.me()).username
    await create_anon_link(callback.from_user.id, code)
    link = f"https://t.me/{bot_username}?start={code}"
    await callback.message.edit_text(
        f"✅ لینک ناشناس شما ساخته شد:\n\n🔗 <code>{link}</code>",
        reply_markup=back_kb("my_links"), parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("anon_detail_"))
async def anon_detail(callback: CallbackQuery):
    code = callback.data.replace("anon_detail_", "")
    links = await get_user_anon_links(callback.from_user.id)
    link = next((l for l in links if l["link_code"] == code), None)
    if not link:
        await callback.answer("❌ یافت نشد!", show_alert=True)
        return
    s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
    last = link.get("last_used") or "هرگز"
    bot_username = (await callback.bot.me()).username
    await callback.message.edit_text(
        f"🔗 <b>جزئیات لینک</b>\n\n"
        f"کد: <code>{code}</code>\n"
        f"لینک: <code>https://t.me/{bot_username}?start={code}</code>\n"
        f"وضعیت: {s}\nپیام: {link['message_count']}\nآخرین استفاده: {last}",
        reply_markup=anon_detail_kb(code, link["is_active"]), parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("anon_toggle_"))
async def anon_toggle(callback: CallbackQuery):
    code = callback.data.replace("anon_toggle_", "")
    await toggle_anon_link(code)
    await callback.answer("✅ تغییر کرد")
    links = await get_user_anon_links(callback.from_user.id)
    link = next((l for l in links if l["link_code"] == code), None)
    if link:
        s = "🟢 فعال" if link["is_active"] else "🔴 غیرفعال"
        last = link.get("last_used") or "هرگز"
        bot_username = (await callback.bot.me()).username
        await callback.message.edit_text(
            f"🔗 <b>جزئیات لینک</b>\n\n"
            f"کد: <code>{code}</code>\n"
            f"لینک: <code>https://t.me/{bot_username}?start={code}</code>\n"
            f"وضعیت: {s}\nپیام: {link['message_count']}\nآخرین استفاده: {last}",
            reply_markup=anon_detail_kb(code, link["is_active"]), parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("anon_delete_"))
async def anon_delete(callback: CallbackQuery):
    code = callback.data.replace("anon_delete_", "")
    await delete_anon_link(code)
    await callback.answer("🗑 حذف شد")
    await my_links_cb(callback)


@router.callback_query(F.data == "send_anon_to_admin")
async def send_to_admin_cb(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.anon_send)
    await state.update_data(anon_code=None, anon_owner=None)
    await callback.message.edit_text("📨 پیام خود را بنویسید (هر نوع فایل، متن، عکس، ویدیو و...):", reply_markup=cancel_kb())
    await callback.answer()


@router.message(F.text == "📨 ارسال پیام به ادمین")
async def send_to_admin_text(message: Message, state: FSMContext):
    await state.set_state(UserStates.anon_send)
    await state.update_data(anon_code=None, anon_owner=None)
    await message.answer("📨 پیام خود را بنویسید (هر نوع فایل، متن، عکس، ویدیو و...):", reply_markup=cancel_kb())


@router.callback_query(F.data == "tools_menu")
async def tools_menu_cb(callback: CallbackQuery):
    await callback.message.edit_text("🔧 <b>ابزارها</b>", reply_markup=tools_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "🔧 ابزارها")
async def tools_menu_text(message: Message):
    await message.answer("🔧 <b>ابزارها</b>", reply_markup=tools_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "tool_img2pdf")
async def tool_img2pdf_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.image_to_pdf)
    await callback.message.edit_text("🖼️ عکس خود را ارسال کنید:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(UserStates.image_to_pdf, F.photo | F.document)
async def tool_img2pdf_process(message: Message, state: FSMContext):
    if message.photo:
        file = await message.bot.get_file(message.photo[-1].file_id)
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        file = await message.bot.get_file(message.document.file_id)
    else:
        await message.answer("❌ لطفاً یک تصویر ارسال کنید.")
        return
    buf = io.BytesIO()
    await message.bot.download_file(file.file_path, buf)
    pdf_bytes = await image_to_pdf(buf.getvalue())
    await message.answer_document(BufferedInputFile(pdf_bytes, filename="converted.pdf"), caption="✅ PDF آماده شد.")
    await state.clear()


@router.callback_query(F.data == "tool_convert")
async def tool_convert_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.file_convert)
    await callback.message.edit_text("🔄 تصویر را با کپشن فرمت مقصد بفرستید\n(png, jpg, webp, bmp)", reply_markup=cancel_kb())
    await callback.answer()


@router.message(UserStates.file_convert, F.photo | F.document)
async def tool_convert_process(message: Message, state: FSMContext):
    caption = (message.caption or "").strip().lower()
    if caption not in ("jpg", "jpeg", "png", "webp", "bmp"):
        await message.answer("❌ فرمت مقصد را در کپشن بنویسید")
        return
    if message.photo:
        file = await message.bot.get_file(message.photo[-1].file_id)
        src = "jpg"
    else:
        file = await message.bot.get_file(message.document.file_id)
        name = message.document.file_name or "img.jpg"
        src = name.rsplit(".", 1)[-1] if "." in name else "jpg"
    buf = io.BytesIO()
    await message.bot.download_file(file.file_path, buf)
    result = await convert_image(buf.getvalue(), src, caption)
    ext = caption if caption != "jpeg" else "jpg"
    await message.answer_document(BufferedInputFile(result, filename=f"converted.{ext}"), caption=f"✅ {src} → {ext}")
    await state.clear()


@router.callback_query(F.data == "tool_qr")
async def tool_qr_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.qr_input)
    await callback.message.edit_text("📊 متن یا لینک را بفرستید:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(UserStates.qr_input, F.text)
async def tool_qr_process(message: Message, state: FSMContext):
    img, raw = await generate_qr(message.text)
    await message.answer_photo(BufferedInputFile(img, filename="qr.png"), caption=f"✅ QR Code!\n<code>{raw}</code>", parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data == "tool_password")
async def tool_password_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.pass_length)
    await callback.message.edit_text("🔐 تعداد کاراکترها (4 تا 128):", reply_markup=cancel_kb())
    await callback.answer()


@router.message(UserStates.pass_length, F.text)
async def tool_password_length(message: Message, state: FSMContext):
    try:
        length = int(message.text)
        if not 4 <= length <= 128:
            raise ValueError
    except ValueError:
        await message.answer("❌ عدد بین 4 تا 128 وارد کنید.")
        return
    await state.update_data(pass_length=length)
    await message.answer("سطح رمز:", reply_markup=password_level_kb())


@router.callback_query(F.data.startswith("pass_"))
async def tool_password_generate(callback: CallbackQuery, state: FSMContext):
    level = callback.data.replace("pass_", "")
    data = await state.get_data()
    length = data.get("pass_length", 16)
    pw = generate_password(length, level)
    await callback.message.edit_text(
        f"🔐 <b>رمز عبور:</b>\n\n<code>{pw}</code>\n\nطول: {length} | سطح: {level}",
        parse_mode="HTML", reply_markup=back_kb("tools_menu"),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("custom_user_"))
async def custom_user_button(callback: CallbackQuery):
    btn_id = int(callback.data.replace("custom_user_", ""))
    buttons = await get_custom_buttons("user")
    btn = next((b for b in buttons if b["id"] == btn_id), None)
    if btn and btn["button_action"] == "send_message":
        await callback.message.answer(btn["button_data"] or "متنی تنظیم نشده.")
    await callback.answer()
