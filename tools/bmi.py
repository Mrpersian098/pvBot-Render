from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_kb, back_kb

router = Router()


class BmiState(StatesGroup):
    height = State()
    weight = State()


@router.callback_query(F.data == "tool_bmi")
async def bmi_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BmiState.height)
    await cb.message.edit_text("⚖️ محاسبه BMI\n\n📏 قد خود را به سانتی‌متر وارد کنید:\n(مثال: 175)", reply_markup=cancel_kb())
    await cb.answer()


@router.message(BmiState.height, F.text)
async def bmi_height(m: Message, state: FSMContext):
    try:
        h = float(m.text.strip())
        if not 50 <= h <= 250:
            raise ValueError
    except ValueError:
        await m.answer("❌ عدد بین 50 تا 250 سانتی‌متر وارد کنید.")
        return
    await state.update_data(height=h)
    await state.set_state(BmiState.weight)
    await m.answer("⚖️ وزن خود را به کیلوگرم وارد کنید:\n(مثال: 70)", reply_markup=cancel_kb())


@router.message(BmiState.weight, F.text)
async def bmi_weight(m: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        w = float(m.text.strip())
        if not 10 <= w <= 300:
            raise ValueError
    except ValueError:
        await m.answer("❌ عدد بین 10 تا 300 کیلوگرم وارد کنید.")
        return

    h = data["height"] / 100
    bmi = w / (h * h)

    if bmi < 18.5:
        cat = "🟡 کمبود وزن"
        tip = "تغذیه سالم و منظم داشته باشید."
    elif bmi < 25:
        cat = "🟢 وزن نرمال"
        tip = "عالی! سبک زندگی سالم رو ادامه بدید."
    elif bmi < 30:
        cat = "🟠 اضافه وزن"
        tip = "ورزش منظم و کاهش کالری توصیه میشه."
    else:
        cat = "🔴 چاقی"
        tip = "مراجعه به پزشک تغذیه توصیه میشه."

    ideal_min = 18.5 * (h ** 2)
    ideal_max = 24.9 * (h ** 2)

    await m.answer(
        f"⚖️ <b>نتیجه BMI</b>\n\n"
        f"📊 BMI: <code>{bmi:.1f}</code>\n"
        f"📋 دسته: {cat}\n"
        f"💡 {tip}\n\n"
        f"📏 وزن ایده‌آل: {ideal_min:.0f} - {ideal_max:.0f} کیلوگرم",
        reply_markup=back_kb("tools_menu"),
        parse_mode="HTML",
    )
