import time
import aiohttp
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton,
)

router = Router()

COINS = {
    "bitcoin":       ("₿ بیت‌کوین", "BTC"),
    "ethereum":      ("⟠ اتریوم", "ETH"),
    "tether":        ("₮ تتر", "USDT"),
    "tron":          ("◎ ترون", "TRX"),
    "toncoin":       ("💎 تون‌کوین", "TON"),
    "binancecoin":   ("🟡 بایننس", "BNB"),
    "solana":        ("◉ سولانا", "SOL"),
    "ripple":        ("✕ ریپل", "XRP"),
    "dogecoin":      ("🐕 دوج‌کوین", "DOGE"),
    "cardano":       ("₳ کاردانو", "ADA"),
    "shiba-inu":     ("🔥 شیبا", "SHIB"),
    "litecoin":      ("🥈 لایت‌کوین", "LTC"),
    "polygon":       ("🟣 پالیگان", "MATIC"),
    "the-open-network": ("💎 گرام", "GRAM"),
}

SYM_TO_ID = {}
for _cid, (_label, _sym) in COINS.items():
    SYM_TO_ID[_sym.lower()] = _cid

PRICE_CACHE = {"data": None, "ts": 0}


async def fetch_crypto():
    now = time.time()
    if PRICE_CACHE["data"] and now - PRICE_CACHE["ts"] < 30:
        return PRICE_CACHE["data"]

    ids = ",".join(COINS.keys())
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd,eur,irt&include_24hr_change=true"
        f"&include_24hr_vol=true&include_market_cap=true"
    )
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status != 200:
                raise Exception(f"HTTP {r.status}")
            data = await r.json()

    PRICE_CACHE["data"] = data
    PRICE_CACHE["ts"] = now
    return data


def fmt_crypto(data):
    lines = ["💰 قیمت لحظه‌ای ارزهای دیجیتال\n"]
    for cid, (label, sym) in COINS.items():
        if cid not in data:
            continue
        p = data[cid].get("usd", 0)
        c = data[cid].get("usd_24h_change", 0) or 0
        vol = data[cid].get("usd_24h_vol", 0) or 0
        e = "🟢" if c >= 0 else "🔴"
        pf = f"${p:,.6f}" if p < 1 else f"${p:,.2f}"
        lines.append(f"{label} ({sym})")
        lines.append(f"  💵 {pf}  {e} {c:+.2f}%\n")
    lines.append("📡 منبع: CoinGecko | کش ۳۰ ثانیه")
    return "\n".join(lines)


def fmt_single(data, cid):
    if cid not in data:
        return "❌ ارز پیدا نشد"
    label, sym = COINS.get(cid, ("?", "?"))
    p = data[cid].get("usd", 0)
    c = data[cid].get("usd_24h_change", 0) or 0
    vol = data[cid].get("usd_24h_vol", 0) or 0
    mcap = data[cid].get("usd_market_cap", 0) or 0
    irt = data[cid].get("irt")
    e = "🟢" if c >= 0 else "🔴"
    pf = f"${p:,.6f}" if p < 1 else f"${p:,.2f}"
    text = (
        f"{label} ({sym})\n\n"
        f"💵 قیمت: {pf}\n"
        f"{e} تغییر ۲۴ ساعته: {c:+.2f}%\n"
        f"📊 حجم معاملات: ${vol:,.0f}\n"
        f"💰 ارزش بازار: ${mcap:,.0f}\n"
    )
    if irt:
        text += f"🇮🇷 قیمت تومان: {irt:,.0f} تومان\n"
    return text


def cryp_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="cryp_ref")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


def single_kb(cid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data=f"cryp_one_{cid}")],
        [InlineKeyboardButton(text="📊 همه ارزها", callback_data="tool_crypto")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="tools_menu")],
    ])


@router.callback_query(F.data == "tool_crypto")
async def crypto_menu(cb: CallbackQuery):
    await cb.answer("⏳ دریافت قیمت‌ها...")
    try:
        data = await fetch_crypto()
        txt = fmt_crypto(data)
    except Exception as ex:
        txt = f"❌ خطا: {ex}"
    await cb.message.edit_text(txt, reply_markup=cryp_kb())


