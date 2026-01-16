# Credit Card Bill Notifier (Taiwan)

A Python-based automated tool designed to fetch, parse, and organize credit card e-statements from various Taiwanese banks. It stores bill details in a local database and sends timely reminders via Telegram to ensure you never miss a payment.

## Features

- **Automated Fetching**: Connects to Gmail via the official API (recommended) or IMAP to search for bill emails.
- **Intelligent Parsing**: Extracts bill amounts and due dates from:
  - Email HTML bodies
  - PDF attachments (supports encrypted PDFs using your ID or custom passwords)
  - HTML attachments
- **Centralized Storage**: Stores all bill history in a local SQLite database (`bills.db`).
- **Telegram Notifications**: Sends alerts for upcoming due dates (default: 3 days before).
- **Web Interface**: Includes a simple Web UI to view your bill history and status.
- **Docker Support**: Ready-to-use Docker Compose setup for easy deployment.
- **Secure**: Sensitive credentials can be managed via system keyring or environment variables.

## Supported Banks

This tool currently supports parsing for the following banks:

*   **Taishin (台新銀行)**
*   **Cathay United (國泰世華)**
*   **CTBC (中國信託)**
*   **E.SUN (玉山銀行)**
*   **SinoPac (永豐銀行)**
*   **HuaNan (華南銀行)**
*   **HSBC (滙豐)** - Supports Live+, Cashback Titanium (匯鑽), and TravelOne (旅人) cards.
*   **Union Bank (聯邦銀行)**
*   **Taipei Fubon (台北富邦)**
*   **DBS (星展銀行)**
*   **SCSB (上海商銀)**

## Prerequisites

- **Python**: 3.11 or higher
- **Gmail Account**:
  - **Recommended**: Enable Gmail API and download `credentials.json`.
  - **Alternative**: Enable IMAP and generate an App Password.
- **Telegram Bot**:
  - Create a bot via [BotFather](https://t.me/BotFather) to get a `TOKEN`.
  - Get your `CHAT_ID` (you can use `python main.py --get-user-id` after valid setup).
- **System Dependencies** (Linux):
  - `libdbus-1-dev`, `libglib2.0-dev`, `libsecret-1-dev` (required for Keyring)

## Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/s950449/TW_Creditcard_Bills_Notifier.git
    cd Creditcard_Bills_Notifier
    ```

2.  **Install Python dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Copy the example environment file and edit it:
    ```bash
    cp .env.example .env
    ```
    
    Edit `.env` with your details:
    ```ini
    # Gmail Credentials
    EMAIL_USER=your_email@gmail.com
    # Required for IMAP fallback
    EMAIL_PASSWORD=your_app_password
    
    # Telegram Credentials
    TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
    TELEGRAM_CHAT_ID=123456789

    # Identity for PDF Decryption (Default password for most banks)
    ID_NUMBER=A123456789
    
    # Optional: Enable/Disable Gmail API
    USE_GMAIL_API=true
    ```
    Or use KeyringManager
    ```bash
    python keyring_manager.py set EMAIL_USER your_email@gmail.com
    python keyring_manager.py set EMAIL_PASSWORD your_app_password
    python keyring_manager.py set TELEGRAM_BOT_TOKEN your_bot_token
    python keyring_manager.py set TELEGRAM_CHAT_ID your_chat_id
    python keyring_manager.py set ID_NUMBER your_id_number
    python keyring_manager.py set USE_GMAIL_API true
    python keyring_manager.py set BIRTHDAY your_birthday
    
    ```

4.  **Gmail API Setup (Recommended)**
    1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
    2.  Create a project and enable the **Gmail API**.
    3.  Create OAuth Credentials (`Desktop App`).
    4.  Download the JSON file, save it as `credentials.json` in the project root.
    5.  On the first run, a browser window will open to authorize the app.

## Usage

### Command Line Interface

The main entry point is `main.py`.

*   **Fetch new bills:**
    ```bash
    python main.py --fetch
    ```
    *Scans your email for keywords defined in `banks/__init__.py`, parses them, and saves to the DB.*

*   **Send Notifications:**
    ```bash
    python main.py --notify
    ```
    *Checks the database for bills due in 3 days (configurable) and sends a Telegram message.*

*   **Helper Commands:**
    ```bash
    # Send a test notification to verify Telegram setup
    python main.py --test-notify
    
    # Get your User Chat ID (message the bot first)
    python main.py --get-user-id
    ```

### Web Interface

Start the web server to view your dashboard:

```bash
python web/app.py
```
Access the UI at `http://localhost:8000`.

### Docker Usage

You can run the entire stack (Web UI) using Docker Compose.

1.  Ensure `.env` and `credentials.json` (if using API) are present.
2.  Run:
    ```bash
    docker-compose up -d
    ```

## Security Note

*   **Sensitive Data**: This application handles financial data (bill amounts) and personal credentials (ID number for PDF passwords).
*   **Local Execution**: Everything runs locally on your machine or server. No data is sent to external servers other than:
    *   Google (for fetching emails)
    *   Telegram (for sending notifications)
*   **Keyring**: The code supports `keyring` to store passwords securely in your OS keychain instead of plain text in `.env`, though `.env` is supported for simplicity in Docker/headless environments.

## License

See [LICENSE](LICENSE) file.
