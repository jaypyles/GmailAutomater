CREATE TABLE
  IF NOT EXISTS keep_emails (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL,
    subject TEXT,
    body TEXT
  );

CREATE TABLE
  IF NOT EXISTS last_checked (id INTEGER PRIMARY KEY, check_date TEXT);

CREATE TABLE
  IF NOT EXISTS labels (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);

CREATE TABLE
  IF NOT EXISTS Transactions (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL UNIQUE
  );

CREATE TABLE
  IF NOT EXISTS deletion (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL UNIQUE
  );

CREATE TABLE
  IF NOT EXISTS BillEmails (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL UNIQUE
  );

INSERT INTO
  deletion (sender)
VALUES
  ('partner-news@reply.spreadshirt.com'),
  ('jane@example.com');

INSERT INTO
  Transactions (sender)
VALUES
  ('jane@example.com');

INSERT INTO
  labels (name)
VALUES
  ('Transactions'),
  ('deletion'),
  ('BillEmails');
