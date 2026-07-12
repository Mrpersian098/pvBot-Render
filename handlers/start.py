import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database import add_user, get_setting, is_admin, get_force_channels, get_anon_link_by_code, is_anon_blocked
from states import UserStates
from keyboards import build_panel_keyboard, force_join_check_kb

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    await add_user(user.id, user.username, user.first_name)
    args = message.text.split()

    if len(args) > 1:
        code = args[1]
        link = await get_anon_link_by_code(code)
        if link:
            if not link["is_active"]:
                inactive_text = await get_setting("inactive_link_text")
                await message.answer(inactive_text)
                return
            if await is_anon_blocked(link["owner_id"], user.id):
                await message.answer("⛔ شما بلاک شده‌اید.")
                return
            await state.set_state(UserStates.anon_send)
            await state.update_data(anon_code=code, anon_owner=link["owner_id"])
            await message.answer("🔒 شما در حالت ارسال پیام ناشناس هستید.\nپیام خود را بنویسید:")
            return

    channels = await get_force_channels()
    if channels and not await is_admin(user.id):
        not_joined = []
        for ch in channels:
            try:
                member = await message.bot.get_chat_member(chat_id=ch["channel_id"], user_id=user.id)
                if member.status in ("left", "kicked"):
                    not_joined.append(ch)
            except:
                continue
        if not_joined:
            await message.answer(await get_setting("force_join_text"), reply_markup=force_join_check_kb(not_joined))
            return

    if await is_admin(user.id):
        welcome = await get_setting("welcome_text")
        panel = await build_panel_keyboard("user")
        await message.answer(welcome, reply_markup=panel)
        await message.answer("🛡️ شما ادمین هستید.\nبرای دسترسی به پنل مدیریت دستور /panel را ارسال کنید.")
    else:
        welcome = await get_setting("welcome_text")
        panel = await build_panel_keyboard("user")
        await message.answer(welcome, reply_markup=panel)


@router.message(Command("panel"))
async def cmd_panel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    panel = await build_panel_keyboard("admin")
    await message.answer("🛡️ <b>پنل مدیریت</b>", reply_markup=panel, parse_mode="HTML")


@router.callback_query(F.data == "check_join")
async def check_join_cb(callback: CallbackQuery):
    from database import get_force_channels
    channels = await get_force_channels()
    not_joined = []
    for ch in channels:
        try:
            member = await callback.bot.get_chat_member(chat_id=ch["channel_id"], user_id=callback.from_user.id)
            if member.status in ("left", "kicked"):
                not_joined.append(ch)
        except:
            continue
    if not_joined:
        await callback.message.edit_text(await get_setting("force_join_text"), reply_markup=force_join_check_kb(not_joined))
        await callback.answer("❌ هنوز عضو نشده‌اید!", show_alert=True)
    else:
        await callback.message.delete()
        panel = await build_panel_keyboard("user")
        await callback.message.answer(await get_setting("welcome_text"), reply_markup=panel)
        await callback.answer("✅ تایید شد!")


@router.callback_query(F.data == "back_to_panel")
async def back_to_panel(callback: CallbackQuery):
    if await is_admin(callback.from_user.id):
        panel = await build_panel_keyboard("admin")
        await callback.message.edit_text("🛡️ پنل مدیریت:", reply_markup=panel)
    else:
        panel = await build_panel_keyboard("user")
        await callback.message.edit_text("📋 منوی اصلی:", reply_markup=panel)


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if await is_admin(callback.from_user.id):
        panel = await build_panel_keyboard("admin")
        await callback.message.edit_text("🛡️ پنل مدیریت:", reply_markup=panel)
    else:
        panel = await build_panel_keyboard("user")
        await callback.message.edit_text("📋 منوی اصلی:", reply_markup=panel)
    await callback.answer("❌ لغو شد")


@router.callback_query(F.data == "noop")
async def noop_cb(callback: CallbackQuery):
    await callback.answer()
