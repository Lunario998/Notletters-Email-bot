from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Mailbox:
    email: str
    password: str


class Mailboxes:
    def __init__(self, path="mailboxes.txt"):
        self._path = Path(path)

    def all(self):
        return self._load()

    def add(self, email, password):
        rows = self._load()
        for m in rows:
            if m.email == email:
                return False
        rows.append(Mailbox(email, password))
        self._save(rows)
        return True

    def remove(self, email):
        rows = self._load()
        kept = [m for m in rows if m.email != email]
        if len(kept) == len(rows):
            return False
        self._save(kept)
        return True

    def update_passwords(self, new_by_email):
        rows = self._load()
        updated = [Mailbox(m.email, new_by_email.get(m.email, m.password)) for m in rows]
        self._save(updated)

    def clear(self):
        self._save([])

    def _load(self):
        if not self._path.exists():
            return []
        out = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            email, pw = line.split(":", 1)
            email, pw = email.strip(), pw.strip()
            if email and pw:
                out.append(Mailbox(email, pw))
        return out

    def _save(self, rows):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        body = "\n".join(f"{m.email}:{m.password}" for m in rows)
        if body:
            body += "\n"
        self._path.write_text(body, encoding="utf-8")
