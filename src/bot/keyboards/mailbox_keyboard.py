from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.services.mailboxes import Mailbox

PER_PAGE = 6


def mail_list(mailboxes: list[Mailbox], page=0) -> InlineKeyboardMarkup:
    total = len(mailboxes)
    pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(0, min(page, pages - 1))

    start = page * PER_PAGE
    chunk = mailboxes[start:start + PER_PAGE]

    rows = []
    for i, box in enumerate(chunk):
        idx = start + i
        rows.append([InlineKeyboardButton(text=box.email, callback_data=f"mail:{idx}")])

    if not chunk:
        rows.append([InlineKeyboardButton(text="пусто", callback_data="noop")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀", callback_data=f"pg:{page - 1}"))
    if pages > 1:
        nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶", callback_data=f"pg:{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="+ добавить", callback_data="add")])
    rows.append([InlineKeyboardButton(text="сменить пароли", callback_data="chpw")])
    rows.append([InlineKeyboardButton(text="удалить почты", callback_data="del_all")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def mail_detail(index: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="сменить пароль", callback_data=f"pw1:{index}")],
        [InlineKeyboardButton(text="удалить", callback_data=f"del:{index}")],
        [InlineKeyboardButton(text="назад", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_chpw(target="all") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="да", callback_data=f"chpw_yes:{target}")],
        [InlineKeyboardButton(text="нет", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_del_all() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="да, удалить все", callback_data="del_all_yes")],
        [InlineKeyboardButton(text="нет", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
