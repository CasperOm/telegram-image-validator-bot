from telegram.ext import ApplicationBuilder, MessageHandler, filters
from PIL import Image
import pytesseract
import openai
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

openai.api_key = OPENAI_KEY

image_store = {}

async def handle_photo(update, context):
    chat_id = update.message.chat_id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    image_path = f"{photo.file_id}.jpg"
    await file.download_to_drive(image_path)

    text = pytesseract.image_to_string(Image.open(image_path))

    if chat_id not in image_store:
        image_store[chat_id] = []

    image_store[chat_id].append(text)

    if len(image_store[chat_id]) == 2:
        result = compare_texts(image_store[chat_id][0], image_store[chat_id][1])
        await update.message.reply_text(result)
        image_store[chat_id] = []
    else:
        await update.message.reply_text("Image received. Send next image.")

def compare_texts(t1, t2):
    prompt = f"""
Compare two product lists and quantities.
Reply:
Match or Mismatch with details.

List1:
{t1}

List2:
{t2}
"""

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
