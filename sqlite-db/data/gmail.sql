CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL,
    subject TEXT,
    body TEXT
);

INSERT INTO emails (sender, subject, body)
VALUES
    ('john@example.com', 'Hello', 'This is a test email.'),
    ('jane@example.com', 'Important Notice', 'Please read the attached document.');
