import os
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. ለ Render የፖርት ስህተት መፍትሄ (Web Server) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    # Render የሚሰጠውን ፖርት ይጠቀማል፣ ካልተሰጠ 8080
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# --- 2. የግል መረጃዎች (Credentials) ---
TELEGRAM_TOKEN = "8717535794:AAEyxQCO2KVRXbhHULdp6ETl4LTeujw56oo"
GEMINI_API_KEY = "AIzaSyCAb97dcGC6vrRbrkpuHGVZYD0hMP74E7w"

# Gemini AI ማዋቀር
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. የቦቱ ተግባራት ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ሰላም! እኔ የ Gemini AI ረዳት ነኝ።\n\n"
        "✅ ጥያቄዎችን በጽሁፍ መጠየቅ ትችላለህ።\n"
        "✅ ፎቶ ስትልክልኝ አይቼ መፍትሄ እሰጣለሁ።"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የጽሁፍ ጥያቄዎችን ለመመለስ"""
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("❌ ይቅርታ፣ ምላሽ ለመስጠት ተቸግሬአለሁ።")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ፎቶዎችን አይቶ ለመተንተን"""
    await update.message.reply_text("🔍 ፎቶውን እያየሁት ነው... እባክዎ ይጠብቁ")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # ፎቶውን ከቴሌግራም ዳውንሎድ ማድረግ
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        # ምስሉን ለ Gemini ማዘጋጀት
        img_parts = [{"mime_type": "image/jpeg", "data": bytes(photo_bytes)}]
        
        prompt = update.message.caption if update.message.caption else "ይህ ምስል ምንድነው? አብራራው።"
        
        response = model.generate_content([prompt, img_parts[0]])
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ ፎቶውን ማንበብ አልቻልኩም፤ እባክዎ በድጋሚ ይሞክሩ።")

# --- 4. ቦቱን ማስጀመር ---

if __name__ == '__main__':
    # 1. መጀመሪያ ፖርት የሚከፍተውን ሰርቨር በባክግራውንድ ማስነሳት (ለ Render)
    Thread(target=run_health_server, daemon=True).start()
    
    # 2. የቴሌግራም ቦቱን ማስነሳት
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Gemini AI Bot is running...")
    application.run_polling()
