import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

QUOTES = [
    "هر روز شروع تازه‌ای است.",
    "موفقیت نتیجه تلاش مداوم است.",
    "بهترین زمان برای شروع، الان است.",
    "هر سختی آسانی در پی دارد.",
    "باور داشته باش، می‌تونی.",
    "بزرگ فکر کن، کوچک شروع کن.",
    "از اشتباهاتت یاد بگیر.",
    "صبر کلید موفقیت است.",
    "خودت رو با دیروزت مقایسه کن.",
    "هر قدم کوچک، یه پیشرفت بزرگه.",
    "زندگی کوتاه‌تر از آن است که نگران باشی.",
    "خوشبختی یک انتخاب است.",
    "امروز بهترین روز زندگیته.",
    "از منطقه امنت بیا بیرون.",
    "هر ناامیدی، شروع یه امید جدیده.",
    "تغییر از خودت شروع میشه.",
    "هدف داشته باش، راه پیدا میشه.",
    "قدردان چیزایی باش که داری.",
    "ترس، دشمن موفقیته.",
    "مثبت فکر کن، مثبت زندگی کن.",
]

FACTS = [
    "عسل هرگز فاسد نمیشه.",
    "ماه حدود ۳۸۴,۴۰۰ کیلومتر از زمین فاصله داره.",
    "مغز انسان حدود ۲۰٪ انرژی بدن رو مصرف میکنه.",
    "فیل‌ها تنها حیواناتی هستن که نمیتونن بپرن.",
    "سرعت نور ۳۰۰,۰۰۰ کیلومتر در ثانیه‌ست.",
    "آب داغ سریع‌تر از آب سرد یخ میزنه.",
    "قلب انسان روزی حدود ۱۰۰,۰۰۰ بار میزنه.",
    "ونوس تنها سیاره‌ای‌ست که در جهت عقربه‌های ساعت میچرخه.",
    "یک ابر به اندازه یک فیل وزن داره.",
    "حلزون میتونه ۳ سال بخوابه.",
]


def rand_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 یکی دیگه", callback_data="rand_again")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


@router.callback_query(F.data == "tool_random_text")
async def random_text(cb: CallbackQuery):
    items = random.choice([QUOTES, FACTS])
    text = random.choice(items)
    prefix = "💬" if items == QUOTES else "🧠"
    await cb.message.edit_text(f"{prefix} <b>{text}</b>", reply_markup=rand_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "rand_again")
async def rand_again(cb: CallbackQuery):
    items = random.choice([QUOTES, FACTS])
    text = random.choice(items)
    prefix = "💬" if items == QUOTES else "🧠"
    await cb.message.edit_text(f"{prefix} <b>{text}</b>", reply_markup=rand_kb(), parse_mode="HTML")
    await cb.answer()
