# STL
import logging
import sqlite3
from sqlite3 import Connection

# LOCAL
from gmailautomater.mail.Email import EmailName

LOG = logging.getLogger()


def connect_to_db():
    """Connect to the db."""
    return sqlite3.connect("sqlite-db/data/gmail.db")


def query_db(conn: Connection, query: str):
    """Make a query to the db."""
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def retrieve_labels_from_db():
    """Retrieve a list of label names from the db."""
    conn = connect_to_db()
    query = "SELECT name FROM labels"
    rows = query_db(conn, query)
    return [row[0] for row in rows]


def retrieve_emails_from_db(table_name: str) -> list[EmailName]:
    """Retrieve a list of email names from a table in the db."""
    conn = sqlite3.connect("sqlite-db/data/gmail.db")
    query = f"SELECT sender FROM {table_name}"
    rows = query_db(conn, query)
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
