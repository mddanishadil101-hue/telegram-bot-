import requests
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8229579729:AAHl6evGAUA96K-94SRnHVlMvj7QaEZPblM"

# Detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("🚀 BOT STARTING - DEBUG VERSION...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"✅ /start received from {update.effective_user.first_name}")
    await update.message.reply_text("🎉 Debug Bot is Working!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📝 Message received: {text}")
    await update.message.reply_text(f"🔁 Echo: {text}")

def main():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1} to start bot...")
            
            app = Application.builder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
            
            print("✅ Starting polling...")
            app.run_polling()
            break
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("🔄 Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("💥 All attempts failed")

if __name__ == '__main__':
    main()
