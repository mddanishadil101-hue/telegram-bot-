import os
import requests
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

# Initialize Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!"

# Bot configuration
BOT_TOKEN = "8229579729:AAHl6evGAUA96K-94SRnHVlMvj7QaEZPblM"
ADLINKFLY_API_BASE = "https://anyshorturl.com/api"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🤖 URL Shortener Bot

I can shorten URLs using your AdLinkFly website!

How to use:
1. First set your API key using /setapi command
2. Then send me any URL to shorten

Commands:
/setapi <your_api_key> - Set your API key
/help - Show help guide
    """
    await update.message.reply_text(welcome_text)

async def set_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide API key:\n/setapi YOUR_API_KEY")
        return
    
    api_key = context.args[0]
    context.user_data['api_key'] = api_key
    await update.message.reply_text("✅ API key set successfully!")

async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'api_key' not in context.user_data:
        await update.message.reply_text("❌ Please set your API key first:\n/setapi YOUR_API_KEY")
        return
    
    url = update.message.text
    api_key = context.user_data['api_key']
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ Please send a valid URL (starting with http:// or https://)")
        return
    
    try:
        processing_msg = await update.message.reply_text("⏳ Processing your URL...")
        
        api_url = f"{ADLINKFLY_API_BASE}?api={api_key}&url={requests.utils.quote(url)}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            
            if data.get('status') == 'success' and data.get('shortenedUrl'):
                shortened_url = data['shortenedUrl']
                await processing_msg.delete()
                
                await update.message.reply_text(
                    f"✅ **URL Shortened Successfully!**\n\n"
                    f"🔗 **Original URL:**\n{url}\n\n"
                    f"🚀 **Shortened URL:**\n{shortened_url}\n\n"
                    f"📋 **Copy this URL:** `{shortened_url}`",
                    parse_mode='Markdown'
                )
            else:
                await processing_msg.delete()
                await update.message.reply_text(f"❌ API Error: {data.get('message', 'Unknown error')}")
        else:
            await processing_msg.delete()
            await update.message.reply_text("❌ Error: Server returned an error response")
            
    except json.JSONDecodeError:
        await processing_msg.delete()
        await update.message.reply_text("❌ Error: Invalid response from server")
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🆘 **Help Guide**

**How to get API Key:**
1. Login to anyshorturl.com
2. Go to API section in Dashboard
3. Copy your API key

**Commands:**
/start - Start the bot
/setapi <api_key> - Set your API key
/help - Show help message

**How to use:**
1. Set API key using /setapi command
2. Send any URL to shorten
3. Copy the shortened URL from the response
    """
    await update.message.reply_text(help_text)

def run_bot():
    """Run the telegram bot"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("setapi", set_api))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_url))

        logger.info("🤖 Bot starting...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        # Restart after 30 seconds if error occurs
        import time
        time.sleep(30)
        run_bot()

if __name__ == '__main__':
    # Start bot in a separate thread
    from threading import Thread
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask app for Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
