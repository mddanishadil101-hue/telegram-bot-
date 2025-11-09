import requests
import json
import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot configuration
BOT_TOKEN = "8229579729:AAHl6evGAUA96K-94SRnHVlMvj7QaEZPblM"
ANYSHORTURL_API_BASE = "https://anyshorturl.com"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class URLShortenerBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("setapi", self.set_api))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.shorten_url))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
🤖 AnyShortURL Bot

I can shorten URLs using your AnyShortURL website!

Commands:
/setapi <your_api_key> - Set your API key
/help - Show help guide
        """
        await update.message.reply_text(welcome_text)
    
    async def set_api(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Please provide API key:\n/setapi YOUR_API_KEY")
            return
        
        api_key = context.args[0]
        context.user_data['api_key'] = api_key
        await update.message.reply_text("✅ API key set successfully!")
    
    async def shorten_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            
            # AnyShortURL API call
            api_url = f"{ANYSHORTURL_API_BASE}/api?api={api_key}&url={requests.utils.quote(url)}"
            
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
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
                    error_msg = data.get('message', 'Unknown error')
                    await update.message.reply_text(f"❌ API Error: {error_msg}")
            else:
                await processing_msg.delete()
                await update.message.reply_text(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🆘 **AnyShortURL Bot Help**

**How to get API Key:**
1. Login to anyshorturl.com
2. Go to API section in Dashboard
3. Copy your API key

**Commands:**
/start - Start the bot
/setapi <api_key> - Set your API key
/help - Show help message
        """
        await update.message.reply_text(help_text)
    
    def run(self):
        print("🤖 Bot starting on Render.com...")
        self.application.run_polling()

if __name__ == '__main__':
    bot = URLShortenerBot()
    bot.run()
