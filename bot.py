import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
user_posts = {}

def start(update, context):
    keyboard = [[InlineKeyboardButton("📝 ارسال مطلب جدید", callback_data="new_post")]]
    update.message.reply_text("سلام! روی دکمه کلیک کن:", reply_markup=InlineKeyboardMarkup(keyboard))

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "new_post":
        user_posts[query.from_user.id] = "waiting"
        query.edit_message_text("لطفاً پیام یا عکس خود را ارسال کن:")

def handle_message(update, context):
    user_id = update.effective_user.id
    if user_posts.get(user_id) == "waiting":
        try:
            context.bot.copy_message(
                chat_id=CHANNEL_ID,
                from_chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            update.message.reply_text("✅ منتشر شد!")
            del user_posts[user_id]
        except Exception as e:
            update.message.reply_text(f"❌ خطا: {e}")
            del user_posts[user_id]
    else:
        update.message.reply_text("ابتدا روی /start کلیک کن.")

updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button_handler))
dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_message))

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dp.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "ربات فعال است!"

if __name__ == "__main__":
    updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 10000)), url_path=BOT_TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
