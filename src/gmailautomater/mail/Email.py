# STL
from typing import Type

EmailName = Type[str]


class Email(object):
    def __init__(self, subject: str, sender: str, id: bytes) -> None:
        self.id = id
        self.sender = sender
        self.subject = subject

    def __repr__(self) -> str:
        return str((self.id, self.sender, self.subject))
