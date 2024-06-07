# STL
import sqlite3
from typing import Generic, TypeVar, Optional, Generator
from contextlib import contextmanager

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(
        self, success: bool, value: Optional[T] = None, error: Optional[str] = None
    ):
        self.success = success
        self.value = value
        self.error = error


# Context manager for handling transactions
@contextmanager
def transaction(
    connection: sqlite3.Connection,
) -> Generator[sqlite3.Cursor, None, None]:
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
