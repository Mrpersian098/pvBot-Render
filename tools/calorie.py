from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import cancel_kb, back_kb

router = Router()


class CalState(StatesGroup):
    food = State()


FOODS = {
    "برنج": 130, "نان": 265, "مرغ": 239, "گوشت": 250, "ماهی": 206,
    "تخم‌مرغ": 155, "شیر": 42, "ماست": 59, "پنیر": 264, "کره": 717,
    "سیب": 52, "موز": 89, "پرتقال": 47, "انگور": 69, "هندوانه": 30,
    "سیب‌زمینی": 77, "گوجه": 18, "خیار": 16, "کاهو": 15, "هویج": 41,
    "ماکارونی": 131, "پیتزا": 266, "همبرگر": 295, "سوسیس": 277,
    "بستنی": 207, "شکلات": 546, "کیک": 257, "عسل": 304, "مربا": 250,
    "آجیل": 607, "گردو": 654, "بادام": 579, "پسته": 560,
    "عدس": 116, "لوبیا": 127, "نخود": 164, "جو": 389,
    "دوغ": 23, "نوشابه": 41, "آبمیوه": 45, "چای": 1, "قهوه": 2,
}


@router.callback_query(F.data == "tool_calorie")
async def calorie_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(CalState.food)
    await cb.message.edit_text(
        "🍎 شمارش کالری\n\n"
        "نوع غذا رو بنویسید:\n\n"
        "غذاهای موجود:\n"
        f"{', '.join(list(FOODS.keys())[:20])}...\n\n"
        "یا مقدار کالری در ۱۰۰ گرم رو بنویسید.",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


@router.message(CalState.food, F.text)
async def calorie_process(m: Message, state: FSMContext):
    await state.clear()
    food = m.text.strip()
    if food in FOODS:
        cal = FOODS[food]
        await m.answer(
            f"🍎 <b>{food}</b>\n\n"
            f"📊 کالری در ۱۰۰ گرم: <code>{cal}</code> kcal\n"
            f"📊 کالری در ۲۰۰ گرم: <code>{cal * 2}</code> kcal\n"
            f"📊 کالری در ۳۰۰ گرم: <code>{cal * 3}</code> kcal\n"
            f"📊 کالری در ۵۰۰ گرم: <code>{cal * 5}</code> kcal",
            reply_markup=back_kb("tools_menu"), parse_mode="HTML",
        )
    else:
        try:
            cal = float(food)
            await m.answer(
                f"🍎 غذای سفارشی\n\n"
                f"📊 کالری در ۱۰۰ گرم: <code>{cal}</code> kcal\n"
                f"📊 کالری در ۲۰۰ گرم: <code>{cal * 2}</code> kcal\n"
                f"📊 کالری در ۵۰۰ گرم: <code>{cal * 5}</code> kcal",
                reply_markup=back_kb("tools_menu"), parse_mode="HTML",
            )
        except ValueError:
            await m.answer(
                f"❌ «{food}» پیدا نشد.\n\n"
                f"غذاهای موجود:\n{', '.join(list(FOODS.keys())[:30])}",
                reply_markup=back_kb("tools_menu"),
            )
