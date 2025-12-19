import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from PIL import Image
from reportlab.pdfgen import canvas
import database

TOKEN = "8412096907:AAGwvKvHaB9zTWBcvmFNkbGNlxUoZEq46K8"

os.makedirs("files", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    database.add_user(user_id)
    await update.message.reply_text(
        "👋 سڵاو\n"
        "وێنە یان فایل بنێرە بۆ گۆڕینی بۆ PDF"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]

    file = await photo.get_file()
    img_path = f"files/{photo.file_unique_id}.jpg"
    pdf_path = f"pdfs/{photo.file_unique_id}.pdf"

    await file.download_to_drive(img_path)

    image = Image.open(img_path).convert("RGB")
    image.save(pdf_path, "PDF")

    database.add_file(user_id, pdf_path)

    await update.message.reply_document(open(pdf_path, "rb"))

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    document = update.message.document

    file = await document.get_file()
    file_path = f"files/{document.file_unique_id}_{document.file_name}"
    pdf_path = f"pdfs/{document.file_unique_id}.pdf"

    await file.download_to_drive(file_path)

    c = canvas.Canvas(pdf_path)
    c.drawString(50, 800, f"File name: {document.file_name}")
    c.drawString(50, 770, "Converted to PDF")
    c.save()

    database.add_file(user_id, pdf_path)

    await update.message.reply_document(open(pdf_path, "rb"))

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
