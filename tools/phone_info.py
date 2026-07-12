import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_kb, back_kb

router = Router()


class PhoneState(StatesGroup):
    wait = State()


BRANDS = {
    "apple": "Apple", "samsung": "Samsung",
    "xiaomi": "Xiaomi", "huawei": "Huawei",
    "oppo": "OPPO", "vivo": "Vivo",
    "oneplus": "OnePlus", "realme": "Realme",
    "nokia": "Nokia", "sony": "Sony",
    "lg": "LG", "motorola": "Motorola",
    "google": "Google", "nothing": "Nothing",
    "honor": "Honor", "tecno": "Tecno",
    "itel": "Itel", "infinix": "Infinix",
    "asus": "Asus", "lenovo": "Lenovo",
    "poco": "POCO", "redmi": "Redmi",
}


@router.callback_query(F.data == "tool_phone")
async def phone_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(PhoneState.wait)
    await cb.message.edit_text(
        "📱 اطلاعات گوشی\n\n"
        "نام یا مدل گوشی رو بنویسید:\n"
        "(مثال: Samsung Galaxy S24 Ultra)",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


@router.message(PhoneState.wait, F.text)
async def phone_process(m: Message, state: FSMContext):
    await state.clear()
    query = m.text.strip().lower()

    found_brand = None
    for key, name in BRANDS.items():
        if key in query:
            found_brand = name
            break

    text = f"📱 <b>جستجو: {m.text.strip()}</b>\n\n"
    if found_brand:
        text += f"🏷️ برند: {found_brand}\n"
    else:
        text += "🏷️ برند: ناشناس\n"

    text += (
        f"\n🔍 مدل: {m.text.strip()}\n\n"
        f"💡 برای اطلاعات دقیق، نام کامل مدل رو بنویسید.\n"
        f"مثال: Samsung Galaxy S24 Ultra 256GB\n\n"
        f"⚠️ این ابزار اطلاعات عمومی نشون میده.\n"
        f"برای مشخصات دقیق، سایت gsmarena.com رو چک کنید."
    )
    await m.answer(text, reply_markup=back_kb("tools_menu"), parse_mode="HTML")
