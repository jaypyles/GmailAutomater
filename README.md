# Gmail Automater

## Overview

Gmail Automater is a tool designed to help you organize and manage your Gmail inbox efficiently. This CLI-based tool allows you to set up labels, add emails to specific labels, delete emails, and sync your Gmail labels with a local database.

Features:

    Organize emails with specific labels
    Set and store email credentials securely
    Add or remove labels in Gmail
    Add emails to labels for sorting
    Mark emails for deletion
    Sync Gmail labels and emails with a local SQLite database
    List all stored labels

## Installation

Clone the repository:

```sh
git clone https://github.com/jaypyles/GmailAutomater
cd GmailAutomater
```

Install dependencies using PDM:

```sh
pdm install
```

Or build from source:

```sh
pdm run build
```

```sh
pipx install dist/gmailautomater-...-py3.none.whl
```

## Usage

### Command Overview

```sh
    organize --all: Organize all emails.
    set_credentials <email> <app_password>: Set the email and app password for Gmail 2FA.
    add_label <label>: Add a label to Gmail.
    remove_label <label>: Remove a label from Gmail.
    add_email --email <email> --label <label>: Add an email to a specific label.
    delete_email --email <email>: Mark an email for deletion.
    sync: Sync all email senders and labels from current folders.
    list_labels: List all currently stored labels.
```

### Example Commands

Organize Emails

```sh
gmailautomater organize --all
```

Set Email Credentials

```sh
gmailautomater set_credentials example@gmail.com your_app_password
```

Add a Label

```sh
gmailautomater add_label "Important"
```

Remove a Label

```sh
gmailautomater remove_label "Spam"
```

Add an Email to a Label

```sh
gmailautomater add_email --email "contact@example.com" --label "Work"
```

Set an email for deletion

```sh
gmailautomater delete_email --email "spam@example.com"
```

Sync Labels and Emails

```sh
gmailautomater sync
```

List All Labels

```sh
gmailautomater list_labels
```

## Contributing

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit them (git commit -m 'Add new feature').
Push to the branch (git push origin feature/your-feature).
Open a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or suggestions, please open an issue in the repository.
