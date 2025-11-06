import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token yahan dalo (BotFather se milega)
BOT_TOKEN = '8313201920:AAH1PfXk6b6sgBPNCT_H5AEMAhZETItO5gg'

# API base URL aur key
API_BASE = 'https://kalyug-papa.vercel.app/api/info'
API_KEY = 'jhat-ke-pakode'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot start command handler."""
    await update.message.reply_text(
        'Namaste! Phone number bhejo (10-digit Indian number, jaise 9876543210) lookup ke liye. Example: /info 9876543210\n'
        'Ya sirf number type karo.'
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /info command handler with optional phone number argument."""
    if context.args:
        phone = context.args[0]
    else:
        await update.message.reply_text('Phone number provide karo: /info <number>')
        return

    await get_phone_info(update, phone)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle direct messages that look like phone numbers (10 digits)."""
    text = update.message.text.strip()
    if text.isdigit() and len(text) == 10:
        await get_phone_info(update, text)
    else:
        await update.message.reply_text('Valid 10-digit phone number bhejo lookup ke liye.')

async def get_phone_info(update: Update, phone: str) -> None:
    """Fetch info from API and send response."""
    try:
        # API call
        url = f"{API_BASE}?num={phone}&key={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Format response (API structure ke hisab se adjust karo agar alag hai)
        # Assuming common keys: carrier, location, type, etc. (tool se exact nahi mila, but typical telecom API)
        formatted_info = f"📱 Phone: {phone}\n"
        if 'carrier' in data:
            formatted_info += f"🛡️ Carrier: {data['carrier']}\n"
        if 'location' in data:
            formatted_info += f"📍 Location: {data['location']}\n"
        if 'type' in data:
            formatted_info += f"🔍 Type: {data['type']}\n"
        if 'status' in data:
            formatted_info += f"✅ Status: {data['status']}\n"
        # Add more keys as per actual API response
        formatted_info += "\nFull JSON: " + str(data)  # Fallback for full data

        await update.message.reply_text(formatted_info)

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        await update.message.reply_text('Oops! API error hua. Baad mein try karo.')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text('Kuch gadbad ho gaya. Number check karo.')

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
