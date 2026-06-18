import os
import logging
import requests
import base64
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")


def get_github_file_sha(file_path: str):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sha")
    return None


def upload_to_github(file_path: str, file_content: bytes, commit_message: str):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    encoded_content = base64.b64encode(file_content).decode("utf-8")
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    existing_sha = get_github_file_sha(file_path)
    is_update = existing_sha is not None
    if is_update:
        data["sha"] = existing_sha

    response = requests.put(url, headers=headers, json=data)
    success = response.status_code in [200, 201]
    return success, is_update


# /start command
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 *Namaste {user.first_name}!*\n\n"
        f"Main tera *APK Upload Bot* hu 🤖\n\n"
        f"📌 *Kaise use karein:*\n"
        f"• Koi bhi `.apk` file bhejo\n"
        f"• Main usse GitHub pe upload kar dunga\n"
        f"• Tumhe direct download link milega\n\n"
        f"📂 *Repo:* `{GITHUB_REPO}`\n"
        f"🌿 *Branch:* `{GITHUB_BRANCH}`\n\n"
        f"_Bas APK bhejo, baaki main sambhalunga!_ 🚀",
        parse_mode="Markdown"
    )


# /help command
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Help Menu*\n\n"
        "📤 *APK Upload karna:*\n"
        "Sirf apni `.apk` file bhejo — bot automatically:\n"
        "  1️⃣ File download karega\n"
        "  2️⃣ GitHub pe upload karega\n"
        "  3️⃣ Purani file replace karega\n"
        "  4️⃣ Download link dega\n\n"
        "📌 *Commands:*\n"
        "/start — Bot ke baare mein jaano\n"
        "/help — Ye menu\n"
        "/status — GitHub repo status check karo\n\n"
        "⚠️ *Note:* Sirf `.apk` files accept hoti hain",
        parse_mode="Markdown"
    )


# /status command
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 GitHub connection check ho raha hai...")

    url = f"https://api.github.com/repos/{GITHUB_REPO}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        await msg.edit_text(
            f"✅ *GitHub Connected!*\n\n"
            f"📂 *Repo:* `{data['full_name']}`\n"
            f"🌿 *Branch:* `{GITHUB_BRANCH}`\n"
            f"🔒 *Private:* {'Yes' if data['private'] else 'No'}\n"
            f"💾 *Size:* {data['size']} KB\n\n"
            f"_Sab kuch sahi chal raha hai!_ 🎉",
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(
            f"❌ *GitHub Connection Failed!*\n\n"
            f"Status Code: `{response.status_code}`\n"
            f"Apna `GITHUB_TOKEN` aur `GITHUB_REPO` check karo.",
            parse_mode="Markdown"
        )


# Document/APK handler
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_name = document.file_name

    # Only APK allowed
    if not file_name.lower().endswith(".apk"):
        await update.message.reply_text(
            f"❌ *Invalid File!*\n\n"
            f"`{file_name}` accept nahi hoga.\n"
            f"Sirf `.apk` files bhejo! 📦",
            parse_mode="Markdown"
        )
        return

    # Step 1: Received
    file_size_mb = round(document.file_size / (1024 * 1024), 2)
    status_msg = await update.message.reply_text(
        f"📥 *APK Received!*\n\n"
        f"📄 File: `{file_name}`\n"
        f"📦 Size: `{file_size_mb} MB`\n\n"
        f"⏳ Downloading from Telegram...",
        parse_mode="Markdown"
    )

    # Step 2: Downloading
    try:
        file = await context.bot.get_file(document.file_id)
        file_content = bytes(await file.download_as_bytearray())
    except Exception as e:
        await status_msg.edit_text(
            f"❌ *Download Failed!*\n\n"
            f"Telegram se file download nahi hui.\n"
            f"Error: `{str(e)}`",
            parse_mode="Markdown"
        )
        return

    # Step 3: Uploading to GitHub
    await status_msg.edit_text(
        f"📤 *Uploading to GitHub...*\n\n"
        f"📄 File: `{file_name}`\n"
        f"📦 Size: `{file_size_mb} MB`\n"
        f"📂 Repo: `{GITHUB_REPO}`\n\n"
        f"⏳ Please wait...",
        parse_mode="Markdown"
    )

    try:
        commit_msg = f"Update {file_name} via Telegram bot"
        success, is_update = upload_to_github(file_name, file_content, commit_msg)
    except Exception as e:
        await status_msg.edit_text(
            f"❌ *Upload Failed!*\n\n"
            f"GitHub pe upload nahi hua.\n"
            f"Error: `{str(e)}`",
            parse_mode="Markdown"
        )
        return

    # Step 4: Result
    if success:
        download_url = f"https://github.com/{GITHUB_REPO}/raw/{GITHUB_BRANCH}/{file_name}"
        action = "🔄 Updated" if is_update else "🆕 Uploaded"
        await status_msg.edit_text(
            f"✅ *{action} Successfully!*\n\n"
            f"📄 *File:* `{file_name}`\n"
            f"📦 *Size:* `{file_size_mb} MB`\n"
            f"📂 *Repo:* `{GITHUB_REPO}`\n\n"
            f"📥 *Direct Download Link:*\n"
            f"`{download_url}`",
            parse_mode="Markdown"
        )
    else:
        await status_msg.edit_text(
            f"❌ *GitHub Upload Failed!*\n\n"
            f"Possible reasons:\n"
            f"• `GITHUB_TOKEN` expired ya invalid\n"
            f"• Repo `{GITHUB_REPO}` exist nahi karta\n"
            f"• File size too large (GitHub limit: 100MB)\n\n"
            f"_/status command se check karo_",
            parse_mode="Markdown"
        )


# Any other text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📁 Mujhe ek `.apk` file bhejo!\n\n"
        "Commands ke liye /help type karo 👇",
        parse_mode="Markdown"
    )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
