#!/usr/bin/env bash
# setup.sh — one-time environment setup for DarajaDemo
# Usage: chmod +x setup.sh && ./setup.sh

set -e  # exit immediately if any command fails

echo "=== Daraja Demo Setup ==="

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists, skipping creation."
fi

# 2. Activate venv (works for bash/zsh on Mac/Linux/WSL)
# Windows users: run this script via Git Bash, or activate manually with venv\Scripts\activate
source venv/bin/activate

# 3. Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "No requirements.txt found — installing core packages directly."
    pip install django requests python-decouple
    pip freeze > requirements.txt
fi

# 4. Create .env if missing
if [ ! -f ".env" ]; then
    echo ""
    echo "No .env file found. Creating one now — you'll need your Daraja sandbox credentials."
    read -p "MPESA_CONSUMER_KEY: " CONSUMER_KEY
    read -p "MPESA_CONSUMER_SECRET: " CONSUMER_SECRET
    read -p "MPESA_CALLBACK_URL (e.g. your ngrok URL + /mpesa/callback/): " CALLBACK_URL

    cat > .env <<EOF
MPESA_CONSUMER_KEY=${CONSUMER_KEY}
MPESA_CONSUMER_SECRET=${CONSUMER_SECRET}
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=${CALLBACK_URL}
MPESA_BASE_URL=https://sandbox.safaricom.co.ke
EOF

    echo ".env file created."
else
    echo ".env already exists, skipping."
fi

# 5. Run migrations
echo ""
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# 6. Offer to create a superuser
echo ""
read -p "Create a Django superuser now? (y/n): " CREATE_SUPERUSER
if [ "$CREATE_SUPERUSER" = "y" ] || [ "$CREATE_SUPERUSER" = "Y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Activate the venv:  source venv/bin/activate   (or venv\\Scripts\\activate on Windows)"
echo "  2. Start the server:   python manage.py runserver"
echo "  3. In a second terminal, start ngrok: ngrok http 8000"
echo "  4. Update MPESA_CALLBACK_URL in .env with your ngrok URL, and add the ngrok domain to ALLOWED_HOSTS in settings.py"
echo "  5. Visit http://localhost:8000/ to test the payment flow"
