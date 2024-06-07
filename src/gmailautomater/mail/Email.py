# STL
import re
from typing import NewType

EmailName = NewType("EmailName", str)


class Email(object):
    def __init__(self, subject: str, sender: EmailName, id: bytes, date: str) -> None:
        self.id = id
        simple_email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        _sender = re.search(simple_email_regex, sender)
        self.sender = _sender.group(0) if _sender else ""
        self.subject = subject
        self.date = date

    def __repr__(self) -> str:
        return str((self.id, self.sender, self.subject, self.date))
