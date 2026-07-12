import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AdminStates
from database import is_admin, get_setting, set_setting
from keyboards import admin_antispam_kb, cancel_kb, back_kb

logger = logging.getLogger(__name__)
router = Router()


async def show_antispam(m: Message):
    e = await get_setting("antispam_enabled")
    i = await get_setting("antispam_interval")
    l = await get_setting("antispam_limit")
    p = await get_setting("antispam_period")
    a = await get_setting("antispam_action")
    d = await get_setting("antispam_duration")
    await m.answer("🛡️ ضد اسپم:", reply_markup=admin_antispam_kb(e, i, l, p, a, d))


@router.callback_query(F.data == "adm_antispam")
async def adm_antispam(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    e = await get_setting("antispam_enabled")
    i = await get_setting("antispam_interval")
    l = await get_setting("antispam_limit")
    p = await get_setting("antispam_period")
    a = await get_setting("antispam_action")
    d = await get_setting("antispam_duration")
    await cb.message.edit_text("🛡️ ضد اسپم:", reply_markup=admin_antispam_kb(e, i, l, p, a, d))
    await cb.answer()


@router.callback_query(F.data == "antispam_toggle")
async def antispam_toggle(cb: CallbackQuery):
    cur = await get_setting("antispam_enabled")
    await set_setting("antispam_enabled", "0" if cur == "1" else "1")
    await adm_antispam(cb)
    await cb.answer("✅ تغییر کرد")


@router.callback_query(F.data == "antispam_toggle_action")
async def antispam_toggle_action(cb: CallbackQuery):
    cur = await get_setting("antispam_action")
    await set_setting("antispam_action", "ban" if cur == "mute" else "mute")
    await adm_antispam(cb)
    await cb.answer("✅ تغییر کرد")


@router.callback_query(F.data == "antispam_set_interval")
async def antispam_set_interval(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.antispam_interval)
    await cb.message.edit_text("⏱️ حداقل فاصله بین پیام‌ها (ثانیه):", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.antispam_interval, F.text)
async def antispam_interval_p(m: Message, state: FSMContext):
    try:
        val = float(m.text.strip())
        if val < 0.5: raise ValueError
    except ValueError:
        await m.answer("❌ حداقل 0.5 ثانیه.")
        return
    await set_setting("antispam_interval", str(val))
    await m.answer(f"✅ فاصله: {val} ثانیه", reply_markup=back_kb("adm_antispam"))
    await state.clear()


@router.callback_query(F.data == "antispam_set_limit")
async def antispam_set_limit(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.antispam_limit)
    await cb.message.edit_text("📊 حداکثر پیام در بازه:", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.antispam_limit, F.text)
async def antispam_limit_p(m: Message, state: FSMContext):
    try:
        val = int(m.text.strip())
        if val < 1: raise ValueError
    except ValueError:
        await m.answer("❌ حداقل 1.")
        return
    await set_setting("antispam_limit", str(val))
    await m.answer(f"✅ حداکثر: {val} پیام", reply_markup=back_kb("adm_antispam"))
    await state.clear()


@router.callback_query(F.data == "antispam_set_period")
async def antispam_set_period(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.antispam_period)
    await cb.message.edit_text("⏰ بازه شمارش (ثانیه):", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.antispam_period, F.text)
async def antispam_period_p(m: Message, state: FSMContext):
    try:
        val = float(m.text.strip())
        if val < 1: raise ValueError
    except ValueError:
        await m.answer("❌ حداقل 1 ثانیه.")
        return
    await set_setting("antispam_period", str(val))
    await m.answer(f"✅ بازه: {val} ثانیه", reply_markup=back_kb("adm_antispam"))
    await state.clear()


@router.callback_query(F.data == "antispam_set_duration")
async def antispam_set_duration(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.antispam_duration)
    await cb.message.edit_text("⏳ مدت محدودیت (ثانیه):", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.antispam_duration, F.text)
async def antispam_duration_p(m: Message, state: FSMContext):
    try:
        val = float(m.text.strip())
        if val < 10: raise ValueError
    except ValueError:
        await m.answer("❌ حداقل 10 ثانیه.")
        return
    await set_setting("antispam_duration", str(val))
    await m.answer(f"✅ مدت: {val} ثانیه", reply_markup=back_kb("adm_antispam"))
    await state.clear()
