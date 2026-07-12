import aiohttp
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_kb, back_kb

router = Router()


class UrlState(StatesGroup):
    wait = State()


@router.callback_query(F.data == "tool_shorturl")
async def shorturl_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UrlState.wait)
    await cb.message.edit_text("🔗 لینک کوتاه کننده\n\nلینک خود را بفرستید:", reply_markup=cancel_kb())
    await cb.answer()


@router.message(UrlState.wait, F.text)
async def shorturl_process(m: Message, state: FSMContext):
    await state.clear()
    url = m.text.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"https://tinyurl.com/api-create.php?url={url}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as r:
                if r.status == 200:
                    short = await r.text()
                    await m.answer(
                        f"🔗 <b>لینک کوتاه شده:</b>\n\n"
                        f"📎 اصلی: <code>{url}</code>\n"
                        f"📎 کوتاه: <code>{short}</code>",
                        reply_markup=back_kb("tools_menu"), parse_mode="HTML",
                    )
                    return
    except:
        pass

    await m.answer(
        f"❌ خطا در کوتاه‌سازی لینک.\n\n"
        f"🔗 لینک: <code>{url}</code>\n"
        f"💡 لینک رو چک کنید و دوباره امتحان کنید.",
        reply_markup=back_kb("tools_menu"), parse_mode="HTML",
    )
