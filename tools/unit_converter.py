from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_kb

router = Router()


class ConvState(StatesGroup):
    wait = State()


UNITS = {
    "متر": 1, "m": 1, "سانتی‌متر": 0.01, "cm": 0.01,
    "میلی‌متر": 0.001, "mm": 0.001, "کیلومتر": 1000, "km": 1000,
    "مایل": 1609.344, "mile": 1609.344, "فوت": 0.3048, "ft": 0.3048,
    "اینچ": 0.0254, "inch": 0.0254, "یارد": 0.9144, "yard": 0.9144,
    "کیلوگرم": 1000, "kg": 1000, "کیلو": 1000,
    "گرم": 1, "g": 1, "میلی‌گرم": 0.001, "mg": 0.001,
    "پوند": 453.592, "lb": 453.592, "اونس": 28.3495, "oz": 28.3495,
    "تن": 1_000_000, "ton": 1_000_000,
    "لیتر": 1000, "l": 1000, "میلی‌لیتر": 1, "ml": 1,
    "گالن": 3785.41, "gal": 3785.41, "فنجان": 236.588, "cup": 236.588,
    "سلسیوس": "C", "celsius": "C", "سانتیگراد": "C",
    "فارنهایت": "F", "fahrenheit": "F",
    "کلوین": "K", "kelvin": "K",
}

FA_NAMES = {
    "متر": "متر", "سانتی‌متر": "سانتی‌متر", "میلی‌متر": "میلی‌متر",
    "کیلومتر": "کیلومتر", "مایل": "مایل", "فوت": "فوت", "اینچ": "اینچ",
    "یارد": "یارد", "کیلوگرم": "کیلوگرم", "گرم": "گرم", "میلی‌گرم": "میلی‌گرم",
    "پوند": "پوند", "اونس": "اونس", "تن": "تن", "لیتر": "لیتر",
    "میلی‌لیتر": "میلی‌لیتر", "گالن": "گالن", "فنجان": "فنجان",
    "سلسیوس": "سلسیوس", "فارنهایت": "فارنهایت", "کلوین": "کلوین",
}


def convert_temp(val, fr, to):
    if fr == "C": c = val
    elif fr == "F": c = (val - 32) * 5 / 9
    else: c = val - 273.15
    if to == "C": return c
    elif to == "F": return c * 9 / 5 + 32
    else: return c + 273.15


@router.callback_query(F.data == "tool_unit")
async def unit_menu(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ConvState.wait)
    msg = await cb.message.edit_text(
        "📐 تبدیل واحدها\n\n"
        "فرمت: مقدار واحد_مبدا واحد_مقصد\n\n"
        "مثال:\n"
        "• 100 کیلومتر مایل\n"
        "• 70 کیلوگرم پوند\n"
        "• 100 فارنهایت سلسیوس\n\n"
        "📏 طول | ⚖️ وزن | 📦 حجم | 🌡️ دما",
        reply_markup=cancel_kb()
    )
    await state.update_data(inst_msg_id=msg.message_id)
    await cb.answer()


@router.message(ConvState.wait)
async def do_convert(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    try:
        await message.bot.delete_message(message.chat.id, data.get("inst_msg_id", 0))
    except:
        pass

    parts = message.text.strip().split()
    if len(parts) < 3:
        await message.answer("❌ فرمت: مقدار واحد_مبدا واحد_مقصد\nمثال: 100 کیلومتر مایل")
        return

    try:
        val = float(parts[0].replace(",", "").replace("٫", "."))
    except ValueError:
        await message.answer("❌ مقدار باید عدد باشه")
        return

    fu = UNITS.get(parts[1])
    tu = UNITS.get(parts[2])
    if fu is None:
        await message.answer(f"❌ واحد «{parts[1]}» شناخته نشد")
        return
    if tu is None:
        await message.answer(f"❌ واحد «{parts[2]}» شناخته نشد")
        return

    if isinstance(fu, str) and isinstance(tu, str):
        result = convert_temp(val, fu, tu)
        fn = FA_NAMES.get(parts[1], parts[1])
        tn = FA_NAMES.get(parts[2], parts[2])
        await message.answer(f"🌡️ نتیجه:\n\n📥 {val:,.2f} {fn}\n📤 {result:,.2f} {tn}")
        return

    if type(fu) != type(tu):
        await message.answer("❌ این دو واحد از دسته‌های مختلفن")
        return

    result = val * fu / tu
    fn = FA_NAMES.get(parts[1], parts[1])
    tn = FA_NAMES.get(parts[2], parts[2])
    await message.answer(f"📐 نتیجه:\n\n📥 {val:,.4f} {fn}\n📤 {result:,.4f} {tn}")
