from aiogram import BaseMiddleware

from src.services.notletters_client import NotlettersClient


class NotlettersClientMiddleware(BaseMiddleware):
    def __init__(self, client: NotlettersClient):
        self._client = client

    async def __call__(self, handler, event, data):
        data["notletters_client"] = self._client
        return await handler(event, data)
