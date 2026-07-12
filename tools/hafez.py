import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

HAFEZ_GHAZALS = [
    ("الا یا ایها الساقی ادر کأساً و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها", "خواجه حافظ شیرازی"),
    ("اگر آن ترک شیرازی به دست آرد دل ما را\nبه خال هندویش بخشم سمرقند و بخارا را", "خواجه حافظ شیرازی"),
    ("بشنو از نی چون حکایت می‌کند\nاز جدایی‌ها شکایت می‌کند", "مولانا"),
    ("دل می‌رود ز دستم صاحبدلان خدا را\nدردا که راز پنهان خواهد شد آشکارا", "خواجه حافظ شیرازی"),
    ("صبا به لطف بگو آن غزال رعنا را\nکه سر به کوه و بیابان تو نه به فکر ما را", "خواجه حافظ شیرازی"),
    ("مژده ای دل که مسیحا نفسی می‌آید\nکه ز انفاس خوشش بوی کسی می‌آید", "خواجه حافظ شیرازی"),
    ("مرا به رندی و عشق آن فضول عیب کند\nکه خود نه نکته‌ای از فضل می‌داند نه هنر", "خواجه حافظ شیرازی"),
    ("سال‌ها دل طلب جام جم از ما می‌کرد\nوان‌چه خود داشت ز بیگانه تمنا می‌کرد", "خواجه حافظ شیرازی"),
    ("بنی آدم اعضای یک پیکرند\nکه در آفرینش ز یک گوهرند", "سعدی شیرازی"),
    ("رسید مژده که آمد بهار و سبزه دمید\nوظیفه گر برسد مصرفش گل و نبید", "خواجه حافظ شیرازی"),
    ("دوش وقت سحر از غصه نجاتم دادند\nواندر آن ظلمت شب آب حیاتم دادند", "خواجه حافظ شیرازی"),
    ("بیا که قصر امل سخت سست بنیاد است\nبیار باده که بنیاد عمر بر باد است", "خواجه حافظ شیرازی"),
    ("خدا چو صورت ابروی دلگشای تو بست\nگشاد کار من اندر کرشمه‌های تو بست", "خواجه حافظ شیرازی"),
    ("غلام همت آنم که زیر چرخ کبود\nز هر چه رنگ تعلق پذیرد آزاد است", "خواجه حافظ شیرازی"),
    ("مزرع سبز فلک دیدم و داس مه نو\nیادم از کشته خویش آمد و هنگام درو", "خواجه حافظ شیرازی"),
    ("چو بشنوی سخن اهل دل مگو که خطاست\nسخن‌شناس نه‌ای جان من خطا این جاست", "خواجه حافظ شیرازی"),
    ("ز روی دوست دل دشمنان چه دریابد\nکسی که چشم بد دارد صفت نیکو ندارد", "خواجه حافظ شیرازی"),
    ("حدیث از مطرب و می‌گو و راز دهر کمتر جو\nکه کس نگشود و نگشاید به حکمت این معما را", "خواجه حافظ شیرازی"),
    ("خیال روی تو در هر طریق همره ماست\nنسیم موی تو پیوند جان آگه ماست", "خواجه حافظ شیرازی"),
    ("دل و دینم شد و دلبر به ملامت برخاست\nگفتا ما همه مصلحت اندیش جهانیم", "خواجه حافظ شیرازی"),
]

TAABIR = [
    "🌟 مژده! اتفاق خوبی در راه است.",
    "💫 صبر پیشه کن، نتیجه نزدیک است.",
    "🔑 راه حل مشکل در دستان توست.",
    "❤️ عشق و مهربانی تو را به هدف می‌رساند.",
    "🌅 پس از هر سختی، آسانی‌ست.",
    "🍀 شانس با تو یار است، از فرصت‌ها استفاده کن.",
    "🤲 توکل کن، خدا بهترین‌ها رو برات رقم میزنه.",
    "📚 علم و دانش کلید موفقیت توست.",
    "🤝 یه دوست خوب پیدا میکنی که تاثیر مثبتی داره.",
    "💪 قدرت درونی تو بیشتر از چیزی‌ست که فکر میکنی.",
    "🕊️ آرامش در راه است، نگران نباش.",
    "🌈 بعد از هر طوفانی، رنگین‌کمانی هست.",
    "💎 تو گرانبهاتر از چیزی هستی که فکر میکنی.",
    "🌺 زیبایی زندگی رو ببین، همه جا هست.",
    "🎯 به هدفت نزدیک شدی، ادامه بده.",
]

# ─── حافظه کاربران ───
user_history: dict[int, list[int]] = {}


def hafez_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔮 فال دیگر", callback_data="hafez_again")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


def _get_ghazal_index(uid: int) -> int:
    """یه ایندکس تصادفی برمیگردونه که قبلاً به این کاربر نشون داده نشده."""
    seen = user_history.get(uid, [])
    available = [i for i in range(len(HAFEZ_GHAZALS)) if i not in seen]

    # اگه همه رو دیده، ریست کن
    if not available:
        seen.clear()
        available = list(range(len(HAFEZ_GHAZALS)))

    idx = random.choice(available)
    seen.append(idx)
    user_history[uid] = seen
    return idx


@router.callback_query(F.data == "tool_hafez")
async def hafez_menu(cb: CallbackQuery):
    uid = cb.from_user.id
    idx = _get_ghazal_index(uid)
    ghazal, poet = HAFEZ_GHAZALS[idx]
    taabir = random.choice(TAABIR)
    seen = len(user_history.get(uid, []))
    total = len(HAFEZ_GHAZALS)

    await cb.message.edit_text(
        f"🔮 <b>فال حافظ</b>\n\n"
        f"📜 {ghazal}\n\n"
        f"✍️ {poet}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🔮 تعبیر:\n{taabir}\n\n"
        f"📋 فال {seen} از {total}",
        reply_markup=hafez_kb(), parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "hafez_again")
async def hafez_again(cb: CallbackQuery):
    uid = cb.from_user.id
    idx = _get_ghazal_index(uid)
    ghazal, poet = HAFEZ_GHAZALS[idx]
    taabir = random.choice(TAABIR)
    seen = len(user_history.get(uid, []))
    total = len(HAFEZ_GHAZALS)

    await cb.message.edit_text(
        f"🔮 <b>فال حافظ</b>\n\n"
        f"📜 {ghazal}\n\n"
        f"✍️ {poet}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🔮 تعبیر:\n{taabir}\n\n"
        f"📋 فال {seen} از {total}",
        reply_markup=hafez_kb(), parse_mode="HTML",
    )
    await cb.answer()
