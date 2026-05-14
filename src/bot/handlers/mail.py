from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.mailbox_keyboard import mail_detail, mail_list
from src.services.mailboxes import Mailboxes
from src.services.notletters_client import NotlettersApiError, NotlettersClient

router = Router()


async def _show(message: Message, page=0):
    items = Mailboxes().all()
    await message.answer("Почты", reply_markup=mail_list(items, page))


async def show_list(callback: CallbackQuery, page=0):
    items = Mailboxes().all()
    await callback.message.edit_text("Почты", reply_markup=mail_list(items, page))


@router.message(Command("start"))
async def start(message: Message):
    await _show(message)


@router.callback_query(F.data.startswith("pg:"))
async def change_page(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    page = int(callback.data.split(":")[1])
    await show_list(callback, page)
    await callback.answer()


@router.callback_query(F.data.startswith("mail:"))
async def open_mail(callback: CallbackQuery, notletters_client: NotlettersClient, state: FSMContext):
    await state.clear()
    index = int(callback.data.split(":")[1])
    items = Mailboxes().all()
    if not 0 <= index < len(items):
        await callback.answer("Пропала")
        return

    box = items[index]
    try:
        result = await notletters_client.get_letters(email=box.email, password=box.password)
    except NotlettersApiError as err:
        await callback.message.edit_text(f"Ошибка: {err}", reply_markup=mail_detail(index))
        await callback.answer()
        return

    if not result.success:
        text = f"{box.email}\n{result.message}"
    elif not result.letters:
        text = f"{box.email}\nписем нет"
    else:
        last = max(result.letters, key=lambda x: x.date)
        body = last.letter.text[:800]
        text = f"{box.email}\nот {last.sender_name} <{last.sender}>\n{last.subject}\n\n{body}"

    await callback.message.edit_text(text, reply_markup=mail_detail(index))
    await callback.answer()


@router.callback_query(F.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_list(callback, 0)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
