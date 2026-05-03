import os
import io
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. የግል መረጃዎች (Credentials) ---
TELEGRAM_TOKEN = "8717535794:AAEyxQCO2KVRXbhHULdp6ETl4LTeujw56oo"
GEMINI_API_KEY = "AIzaSyCAb97dcGC6vrRbrkpuHGVZYD0hMP74E7w"

# Gemini AI ማዋቀር
genai.configure(api_key=GEMINI_API_KEY)
# ለጽሁፍ እና ለፎቶ gemini-1.5-flash ምርጥ እና ፈጣን ነው
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. የቦቱ ተግባራት ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ሰላም! እኔ የ Gemini AI ረዳት ነኝ።\n\n"
        "🔹 ማንኛውንም ጥያቄ በጽሁፍ መጠየቅ ትችላለህ።\n"
        "🔹 ማንኛውንም ፎቶ ስትልክልኝ አይቼ መፍትሄ እሰጥሃለሁ።"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """የጽሁፍ ጥያቄዎችን ለመመለስ"""
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ ምላሽ ለመስጠት ተቸግሬአለሁ።")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ፎቶዎችን ተቀብሎ ለመተንተን"""
    await update.message.reply_text("🔄 ፎቶውን እያየሁት ነው... እባክዎ ይጠብቁ")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # ፎቶውን ከቴሌግራም ዳውንሎድ ማድረግ
        photo_file = await update.message.photo[-1].get_file()
        photo_bytearray = await photo_file.download_as_bytearray()
        
        # ምስሉን ለ Gemini ማዘጋጀት
        img_data = [{'mime_type': 'image/jpeg', 'data': bytes(photo_bytearray)}]
        
        # Gemini ፎቶውን እንዲያየው ማድረግ (ከመግለጫ ጋር)
        prompt = "ይህንን ምስል ተመልከትና በውስጡ ያለውን ነገር አብራራ ወይም ጥያቄ ካለበት መልስ ስጥ።"
        if update.message.caption:
            prompt = update.message.caption

        response = model.generate_content([prompt, img_data[0]])
        await update.message.reply_text(response.text)
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ ፎቶውን ማንበብ አልቻልኩም፤ እባክዎ በድጋሚ ይሞክሩ።")

# --- 3. ቦቱን ማስጀመር ---

if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # ትዕዛዞች
    application.add_handler(CommandHandler("start", start))
    
    # ለጽሁፍ መልዕክት
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # ለፎቶ መልዕክት
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Gemini Vision ቦት ስራ ጀምሯል...")
    application.run_polling()
