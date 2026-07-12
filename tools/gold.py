import aiohttp
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


async def fetch_gold():
    url = "https://api.farmzone.ir/gold"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    return await r.json()
    except:
        pass
    return None


def gold_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="gold_ref")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


@router.callback_query(F.data == "tool_gold")
async def gold_menu(cb: CallbackQuery):
    await cb.answer("⏳ ...")
    data = await fetch_gold()
    if data:
        text = "🪙 <b>قیمت طلا و سکه:</b>\n\n"
        for item in data.get("results", data if isinstance(data, list) else [])[:10]:
            name = item.get("name", item.get("title", "?"))
            price = item.get("price", item.get("value", "?"))
            text += f"• {name}: {price}\n"
    else:
        text = "🪙 <b>قیمت طلا و سکه</b>\n\n⚠️ در حال حاضر امکان دریافت قیمت نیست.\nمنبع داده موقتا در دسترس نیست."
    await cb.message.edit_text(text, reply_markup=gold_kb(), parse_mode="HTML")


@router.callback_query(F.data == "gold_ref")
async def gold_ref(cb: CallbackQuery):
    await cb.answer("⏳ بروزرسانی...")
    data = await fetch_gold()
    if data:
        text = "🪙 <b>قیمت طلا و سکه:</b>\n\n"
        for item in data.get("results", data if isinstance(data, list) else [])[:10]:
            name = item.get("name", item.get("title", "?"))
            price = item.get("price", item.get("value", "?"))
            text += f"• {name}: {price}\n"
    else:
        text = "🪙 <b>قیمت طلا و سکه</b>\n\n⚠️ منبع داده در دسترس نیست."
    await cb.message.edit_text(text, reply_markup=gold_kb(), parse_mode="HTML")
