# STL
import os
import uuid
import logging
import sqlite3
import subprocess
from sqlite3 import Connection

# LOCAL
from gmailautomater.utils import transaction
from gmailautomater.mail.Email import EmailName
from gmailautomater.mail.Label import Label

LOG = logging.getLogger()

HOME = os.environ.get("HOME")
assert HOME, "Must set $HOME."
DATABASE_PATH = os.path.join(HOME, ".config/gmailautomater/sqlite-db/data/gmail.db")


def initialize_db() -> bool:
    """Check if the db has been initialized."""

    if os.path.exists(DATABASE_PATH):
        return True

    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        create_db = f"sqlite3 {DATABASE_PATH} < sqlite-db/data/gmail.sql"
        _ = subprocess.run(
            create_db,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        conn = connect_to_db()
        queries = [
            "CREATE TABLE IF NOT EXISTS last_checked (id INTEGER PRIMARY KEY, check_date TEXT);",
            "CREATE TABLE IF NOT EXISTS label (id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE);",
            "CREATE TABLE IF NOT EXISTS email (id TEXT PRIMARY KEY, domain TEXT NOT NULL UNIQUE);",
            """CREATE TABLE IF NOT EXISTS label_to_email (
                label_id TEXT NOT NULL,
                email_id TEXT NOT NULL,
                PRIMARY KEY (label_id, email_id),
                FOREIGN KEY (label_id) REFERENCES label (id),
                FOREIGN KEY (email_id) REFERENCES email (id)
            );""",
            "CREATE TABLE IF NOT EXISTS deletion (id INTEGER PRIMARY KEY, domain TEXT NOT NULL UNIQUE);",
            f"INSERT INTO label (id, name) VALUES ('{uuid.uuid4().hex}', 'delete');",
        ]

        for query in queries:
            execute_db(conn, query)

        return True
    except subprocess.CalledProcessError as e:
        LOG.error(f"ERROR: {e}")
        LOG.error(
            f"Command failed with exit code {e.returncode}, ensure you have sqlite3."
        )
        return False


def connect_to_db():
    """Connect to the db."""
    return sqlite3.connect(DATABASE_PATH)


def query_db(conn: Connection, query: str):
    """Make a query to the db."""
    cursor = conn.cursor()
    _ = cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def execute_db(conn: Connection, query: str):
    """Execute a command in the db."""
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


def get_last_checked():
    """Get the date of the last checked email."""
    conn = connect_to_db()
    query = f"""
    SELECT check_date FROM last_checked;
    """
    rows = query_db(conn, query)
    if len(rows) == 0:
        return None
    else:
        return rows[0][0]


def insert_last_checked(date: str) -> None:
    """Insert the date of the last checked email."""
    conn = connect_to_db()
    query = f"""
    INSERT OR REPLACE INTO last_checked (id, check_date)
    VALUES (1, '{date}');
    """
    execute_db(conn, query)


def remove_label_from_labels(label: str):
    """Remove a label from the label table."""
    conn = connect_to_db()

    try:
        with transaction(conn) as cursor:
            _ = cursor.execute("SELECT id FROM label WHERE name = ?", (label,))
            label_row: list[str] = cursor.fetchone()
            if not label_row:
                raise ValueError(f"Label '{label}' not found")

            label_id = label_row[0]
            print(label_id)

            _ = cursor.execute(
                "DELETE FROM label_to_email WHERE label_id = ?;", (label_id,)
            )

            _ = cursor.execute("DELETE FROM label where id = ?;", (label_id,))

    finally:
        conn.close()


def add_email_to_label(label: Label, email: str) -> str:
    """Add an email to be sorted into a label."""
    connection = connect_to_db()
    email_id = uuid.uuid4().hex

    try:
        with transaction(connection) as cursor:
            _ = cursor.execute("SELECT id FROM label WHERE name = ?", (label,))
            label_row: list[str] = cursor.fetchone()
            if not label_row:
                raise ValueError(f"Label '{label}' not found")

            label_id = label_row[0]

            _ = cursor.execute(
                "INSERT OR IGNORE INTO email (id, domain) VALUES (?, ?)",
                (email_id, email),
            )

            _ = cursor.execute(
                "INSERT OR IGNORE INTO label_to_email (label_id, email_id) VALUES (?, ?);",
                (label_id, email_id),
            )

    finally:
        connection.close()

    return email_id


def add_label_to_db(label: Label) -> str:
    """Add a new label to the db."""
    connection = connect_to_db()
    label_id = uuid.uuid4().hex
    try:
        with transaction(connection) as cursor:
            _ = cursor.execute(
                "INSERT INTO label (id, name) VALUES (?, ?);", (label_id, label)
            )

    finally:
        connection.close()

    return label_id


def retrieve_labels_from_db():
    """Retrieve a list of label names from the db."""
    conn = connect_to_db()
    query = "SELECT name FROM label;"
    rows = query_db(conn, query)
    return [row[0] for row in rows]


def retrieve_emails_from_db(label: Label) -> list[EmailName]:
    """Retrieve a list of email names from a table in the db."""
    conn = sqlite3.connect("sqlite-db/data/gmail.db")

    query = f"""
    SELECT e.domain
    FROM label AS l
    JOIN label_to_email AS lte ON l.id = lte.label_id
    JOIN email AS e ON lte.email_id = e.id
    WHERE l.name = '{label}';
    """

    rows: list[tuple[EmailName]] = query_db(conn, query)
    return [email[0] for email in rows]


def insert_email_into_database(email: str):
    """Attempt to insert an email into the database."""
    conn = sqlite3.connect("sqlite-db/data/gmail.db")
    cursor = conn.cursor()

    try:
        insert_query = f"INSERT INTO keep_emails(sender) VALUES (?)"
        cursor.execute(insert_query, (email,))
        conn.commit()
        LOG.info(f"Email '{email}' inserted into the database.")
    except sqlite3.IntegrityError:
        LOG.info(f"Email '{email}' already exists in the database. Skipping insertion.")

    cursor.close()
    conn.close()
