from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from src.bot.handlers.mail import show_list
from src.bot.keyboards.mailbox_keyboard import (
    confirm_chpw,
    mail_detail,
    mail_list,
)
from src.config.settings import get_settings
from src.services.mailboxes import Mailboxes
from src.services.notletters_client import NotlettersApiError, NotlettersClient
from src.services.report_writer import dump_all, dump_updated

router = Router()


@router.callback_query(F.data.startswith("pw1:"))
async def ask_pw1(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    index = int(callback.data.split(":")[1])
    items = Mailboxes().all()
    if not 0 <= index < len(items):
        await callback.answer("Пропала")
        return
    email = items[index].email
    new_pw = get_settings().new_password
    await callback.message.edit_text(
        f"Сменить пароль {email} на {new_pw}?",
        reply_markup=confirm_chpw(str(index)),
    )
    await callback.answer()


@router.callback_query(F.data == "chpw")
async def ask_chpw(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    items = Mailboxes().all()
    if not items:
        await callback.answer("Список пуст")
        return
    new_pw = get_settings().new_password
    await callback.message.edit_text(
        f"Сменить пароль у {len(items)} шт на {new_pw}?",
        reply_markup=confirm_chpw("all"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("chpw_yes:"))
async def do_chpw(callback: CallbackQuery, notletters_client: NotlettersClient, state: FSMContext):
    await state.clear()
    target = callback.data.split(":")[1]
    new_pw = get_settings().new_password
    mb = Mailboxes()
    items = mb.all()

    if target == "all":
        pairs = [(m.email, m.password) for m in items]
    else:
        index = int(target)
        if not 0 <= index < len(items):
            await callback.answer("Пропала")
            return
        pairs = [(items[index].email, items[index].password)]

    await callback.message.edit_text("Меняю…")
    try:
        results = await notletters_client.change_passwords(pairs, new_pw)
    except NotlettersApiError as err:
        kb = mail_detail(0) if target != "all" else mail_list(mb.all())
        await callback.message.edit_text(f"Не вышло: {err}", reply_markup=kb)
        return

    ok = sum(1 for r in results if r.success)
    bad = len(results) - ok

    updated_path = dump_updated(results=results, new_password=new_pw)
    all_path = dump_all(original_accounts=pairs, results=results, new_password=new_pw)
    mb.update_passwords({r.email: new_pw for r in results if r.success})

    await callback.message.answer_document(FSInputFile(updated_path))
    await callback.message.answer_document(FSInputFile(all_path))

    if target == "all":
        await show_list(callback)
    else:
        await callback.message.edit_text(
            f"Готово. Ок: {ok}, косяк: {bad}",
            reply_markup=mail_detail(int(target)),
        )
