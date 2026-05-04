import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Render ፖርት እንዲያገኝ የሚረዳ ሰርቨር ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- ቦት መረጃዎች ---
TELEGRAM_TOKEN = "8717535794:AAEyxQCO2KVRXbhHULdp6ETl4LTeujw56oo"
GEMINI_API_KEY = "AIzaSyCAb97dcGC6vrRbrkpuHGVZYD0hMP74E7w"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ Gemini AI ቦት ዝግጁ ነው። የፈለጉትን ይጠይቁኝ።")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception:
        await update.message.reply_text("ይቅርታ፣ ምላሽ መስጠት አልቻልኩም።")

if __name__ == '__main__':
    # ሰርቨሩን ማስነሳት
    Thread(target=run_server, daemon=True).start()
    
    # ቦቱን ማስነሳት
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    application.run_polling()
