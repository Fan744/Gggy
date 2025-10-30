from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import requests
from bs4 import BeautifulSoup

TOKEN = "8090665368:AAGbTejpCBylQCaTBYUXNORLODXMt6tHE6o"
CHANNEL_USERNAME = "@team_black_hat_offical"  # Channel to check

def get_operator(phone_number):
    prefix = phone_number[:4]
    operators = {
        "0300": "Jazz", "0301": "Jazz", "0320": "Jazz / Warid",
        "0330": "Ufone", "0340": "Telenor", "0310": "Zong", "0355": "SCO",
    }
    return operators.get(prefix, "Unknown")

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# === START COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)

    if is_member:
        await send_welcome(update)
    else:
        # Show JOIN + JOINED buttons
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 JOIN", url="https://t.me/team_black_hat_offical")],
            [InlineKeyboardButton("✅ JOINED", callback_data="check_join")]
        ])
        await update.message.reply_text(
            "🚫 YOU NEED TO JOIN *TEAM BLACK HAT* CHANNEL\n\n"
            "FOR USE THIS BOT\n\n👇👇👇",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

# === BUTTON CLICK HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_join":
        is_member = await check_membership(user_id, context)
        if is_member:
            await query.edit_message_text("✅ You are now verified!\n\nWelcome to the bot!")
            await send_welcome(update)
        else:
            await query.edit_message_text(
                "❌ You are *still not joined*.\n\nPlease join the channel first.",
                parse_mode="Markdown"
            )

# === WELCOME TEXT FOR VERIFIED USERS ===
async def send_welcome(update: Update):
    welcome_message = (
        "💀 𝐖𝐄𝐋𝐄𝐂𝐎𝐌 𝐓𝐎 𝐎𝐋𝐃-𝐗-𝐒𝐈𝐌 𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄 💀\n\n"
        "𝐒𝐄𝐍𝐃 𝐍𝐔𝐌𝐁𝐄𝐑 𝐅𝐎𝐑 𝐃𝐀𝐓𝐀 𝐅𝐄𝐓𝐂𝐇 ☠️\n"
        "[ 𝐄𝐗𝐌𝐏𝐋𝐄 ] 030000XXXXX"
    )

    try:
        if update.message:
            await update.message.reply_text(welcome_message)
        elif update.callback_query:
            await update.callback_query.message.reply_text(welcome_message)
    except:
        pass

# === MESSAGE HANDLER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)

    if not is_member:
        await update.message.reply_text(
            "❌ You must join our channel to use this bot.\n\n🔗 [Join Now](https://t.me/team_black_hat_offical)",
            parse_mode="Markdown"
        )
        return

    search_query = update.message.text.strip()
    url = "https://minahilsimsdata.info/search.php"
    data = {"mobileNumber": search_query, "submit": ""}

    await update.message.reply_text(f"🔍 Searching for `{search_query}`...", parse_mode="Markdown")

    try:
        response = requests.post(url, data=data, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tds = soup.find_all("td")

        if len(tds) < 4:
            await update.message.reply_text("❌ No data found or server error.")
            return

        result = ""
        num_records = len(tds) // 4
        for i in range(num_records):
            record = tds[i * 4:(i + 1) * 4]
            mobile = record[0].text.strip()
            name = record[1].text.strip()
            cnic = record[2].text.strip()
            address = record[3].text.strip()
            operator = get_operator(mobile)
            result += (
                f"📦 *SIM #{i+1}*\n"
                f"👤 *Name:* `{name}`\n"
                f"📱 *Mobile:* `{mobile}`\n"
                f"🆔 *CNIC:* `{cnic}`\n"
                f"📶 *Operator:* `{operator}`\n"
                f"📍 *Address:* `{address}`\n\n"
            )

        await update.message.reply_text(result.strip(), parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# === BOT STARTUP ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()