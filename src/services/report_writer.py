from pathlib import Path


def dump_updated(results, new_password):
    path = Path("updated.txt")
    lines = [f"{r.email}:{new_password}" for r in results if r.success]
    text = "\n".join(lines)
    if lines:
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return path


def dump_all(original_accounts, results, new_password):
    path = Path("updated_mail.txt")
    by_email = {r.email: r for r in results}
    out = []
    for email, old in original_accounts:
        r = by_email.get(email)
        if r and r.success:
            out.append(f"{email}:{new_password}")
        else:
            out.append(f"{email}:{old}")
    text = "\n".join(out)
    if out:
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return path