@router.callback_query(F.data == "cryp_ref")
async def crypto_ref(cb: CallbackQuery):
    await cb.answer("⏳ بروزرسانی...")
    try:
        data = await fetch_crypto()
        txt = fmt_crypto(data)
    except Exception as ex:
        txt = f"❌ خطا: {ex}"
    await cb.message.edit_text(txt, reply_markup=cryp_kb())


@router.callback_query(F.data.startswith("cryp_one_"))
async def crypto_single(cb: CallbackQuery):
    cid = cb.data.replace("cryp_one_", "")
    await cb.answer("⏳ ...")
    try:
        data = await fetch_crypto()
        txt = fmt_single(data, cid)
    except Exception as ex:
        txt = f"❌ خطا: {ex}"
    await cb.message.edit_text(txt, reply_markup=single_kb(cid))


@router.inline_query()
async def inline_crypto(query: InlineQuery):
    text = query.query.strip().lower()
    results = []
    try:
        data = await fetch_crypto()
    except:
        await query.answer(results=[], switch_pm_text="❌ خطا", switch_pm_parameter="err")
        return

    if not text:
        top = ["bitcoin", "ethereum", "tether", "tron", "toncoin"]
        for cid in top:
            if cid not in data: continue
            label, sym = COINS[cid]
            p = data[cid].get("usd", 0)
            c = data[cid].get("usd_24h_change", 0) or 0
            e = "🟢" if c >= 0 else "🔴"
            pf = f"${p:,.6f}" if p < 1 else f"${p:,.2f}"
            results.append(InlineQueryResultArticle(
                id=f"top_{cid}", title=f"{label} ({sym})",
                description=f"{pf}  {e} {c:+.2f}%",
                input_message_content=InputTextMessageContent(
                    message_text=f"💰 {label} ({sym})\n\n💵 {pf}\n{e} {c:+.2f}%\n\n📡 CoinGecko",
                ),
            ))
    elif text in SYM_TO_ID:
        cid = SYM_TO_ID[text]
        label, sym = COINS[cid]
        p = data[cid].get("usd", 0)
        c = data[cid].get("usd_24h_change", 0) or 0
        vol = data[cid].get("usd_24h_vol", 0) or 0
        e = "🟢" if c >= 0 else "🔴"
        pf = f"${p:,.6f}" if p < 1 else f"${p:,.2f}"
        results.append(InlineQueryResultArticle(
            id=f"one_{cid}", title=f"{label} ({sym})",
            description=f"{pf}  {e} {c:+.2f}%",
            input_message_content=InputTextMessageContent(
                message_text=f"💰 {label} ({sym})\n\n💵 {pf}\n{e} {c:+.2f}%\n📊 ${vol:,.0f}\n\n📡 CoinGecko",
            ),
        ))
    else:
        for cid, (label, sym) in COINS.items():
            if text in sym.lower() or text in cid or text in label.lower():
                if cid not in data: continue
                p = data[cid].get("usd", 0)
                c = data[cid].get("usd_24h_change", 0) or 0
                e = "🟢" if c >= 0 else "🔴"
                pf = f"${p:,.6f}" if p < 1 else f"${p:,.2f}"
                results.append(InlineQueryResultArticle(
                    id=f"s_{cid}", title=f"{label} ({sym})",
                    description=f"{pf}  {e} {c:+.2f}%",
                    input_message_content=InputTextMessageContent(
                        message_text=f"💰 {label} ({sym})\n\n💵 {pf}\n{e} {c:+.2f}%\n\n📡 CoinGecko",
                    ),
                ))

    if not results:
        results.append(InlineQueryResultArticle(
            id="notfound", title="❌ پیدا نشد",
            description=f"«{text}» — نماد ارز رو انگلیسی وارد کن (btc, eth, usdt, trx, ton)",
            input_message_content=InputTextMessageContent(
                message_text="❌ ارز پیدا نشد.\nنماد: btc, eth, usdt, trx, ton, bnb, sol, xrp, doge, ..."
            ),
        ))
    await query.answer(results[:50], cache_time=30, is_personal=False)
