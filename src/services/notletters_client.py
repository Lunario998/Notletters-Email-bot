import asyncio

import httpx

from src.services.models import ChangePasswordResult, Letter, LettersResult


class NotlettersApiError(RuntimeError):
    pass


class NotlettersClient:
    BASE_PATH = "/v1"

    def __init__(self, api_key, base_url, timeout=15.0, gap=0.1):
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + self.BASE_PATH,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        self._gap = gap

    async def aclose(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def get_letters(self, email, password, search=None, star=None):
        body = {"email": email, "password": password}
        filters = {}
        if search:
            filters["search"] = search
        if star is not None:
            filters["star"] = star
        if filters:
            body["filters"] = filters

        try:
            data = await self._post("/letters", body)
        except NotlettersApiError as e:
            return LettersResult(email=email, success=False, message=str(e))

        raw = data.get("letters", []) if isinstance(data, dict) else data
        letters = [Letter.model_validate(x) for x in raw]
        return LettersResult(email=email, success=True, letters=letters)

    async def change_password(self, email, old_password, new_password):
        body = {"email": email, "old_password": old_password, "new_password": new_password}
        try:
            data = await self._post("/change-password", body)
        except NotlettersApiError as e:
            return ChangePasswordResult(email=email, success=False, message=str(e))
        return ChangePasswordResult(email=email, success=True, message=str(data))

    async def change_passwords(self, accounts, new_password, batch_size=5):
        out = []
        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            tasks = [self.change_password(e, p, new_password) for e, p in batch]
            out.extend(await asyncio.gather(*tasks))
            await asyncio.sleep(1)
        return out

    async def buy_emails(self, count=1, type_email=1):
        data = await self._post("/buy-emails", {"count": count, "type_email": type_email})
        pairs = []
        for item in data:
            email, password = str(item).split(":", 1)
            pairs.append((email, password))
        return pairs

    async def _post(self, path, payload=None):
        for attempt in (1, 2):
            try:
                resp = await self._client.post(path, json=payload)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError):
                if attempt == 2:
                    raise NotlettersApiError("Сетевой сбой при запросе к NotLetters API")
                await asyncio.sleep(0.5)
                continue
            finally:
                await asyncio.sleep(self._gap)

            if resp.is_success:
                try:
                    data = resp.json()
                except ValueError:
                    raise NotlettersApiError("Некорректный ответ API (ожидался JSON)")
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                return data

            if 500 <= resp.status_code < 600 and attempt == 1:
                await asyncio.sleep(0.5)
                continue

            try:
                msg = resp.json().get("error", f"HTTP {resp.status_code}")
            except ValueError:
                msg = f"HTTP {resp.status_code}"
            raise NotlettersApiError(str(msg))
