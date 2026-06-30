import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

app = Flask(__name__)

# گرفتن توکن و آیدی کانال از متغیرهای محیطی
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# دیکشنری برای وضعیت کاربران
user_posts = {}

# دستور /start
async def start(update, context):
    keyboard = [[InlineKeyboardButton("📝 ارسال مطلب جدید", callback_data="new_post")]]
    await update.message.reply_text(
        "سلام! برای ارسال مطلب به کانال، روی دکمه کلیک کن.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# وقتی کاربر روی دکمه کلیک کنه
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "new_post":
        user_posts[query.from_user.id] = "waiting"
        await query.edit_message_text("لطفاً متن، عکس یا فایل خود را ارسال کن:")

# وقتی کاربر پیام بفرسته
async def handle_message(update, context):
    user_id = update.effective_user.id
    if user_posts.get(user_id) == "waiting":
        try:
            # کپی کردن پیام به کانال (همراه با عکس و کپشن)
            await context.bot.copy_message(
                chat_id=CHANNEL_ID,
                from_chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id
            )
            await update.message.reply_text("✅ مطلب شما در کانال منتشر شد!")
            del user_posts[user_id]
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {str(e)}\nمطمئن شو ربات ادمین کانال هست.")
            del user_posts[user_id]
    else:
        await update.message.reply_text("ابتدا روی دکمه /start کلیک کن.")

# تنظیمات ربات
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

# Webhook برای Render
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def webhook():
    await application.update_queue.put(Update.de_json(request.get_json(force=True), application.bot))
    return "ok"

@app.route('/')
def index():
    return "ربات فعال است!"

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
