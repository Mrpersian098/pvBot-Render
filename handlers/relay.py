import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import UserStates
from database import (
    is_admin, get_setting, save_message, save_mapping, get_mapping,
    increment_messages, update_anon_link_usage, get_admin_ids, get_user,
    save_anon_message, is_anon_blocked,
)

logger = logging.getLogger(__name__)
router = Router()


async def _ctype(m):
    for t in ("text", "photo", "video", "document", "audio", "voice", "animation", "sticker", "video_note"):
        if getattr(m, t, None): return t
    return "unknown"


async def _fid(m):
    if m.photo: return m.photo[-1].file_id
    for a in ("video", "document", "audio", "voice", "animation", "sticker", "video_note"):
        o = getattr(m, a, None)
        if o: return o.file_id
    return ""


async def _send_to(bot, m, target):
    sent = None
    if m.text: sent = await bot.send_message(target, m.text)
    elif m.photo: sent = await bot.send_photo(target, m.photo[-1].file_id, caption=m.caption)
    elif m.video: sent = await bot.send_video(target, m.video.file_id, caption=m.caption)
    elif m.document: sent = await bot.send_document(target, m.document.file_id, caption=m.caption)
    elif m.audio: sent = await bot.send_audio(target, m.audio.file_id, caption=m.caption)
    elif m.voice: sent = await bot.send_voice(target, m.voice.file_id, caption=m.caption)
    elif m.animation: sent = await bot.send_animation(target, m.animation.file_id, caption=m.caption)
    elif m.sticker: sent = await bot.send_sticker(target, m.sticker.file_id)
    elif m.video_note: sent = await bot.send_video_note(target, m.video_note.file_id)
    return sent


async def _fwd_admins(bot, m, uid, is_anon=False, link_own=0):
    aids = await get_admin_ids()
    user = await get_user(uid)
    name = user.get("first_name", "ناشناس") if user else "ناشناس"
    at = await get_setting("admin_new_msg_text")
    header = at.format(user_name=name, user_id=uid)
    if is_anon:
        header = f'🔒 پیام ناشناس از <a href="tg://user?id={uid}">{name}</a> (ID: <code>{uid}</code>):'
    for aid in aids:
        if aid == uid: continue
        try:
            await bot.send_message(aid, header, parse_mode="HTML")
            sent = await _send_to(bot, m, aid)
            if sent:
                tgt = link_own if is_anon else uid
                await save_mapping(sent.message_id, aid, tgt, uid, 1 if is_anon else 0, link_own)
        except Exception as e:
            logger.error(f"ارسال به ادمین {aid}: {e}")


@router.message(UserStates.anon_send)
async def anon_handler(m: Message, state: FSMContext):
    d = await state.get_data()
    code = d.get("anon_code")
    owner = d.get("anon_owner")
    uid = m.from_user.id
    ct = await _ctype(m)
    fid = await _fid(m)
    text = m.text or m.caption or ""

    if code and owner:
        if await is_anon_blocked(owner, uid):
            await m.answer("⛔ شما بلاک شده‌اید."); return
        await save_message(uid, owner, ct, fid, text, is_anonymous=1)
        await save_anon_message(uid, owner, ct, text, fid, m.caption or "")
        await update_anon_link_usage(code)
        await _fwd_admins(m.bot, m, uid, True, owner)
        try:
            await m.bot.send_message(owner, "🔒 <b>پیام ناشناس جدید:</b>", parse_mode="HTML")
            await _send_to(m.bot, m, owner)
        except Exception as e:
            logger.error(f"ارسال به مالک لینک: {e}")
    else:
        await save_message(uid, 0, ct, fid, text)
        await _fwd_admins(m.bot, m, uid)

    await increment_messages(uid)


@router.message(F.reply_to_message, F.chat.type == "private")
async def reply_handler(m: Message):
    uid = m.from_user.id
    mapping = await get_mapping(m.reply_to_message.message_id, m.chat.id)
    if not mapping: return

    if await is_admin(uid):
        target = mapping["target_user_id"]
        try:
            await _send_to(m.bot, m, target)
            auto = await get_setting("auto_reply_text")
            await m.bot.send_message(target, auto)
            await m.answer("✅ ارسال شد.")
        except Exception as e:
            await m.answer(f"❌ خطا: {e}")
    else:
        target = mapping["link_owner_id"] if mapping["is_anonymous"] else mapping["original_user_id"]
        try:
            await _send_to(m.bot, m, target)
            await m.answer("✅ ارسال شد.")
        except Exception as e:
            await m.answer(f"❌ خطا: {e}")


@router.message(F.chat.type == "private")
async def user_relay(m: Message, state: FSMContext):
    cur = await state.get_state()
    if cur: return
    if await get_setting("bot_enabled") != "1": return
    uid = m.from_user.id
    if await is_admin(uid): return
    ct = await _ctype(m)
    fid = await _fid(m)
    text = m.text or m.caption or ""
    await save_message(uid, 0, ct, fid, text)
    await increment_messages(uid)
    await _fwd_admins(m.bot, m, uid)

    auto_reply = await get_setting("auto_reply_text")
    if auto_reply:
        try:
            await m.answer(auto_reply)
        except:
            pass
