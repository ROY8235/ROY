import os
import shutil
import zipfile
from datetime import datetime
from telegram import Update, InputFile, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from split_txt import split_story_file
import asyncio
import dotenv
import nest_asyncio

TEMP_DIR = "temp"

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 नमस्ते! कृपया अपनी स्टोरी वाली .txt फाइल भेजें।")

# ✅ File Handler - splits txt file into chapters
async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    os.makedirs(TEMP_DIR, exist_ok=True)
    filename = os.path.join(TEMP_DIR, "story.txt")
    await file.download_to_drive(custom_path=filename)

    await update.message.reply_text("✅ फ़ाइल प्राप्त हो गई, प्रोसेसिंग शुरू कर रहा हूँ...")

    chapters = split_story_file(filename)

    for i, chapter_file in enumerate(chapters, start=1):
        with open(chapter_file, "rb") as f:
            await update.message.reply_document(document=InputFile(f), filename=f"chapter_{i}.txt")

    await update.message.reply_text(f"🎉 {len(chapters)} चैप्टर सफलतापूर्वक भेज दिए गए!")

# ✅ /zip command
async def send_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(TEMP_DIR):
        await update.message.reply_text("❌ अभी तक कोई चैप्टर प्रोसेस नहीं हुआ है। पहले txt भेजें।")
        return

    zip_filename = f"chapters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if filename.startswith("chapter_") and filename.endswith(".txt"):
                zipf.write(file_path, arcname=filename)

    with open(zip_path, "rb") as f:
        await update.message.reply_document(document=InputFile(f), filename=zip_filename)

    await update.message.reply_text("✅ सभी चैप्टर्स ZIP फाइल में भेज दिए गए।")

# ✅ /clean command
async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    await update.message.reply_text("🧹 सभी अस्थाई फाइल्स डिलीट कर दी गई हैं।")

# ✅ Bot command list set on startup
async def set_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "बॉट शुरू करें"),
        BotCommand("clean", "सभी फाइल्स डिलीट करें"),
        BotCommand("zip", "सभी चैप्टर्स को zip में भेजें"),
    ])

# ✅ Main runner
async def main():
    dotenv.load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clean", clean))
    application.add_handler(CommandHandler("zip", send_zip))
    application.add_handler(MessageHandler(filters.Document.FileExtension("txt"), handle_txt_file))

    await set_commands(application)

    print("🤖 Bot is running...")
    await application.run_polling()

# ✅ Nest Async for Replit or cloud
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
