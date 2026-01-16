#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created. For higher security, use 'python keyring_manager.py set <key> <value>' to store sensitive data."
fi

echo "Setup complete."
echo "To use WebUI via Docker: 'docker-compose up --build'"
echo "To store password securely: 'python keyring_manager.py set EMAIL_PASSWORD <your_password>'"
