from aiogram import Router

from src.bot.handlers import accounts, mail, passwords


def build_router() -> Router:
    r = Router()
    r.include_router(mail.router)
    r.include_router(accounts.router)
    r.include_router(passwords.router)
    return r
