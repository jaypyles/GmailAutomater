CREATE TABLE
  IF NOT EXISTS keep_emails (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL,
    subject TEXT,
    body TEXT
  );

CREATE TABLE
  IF NOT EXISTS delete_emails (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL UNIQUE
  );

CREATE TABLE
  IF NOT EXISTS labels (
    id INTEGER PRIMARAY KEY,
    name TEXT NOT NULL UNIQUE
  );

INSERT INTO
  delete_emails (sender)
VALUES
  ('vfe-campaign-response@amazon.com'),
  ('jane@example.com');

INSERT INTO
  labels (name)
VALUES
  ('Transactions');
