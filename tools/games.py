import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


def game_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="game_dice"), InlineKeyboardButton(text="🪙 شیر یا خط", callback_data="game_coin")],
        [InlineKeyboardButton(text="🔢 عدد تصادفی", callback_data="game_random"), InlineKeyboardButton(text="✊ سنگ کاغذ قیچی", callback_data="game_rps")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


@router.callback_query(F.data == "tool_games")
async def games_menu(cb: CallbackQuery):
    await cb.message.edit_text("🎮 <b>بازی‌ها</b>", reply_markup=game_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "game_dice")
async def game_dice(cb: CallbackQuery):
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    await cb.message.edit_text(
        f"🎲 <b>نتیجه تاس:</b>\n\n"
        f"تاس ۱: {d1}\n"
        f"تاس ۲: {d2}\n"
        f"مجموع: {d1 + d2}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 دوباره", callback_data="game_dice")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tool_games")],
        ]),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "game_coin")
async def game_coin(cb: CallbackQuery):
    result = random.choice(["شیر 🦁", "خط 📜"])
    await cb.message.edit_text(
        f"🪙 <b>شیر یا خط:</b>\n\n{result}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 دوباره", callback_data="game_coin")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tool_games")],
        ]),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "game_random")
async def game_random(cb: CallbackQuery):
    num = random.randint(1, 100)
    await cb.message.edit_text(
        f"🔢 <b>عدد تصادفی (۱ تا ۱۰۰):</b>\n\n<code>{num}</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 دوباره", callback_data="game_random")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tool_games")],
        ]),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "game_rps")
async def game_rps(cb: CallbackQuery):
    choice = random.choice(["✊ سنگ", "📄 کاغذ", "✌️ قیچی"])
    await cb.message.edit_text(
        f"✊ <b>سنگ کاغذ قیچی:</b>\n\n{choice}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 دوباره", callback_data="game_rps")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tool_games")],
        ]),
        parse_mode="HTML",
    )
    await cb.answer()
