import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AdminStates
from database import (
    is_admin, get_all_panel_buttons, get_button_configs,
    toggle_button_visibility, update_button_config, reset_button_configs,
    add_custom_button, remove_custom_button, get_custom_buttons,
    get_setting, set_setting,
)
from keyboards import admin_buttons_kb, graph_editor_kb, cancel_kb, back_kb

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "adm_buttons")
async def adm_buttons(cb: CallbackQuery):
    if not await is_admin(cb.from_user.id): return
    await cb.message.edit_text("🔧 مدیریت دکمه‌ها:", reply_markup=admin_buttons_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("graph_edit_"))
async def graph_edit_start(cb: CallbackQuery):
    pt = cb.data.replace("graph_edit_", "")
    buttons = await get_all_panel_buttons(pt)
    await cb.message.edit_text(f"🎨 ویرایش {pt}:", reply_markup=graph_editor_kb(pt, buttons))
    await cb.answer()

@router.callback_query(F.data.startswith("gsel_"))
async def graph_select(cb: CallbackQuery):
    key = cb.data.replace("gsel_", "")
    pt = "user"
    buttons = await get_all_panel_buttons(pt)
    for b in buttons:
        if b["key"] == key:
            pt = "user" if any(x["key"] == key for x in await get_all_panel_buttons("user")) else "admin"
            break
    buttons = await get_all_panel_buttons(pt)
    await cb.message.edit_reply_markup(reply_markup=graph_editor_kb(pt, buttons, selected=key))
    await cb.answer()

@router.callback_query(F.data == "gup")
async def graph_up(cb: CallbackQuery):
    await cb.answer("⬆️")

@router.callback_query(F.data == "gdn")
async def graph_down(cb: CallbackQuery):
    await cb.answer("⬇️")

@router.callback_query(F.data == "glft")
async def graph_left(cb: CallbackQuery):
    await cb.answer("⬅️")

@router.callback_query(F.data == "grgt")
async def graph_right(cb: CallbackQuery):
    await cb.answer("➡️")

@router.callback_query(F.data == "gvis")
async def graph_vis(cb: CallbackQuery):
    await cb.answer("👁")

@router.callback_query(F.data == "gcnl")
async def graph_cancel(cb: CallbackQuery):
    await cb.message.edit_text("🔧 مدیریت دکمه‌ها:", reply_markup=admin_buttons_kb())
    await cb.answer("❌ لغو")

@router.callback_query(F.data.startswith("gsav_"))
async def graph_save(cb: CallbackQuery):
    await cb.answer("💾 ذخیره شد")

@router.callback_query(F.data.startswith("grst_"))
async def graph_reset(cb: CallbackQuery):
    pt = cb.data.replace("grst_", "")
    await reset_button_configs(pt)
    buttons = await get_all_panel_buttons(pt)
    await cb.message.edit_reply_markup(reply_markup=graph_editor_kb(pt, buttons))
    await cb.answer("🔄 ریست شد")


@router.callback_query(F.data.startswith("btn_add_"))
async def btn_add_start(cb: CallbackQuery, state: FSMContext):
    pt = cb.data.replace("btn_add_", "")
    await state.set_state(AdminStates.add_btn_action)
    await state.update_data(btn_panel=pt)
    await cb.message.edit_text(
        f"➕ افزودن دکمه به پنل {pt}\n\n"
        "📝 متن دکمه رو بنویس:",
        reply_markup=cancel_kb(),
    )
    await cb.answer()

@router.message(AdminStates.add_btn_action, F.text)
async def btn_add_action(m: Message, state: FSMContext):
    d = await state.get_data()
    pt = d.get("btn_panel", "user")
    await state.update_data(btn_text=m.text.strip())
    await state.set_state(AdminStates.add_btn_panel)
    await m.answer("📄 متن یا اطلاعاتی که دکمه نشون بده:", reply_markup=cancel_kb())

@router.message(AdminStates.add_btn_panel, F.text)
async def btn_add_p(m: Message, state: FSMContext):
    d = await state.get_data()
    pt = d.get("btn_panel", "user")
    bt = d.get("btn_text", "دکمه")
    customs = await get_custom_buttons(pt)
    rn = max((c["row_number"] for c in customs), default=-1) + 1
    await add_custom_button(pt, bt, "send_message", m.text.strip(), rn, 0)
    await m.answer(f"✅ دکمه «{bt}» اضافه شد.", reply_markup=back_kb("adm_buttons"))
    await state.clear()


@router.callback_query(F.data.startswith("btn_reset_"))
async def btn_reset(cb: CallbackQuery):
    pt = cb.data.replace("btn_reset_", "")
    await reset_button_configs(pt)
    await cb.answer(f"🔄 پنل {pt} ریست شد", show_alert=True)


@router.callback_query(F.data.startswith("btn_panel_"))
async def btn_panel(cb: CallbackQuery):
    pt = cb.data.replace("btn_panel_", "")
    cur = await get_setting(f"panel_type_{pt}")
    new = "keyboard" if cur == "inline" else "inline"
    await set_setting(f"panel_type_{pt}", new)
    await cb.answer(f"🎨 نوع پنل {pt}: {new}", show_alert=True)
