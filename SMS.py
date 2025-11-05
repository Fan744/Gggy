from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import logging

# तुम्हारा BOT TOKEN यहाँ डालो
BOT_TOKEN = "8313201920:AAH1PfXk6b6sgBPNCT_H5AEMAhZETItO5gg"  # ← यहाँ पेस्ट करो

# Numverify API (फ्री) — साइनअप: https://numverify.com
NUMVERIFY_API = "http://apilayer.net/api/validate"
ACCESS_KEY = "60760dddefbb60b8b584d46910be7b7d"  # फ्री में मिलेगा

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📱 Send Phone Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "🔍 *Phone Lookup Bot*\n\n"
        "मोबाइल नंबर भेजो, मैं नाम/लोकेशन बताऊंगा!\n"
        "(सिर्फ तुम्हारा डेटा, कोई लीक नहीं)",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone

    await update.message.reply_text(f"🔎 चेक कर रहा हूँ: {phone}...")

    # Numverify से डेटा
    try:
        params = {'access_key': ACCESS_KEY, 'number': phone, 'country_code': '', 'format': 1}
        r = requests.get(NUMVERIFY_API, params=params, timeout=10)
        data = r.json()

        if data['valid']:
            info = f"""
📞 *नंबर*: {data['international_format']}
🌍 *देश*: {data['country_name']} ({data['location']})
📶 *कैरियर*: {data['carrier']}
✅ *वैलिड*: हाँ
            """
            if data.get('line_type') == 'mobile':
                info += "\n📱 *टाइप*: मोबाइल"
            else:
                info += "\n☎️ *टाइप*: लैंडलाइन"
        else:
            info = "❌ नंबर वैलिड नहीं या प्राइवेट है।"
    except:
        info = "⚠️ API एरर। बाद में ट्राय करो।"

    await update.message.reply_text(info, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith('+') and len(text) >= 10:
        await handle_contact_sim(update, text)
    else:
        await update.message.reply_text("📱 कृपया वैलिड नंबर भेजो (+91 से शुरू) या कॉन्टैक्ट शेयर करो।")

async def handle_contact_sim(update: Update, phone):
    # ऊपर वाला ही कोड (डुप्लिकेट से बचने को)
    await update.message.reply_text(f"🔎 चेक कर रहा हूँ: {phone}...")
    # वही API कोड यहाँ पेस्ट करो (ऊपर वाला)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot चल रहा है...")
    app.run_polling()

if __name__ == '__main__':
    main()
