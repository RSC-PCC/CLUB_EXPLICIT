import os
import stripe
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Config Stripe & Telegram
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_CHANNEL_USERNAME = os.getenv("PUBLIC_CHANNEL_USERNAME")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID")
VIP_LINK = f"https://t.me/+xXNQ0xc8chU4NjQ0"

# ✅ Page d'accueil
@app.route('/')
def home():
    return "Bot CLUB_EXPLICIT – Webhook Stripe OK"

# ✅ Webhook Stripe
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        send_telegram_message(
            chat_id=VIP_CHANNEL_ID,
            message=f"🔞 Bienvenue sur Stripe VIP\n👉 [Accès au contenu VIP]({VIP_LINK})"
        )

    return '', 200

# ✅ Webhook Telegram
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram_message(
                chat_id=chat_id,
                message=(
                    "👋 Bienvenue dans 🔥 CLUB EXPLICIT 🔐 !\n\n"
                    "🚨 Ce canal propose uniquement des extraits de contenu. "
                    "Pour débloquer l’accès complet aux vidéos, photos et autres surprises :\n\n"
                    "💎 *Abonnement VIP* :\n"
                    "👉 1 mois – 16,55€\n"
                    "👉 À vie – 29,99€\n\n"
                    "🔗 Choisis ton offre ici : https://ton-lien-de-paiement.stripe.com"
                )
            )

    return jsonify({"ok": True})

# ✅ Fonction d’envoi
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=data)
