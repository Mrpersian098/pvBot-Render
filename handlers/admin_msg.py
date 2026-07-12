import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AdminStates
from database import is_admin, get_all_user_ids, get_user
from keyboards import admin_messaging_kb, cancel_kb, back_kb
from config import MAX_BROADCAST_BATCH

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "adm_messaging")
async def adm_messaging(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    await cb.message.edit_text("📨 ارسال پیام:", reply_markup=admin_messaging_kb())
    await cb.answer()


@router.callback_query(F.data == "msg_single")
async def msg_single(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.send_single_id)
    await cb.message.edit_text("📤 آیدی عددی کاربر:", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.send_single_id, F.text)
async def msg_single_id(m: Message, state: FSMContext):
    try:
        uid = int(m.text.strip())
    except ValueError:
        await m.answer("❌ آیدی نامعتبر."); return
    await state.update_data(target_id=uid)
    await state.set_state(AdminStates.send_single_msg)
    await m.answer(f"📨 پیام برای <code>{uid}</code>:", reply_markup=cancel_kb(), parse_mode="HTML")

@router.message(AdminStates.send_single_msg)
async def msg_single_send(m: Message, state: FSMContext):
    d = await state.get_data()
    tid = d.get("target_id")
    try:
        if m.text:
            await m.bot.send_message(tid, m.text)
        elif m.photo:
            await m.bot.send_photo(tid, m.photo[-1].file_id, caption=m.caption)
        elif m.video:
            await m.bot.send_video(tid, m.video.file_id, caption=m.caption)
        elif m.document:
            await m.bot.send_document(tid, m.document.file_id, caption=m.caption)
        else:
            await m.answer("❌ نوع پیام پشتیبانی نمیشه."); return
        await m.answer(f"✅ ارسال شد به {tid}", reply_markup=back_kb("adm_messaging"))
    except Exception as e:
        await m.answer(f"❌ خطا: {e}", reply_markup=back_kb("adm_messaging"))
    await state.clear()


@router.callback_query(F.data == "msg_broadcast")
async def msg_broadcast(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcast_msg)
    await cb.message.edit_text("📢 پیام همگانی:\n(هر نوع متن، عکس، ویدیو...)", reply_markup=cancel_kb())
    await cb.answer()

@router.message(AdminStates.broadcast_msg)
async def msg_broadcast_send(m: Message, state: FSMContext):
    uids = await get_all_user_ids()
    sent = 0
    failed = 0
    status = await m.answer(f"📢 ارسال به {len(uids)} کاربر...\n✅ {sent} | ❌ {failed}")
    for i, uid in enumerate(uids):
        try:
            if m.text:
                await m.bot.send_message(uid, m.text)
            elif m.photo:
                await m.bot.send_photo(uid, m.photo[-1].file_id, caption=m.caption)
            elif m.video:
                await m.bot.send_video(uid, m.video.file_id, caption=m.caption)
            elif m.document:
                await m.bot.send_document(uid, m.document.file_id, caption=m.caption)
            sent += 1
        except:
            failed += 1
        if (i + 1) % MAX_BROADCAST_BATCH == 0:
            try:
                await status.edit_text(f"📢 ارسال...\n✅ {sent} | ❌ {failed}\n({i+1}/{len(uids)})")
            except:
                pass
            import asyncio
            await asyncio.sleep(1)
    await status.edit_text(f"📢 ارسال تمام شد!\n✅ {sent} | ❌ {failed}\n({len(uids)} کاربر)")
    await state.clear()
