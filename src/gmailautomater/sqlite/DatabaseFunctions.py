# STL
import os
import logging
import sqlite3
import subprocess
from sqlite3 import Connection

# LOCAL
from gmailautomater.mail.Email import EmailName

LOG = logging.getLogger()


def initalize_db():
    """Check if the db has been initalized."""
    file_path = os.path.join(os.getcwd(), "sqlite-db/data/gmail.db")
    if os.path.exists(file_path):
        return True
    else:
        try:
            create_db = "sqlite3 sqlite-db/data/gmail.db < sqlite-db/data/gmail.sql"
            subprocess.run(
                create_db,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            LOG.error(f"Command failed with exit code {e.returncode}")
            return False


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
        return rows[0]


def insert_last_checked(date):
    """Insert the date of the last checked email."""
    conn = connect_to_db()
    query = f"""
    INSERT OR REPLACE INTO last_checked (id, check_date)
    VALUES (1, {date});
    """
    execute_db(conn, query)


def delete_label_table(label: str):
    """Delete the table for the label."""
    conn = connect_to_db()
    query = f"""
    DROP TABLE {label};
    """
    execute_db(conn, query)


def remove_label_from_labels(label: str):
    """Remove a label from the label table."""
    conn = connect_to_db()
    query = f"""
    DELETE FROM labels
    WHERE name = '{label}';
    """
    execute_db(conn, query)


def add_email_to_label(label: str, email: str):
    """Add a email to be sorted into a label."""
    conn = connect_to_db()
    query = f"""
    INSERT OR IGNORE INTO {label} (sender)
    VALUES
    ('{email}');
    """
    execute_db(conn, query)


def add_label_to_db(label_name: str):
    """Add a new label to the db."""
    conn = connect_to_db()
    query = f"""
    CREATE TABLE
    IF NOT EXISTS {label_name} (
        id INTEGER PRIMARY KEY,
        sender TEXT NOT NULL UNIQUE
    );
    """
    execute_db(conn, query)


def add_label_to_table(label_name: str):
    """Add a label to the labels table in the db."""
    conn = connect_to_db()
    query = f"""
    INSERT INTO
    labels (name)
    VALUES
    ('{label_name}');
    """
    execute_db(conn, query)


def retrieve_labels_from_db():
    """Retrieve a list of label names from the db."""
    conn = connect_to_db()
    query = "SELECT name FROM labels"
    rows = query_db(conn, query)
    return [row[0] for row in rows]


def retrieve_emails_from_db(table_name: str) -> list[EmailName]:
    """Retrieve a list of email names from a table in the db."""
    conn = sqlite3.connect("sqlite-db/data/gmail.db")
    query = f"SELECT sender FROM `{table_name}`"
    LOG.info(query)
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
