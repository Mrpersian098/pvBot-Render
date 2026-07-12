import jdatetime
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import back_kb

router = Router()


@router.callback_query(F.data == "tool_calendar")
async def calendar_menu(cb: CallbackQuery):
    now = datetime.now()
    jnow = jdatetime.datetime.now()

    day_names = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
    month_names = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]

    jd = jnow.day
    jm = month_names[jnow.month - 1]
    jy = jnow.year
    jday = day_names[jnow.weekday()]

    gd = now.day
    gm = now.strftime("%B")
    gy = now.year

    await cb.message.edit_text(
        f"📅 <b>تقویم شمسی</b>\n\n"
        f"🇮🇷 شمسی:\n"
        f"📆 {jday}، {jd} {jm} {jy}\n\n"
        f"🌍 میلادی:\n"
        f"📆 {gm} {gd}, {gy}\n\n"
        f"⏰ ساعت: {now.strftime('%H:%M:%S')}",
        reply_markup=back_kb("tools_menu"),
        parse_mode="HTML",
    )
    await cb.answer()
