from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.handlers.mail import show_list
from src.bot.keyboards.mailbox_keyboard import (
    PER_PAGE,
    confirm_del_all,
    mail_detail,
    mail_list,
)
from src.bot.states import AddAccount
from src.services.mailboxes import Mailboxes

router = Router()


@router.callback_query(F.data.startswith("del:"))
async def delete_mail(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    index = int(callback.data.split(":")[1])
    mb = Mailboxes()
    items = mb.all()
    if not 0 <= index < len(items):
        await callback.answer("Нет такой")
        return
    email = items[index].email
    mb.remove(email)
    await show_list(callback)
    await callback.answer(f"Убрал {email}")


@router.callback_query(F.data == "add")
async def ask_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddAccount.waiting_input)
    await callback.message.edit_text(
        "Отправь почта:пароль\nМожно несколько — каждая с новой строки",
        reply_markup=mail_detail(0),
    )
    await callback.answer()


@router.message(AddAccount.waiting_input)
async def do_add(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    mb = Mailboxes()
    for line in text.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        email, password = line.split(":", 1)
        email, password = email.strip(), password.strip()
        if email and password:
            mb.add(email, password)

    await state.clear()
    items = mb.all()
    page = max(0, (len(items) - 1) // PER_PAGE)
    await message.answer("Почты", reply_markup=mail_list(items, page))


@router.callback_query(F.data == "del_all")
async def ask_del_all(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    items = Mailboxes().all()
    if not items:
        await callback.answer("Список пуст")
        return
    await callback.message.edit_text(
        f"Удалить все почты ({len(items)} шт)?",
        reply_markup=confirm_del_all(),
    )
    await callback.answer()


@router.callback_query(F.data == "del_all_yes")
async def do_del_all(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    mb = Mailboxes()
    count = len(mb.all())
    mb.clear()
    await callback.message.edit_text(f"Удалил {count} почт")
    await callback.answer()
