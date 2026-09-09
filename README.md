# Daraja Demo — Django M-Pesa STK Push Integration

A Django project integrating Safaricom's Daraja API for M-Pesa STK Push (Lipa Na M-Pesa Online) payments, built under the Oran Softwares brand.

## Project Structure

```
DarajaDemo/
├── config/                # Django project settings
│   ├── settings.py
│   ├── urls.py
├── home/                  # Landing page app
│   ├── templates/home/index.html
│   ├── views.py
│   ├── urls.py
├── mpesa/                 # M-Pesa Daraja integration app
│   ├── models.py          # MpesaTransaction model
│   ├── utils.py           # Auth, password generation, STK push logic
│   ├── views.py           # initiate_payment, mpesa_callback, check_status
│   ├── urls.py
│   ├── admin.py
├── manage.py
├── requirements.txt
├── .env                   # Not committed — see Environment Variables below
├── setup.sh               # One-time environment setup script
```

## Requirements

- Python 3.10+
- pip
- [ngrok](https://ngrok.com/download) (for local callback testing only — not needed in production)

## Environment Variables

Create a `.env` file in the project root (same level as `manage.py`):

```env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://your-ngrok-subdomain.ngrok-free.app/mpesa/callback/
MPESA_BASE_URL=https://sandbox.safaricom.co.ke
```

> The shortcode and passkey above are Safaricom's published sandbox test values — shared by all developers testing STK Push in sandbox. Swap these for your real production values after completing Safaricom's Go Live process.

## Setup

Run the included setup script, or follow these steps manually:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Create a virtual environment (`venv/`)
2. Install dependencies from `requirements.txt`
3. Prompt you to create your `.env` file if one doesn't exist
4. Run `makemigrations` and `migrate`
5. Prompt you to create a Django superuser

## Running Locally

**Terminal 1 — Django server:**
```bash
source venv/bin/activate      # venv\Scripts\activate on Windows
python manage.py runserver
```

**Terminal 2 — ngrok (required for receiving Safaricom's callback locally):**
```bash
ngrok http 8000
```

Copy the `https://` URL ngrok gives you, update `MPESA_CALLBACK_URL` in `.env`, add the ngrok domain to `ALLOWED_HOSTS` in `settings.py`, then restart the Django server.

```python
# settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.dev', '.ngrok-free.app']
```

## Testing the Payment Flow

1. Visit `http://localhost:8000/`
2. Enter phone number `254708374149` (Safaricom's official sandbox test number) and an amount
3. Submit — the frontend polls `/mpesa/status/<checkout_request_id>/` until Safaricom's callback updates the transaction
4. Check `http://localhost:8000/admin/` to see the `MpesaTransaction` record and its final status

You can also test the API directly:
```bash
curl -X POST http://localhost:8000/mpesa/stk-push/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "254708374149", "amount": 1}'
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/mpesa/stk-push/` | POST | Initiates an STK push to the given phone number |
| `/mpesa/callback/` | POST | Receives the payment result from Safaricom (CSRF-exempt, called by Safaricom's servers) |
| `/mpesa/status/<checkout_request_id>/` | GET | Frontend polls this to check if a transaction has resolved |

## Known Sandbox Behavior

Safaricom's sandbox frequently returns `"DS timeout user cannot be reached"` as a `ResultDesc` even on legitimate test attempts — this is expected simulated behavior, not a bug in this integration. It confirms the callback pipeline is working; it just means the simulated "customer" didn't complete the PIN entry in time.

## Production Checklist (not yet done)

- [ ] Apply for Safaricom Go Live — obtain production shortcode, passkey, consumer key/secret
- [ ] Swap `MPESA_BASE_URL` to `https://api.safaricom.co.ke`
- [ ] Set real `MPESA_CALLBACK_URL` (must be HTTPS) pointing to the deployed domain
- [ ] Add rate limiting to `/mpesa/stk-push/`
- [ ] Add `timeout=` to all `requests` calls in `utils.py`
- [ ] Validate `amount` input (positive number) before calling `stk_push`
- [ ] Switch database from SQLite to PostgreSQL for production
- [ ] Configure persistent logging (file or external service, not just console)
- [ ] Set `DEBUG = False` and lock down `ALLOWED_HOSTS` to the real domain
- [ ] Consider idempotency protection against duplicate payment submissions

## Tech Stack

- Django
- python-decouple (environment variables)
- requests (HTTP calls to Daraja API)
- SQLite (dev) — PostgreSQL recommended for production
