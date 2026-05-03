import os
import requests
import base64
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

BOT_TOKEN = "8770801794:AAHwZPjH0XGilzlkgBIbW9JSbz5EHAADKvM"
OWNER_ID = 5467108555
GITHUB_TOKEN = "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"
GITHUB_REPO = "amiralimosavian13/my-files"

async def handle_file(update: Update, context):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("شما اجازه ندارید.")
        return
    msg = update.message
    file = None
    file_name = None

    if msg.document:
        file = await msg.document.get_file()
        file_name = msg.document.file_name
    elif msg.photo:
        photo = msg.photo[-1]
        file = await photo.get_file()
        file_name = f"photo_{photo.file_id}.jpg"
    elif msg.video:
        file = await msg.video.get_file()
        file_name = msg.video.file_name or "video.mp4"
    else:
        await msg.reply_text("فقط فایل، عکس یا ویدیو بفرست.")
        return

    await msg.reply_text(f"📥 در حال دریافت {file_name}...")

    try:
        await file.download_to_drive(file_name)
        with open(file_name, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        data = {"message": f"Upload {file_name}", "content": content}
        response = requests.put(url, headers=headers, json=data)

        os.remove(file_name)

        if response.status_code == 201:
            download_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{file_name}"
            await msg.reply_text(f"✅ آپلود شد!\n{download_url}")
        else:
            await msg.reply_text(f"❌ خطا: {response.status_code}")
    except Exception as e:
        await msg.reply_text(f"❌ خطا: {str(e)[:200]}")
        if os.path.exists(file_name):
            os.remove(file_name)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_file))
    print("✅ ربات روشن شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
