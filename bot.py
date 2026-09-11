import os
import asyncio
import threading
import time

from flask import Flask, request

from supabase import create_client, Client

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)


# =========================================================
# CONFIG
# =========================================================

CHANNEL_USERNAME = "@HooshMasnoei_Tools"

PORT = int(os.environ.get("PORT", 10000))

RENDER_EXTERNAL_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "https://hooshmasnoeipromptbot.onrender.com"
)

WEBHOOK_PATH = "/telegram-webhook"

BOT_TOKEN = os.environ.get("BOT_TOKEN")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured.")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not configured.")

if not SUPABASE_SECRET_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY is not configured.")


# =========================================================
# SUPABASE
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)


# =========================================================
# FLASK
# =========================================================

app_web = Flask(__name__)


@app_web.route("/", methods=["GET", "HEAD"])
def home():
    return "Bot is running!", 200


# =========================================================
# USER STATE
# =========================================================

LAST_PROMPT = {}


# =========================================================
# GET PROMPT FROM SUPABASE
# =========================================================

def get_prompt(prompt_id):
    try:
        response = (
            supabase
            .table("prompts")
            .select("id, prompt, title")
            .eq("id", prompt_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            print(f"Prompt not found in Supabase: {prompt_id}")
            return None

        return response.data[0]

    except Exception as e:
        print(f"Supabase prompt error: {e}")
        return None


# =========================================================
# MEMBERSHIP
# =========================================================

async def is_user_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:
        print(f"Membership check error: {e}")
        return False


# =========================================================
# SEND PROMPT
# =========================================================

async def send_prompt(message, prompt_id):

    prompt_data = get_prompt(prompt_id)

    if not prompt_data:
        await message.reply_text(
            "❌ این پرامپت پیدا نشد."
        )
        return

    prompt = prompt_data["prompt"]
    title = prompt_data.get("title") or "پرامپت"

    await message.reply_text(
        f"🎁 {title}\n\n"
        f"```text\n{prompt}\n```",
        parse_mode="Markdown"
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id
    prompt_id = context.args[0] if context.args else None

    print(
        f"START received | "
        f"user={user_id} | "
        f"prompt={prompt_id}"
    )

    # -----------------------------------------------------
    # START WITH PROMPT ID
    # -----------------------------------------------------

    if prompt_id:

        # بررسی وجود پرامپت در Supabase
        prompt_data = get_prompt(prompt_id)

        if not prompt_data:
            await update.message.reply_text(
                "❌ این پرامپت وجود ندارد یا لینک آن اشتباه است."
            )
            return

        LAST_PROMPT[user_id] = prompt_id

        member = await is_user_member(
            context,
            user_id
        )

        if member:
            await send_prompt(
                update.message,
                prompt_id
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔵 عضویت در کانال",
                    url="https://t.me/HooshMasnoei_Tools"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ بررسی عضویت",
                    callback_data=f"check:{prompt_id}"
                )
            ]
        ]

        await update.message.reply_text(
            "🔐 برای دریافت این پرامپت، ابتدا عضو کانال ما شو:\n\n"
            "🔵 @HooshMasnoei_Tools\n\n"
            "بعد از عضویت، روی «✅ بررسی عضویت» بزن.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # -----------------------------------------------------
    # NORMAL START
    # -----------------------------------------------------

    member = await is_user_member(
        context,
        user_id
    )

    if member:

        await update.message.reply_text(
            "👋 سلام! خوش اومدی 🌟\n\n"
            "از منوی ربات می‌تونی به امکانات مختلف دسترسی داشته باشی.\n\n"
            "🎁 اگر قبلاً پرامپتی دریافت کردی، "
            "می‌تونی از گزینه «دریافت مجدد پرامپت» "
            "دوباره دریافتش کنی."
        )

        return

    keyboard = [
        [
            InlineKeyboardButton(
                "🔵 عضویت در کانال",
                url="https://t.me/HooshMasnoei_Tools"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ بررسی عضویت",
                callback_data="check:last"
            )
        ]
    ]

    await update.message.reply_text(
        "👋 سلام! خوش اومدی 🌟\n\n"
        "🔐 برای استفاده از ربات ابتدا باید عضو کانال ما باشی:\n\n"
        "🔵 @HooshMasnoei_Tools",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# CHECK MEMBERSHIP
# =========================================================

async def check_membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id
    data = query.data

    prompt_id = data.split(":", 1)[1]

    if prompt_id == "last":

        prompt_id = LAST_PROMPT.get(user_id)

        if not prompt_id:

            await query.message.reply_text(
                "ℹ️ هنوز پرامپتی برای این کاربر ثبت نشده است.\n\n"
                "برای دریافت یک پرامپت، از یکی از پست‌های "
                "کانال وارد ربات شو."
            )

            return

    # اطمینان از وجود پرامپت
    prompt_data = get_prompt(prompt_id)

    if not prompt_data:

        await query.answer(
            "❌ این پرامپت دیگر وجود ندارد.",
            show_alert=True
        )

        return

    member = await is_user_member(
        context,
        user_id
    )

    if not member:

        await query.answer(
            "❌ هنوز عضو کانال نیستی!",
            show_alert=True
        )

        return

    LAST_PROMPT[user_id] = prompt_id

    await send_prompt(
        query.message,
        prompt_id
    )


# =========================================================
# REPEAT PROMPT
# =========================================================

async def repeat_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user_id = update.effective_user.id

    member = await is_user_member(
        context,
        user_id
    )

    if not member:

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔵 عضویت در کانال",
                    url="https://t.me/HooshMasnoei_Tools"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ بررسی عضویت",
                    callback_data="check:last"
                )
            ]
        ]

        await update.message.reply_text(
            "🔐 برای استفاده از این قابلیت ابتدا عضو کانال شو.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    prompt_id = LAST_PROMPT.get(user_id)

    if not prompt_id:

        await update.message.reply_text(
            "ℹ️ هنوز پرامپتی دریافت نکردی.\n\n"
            "از یکی از پست‌های کانال روی "
            "«🎁 دریافت پرامپت» بزن."
        )

        return

    await send_prompt(
        update.message,
        prompt_id
    )


# =========================================================
# HELP
# =========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "ℹ️ راهنمای ربات\n\n"
        "🎁 برای دریافت پرامپت، از پست‌های کانال "
        "روی «دریافت پرامپت» بزن.\n\n"
        "🔄 اگر قبلاً پرامپتی دریافت کرده‌ای، "
        "از گزینه «دریافت مجدد پرامپت» استفاده کن.\n\n"
        "🤖 @HooshMasnoeiPromptBot"
    )


# =========================================================
# COMMANDS
# =========================================================

async def post_init(application):

    await application.bot.set_my_commands([
        BotCommand("start", "🏠 شروع"),
        BotCommand("prompt", "🎁 دریافت مجدد پرامپت"),
        BotCommand("help", "ℹ️ راهنما")
    ])


# =========================================================
# TELEGRAM APPLICATION
# =========================================================

bot_app = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .post_init(post_init)
    .build()
)

bot_app.add_handler(
    CommandHandler("start", start)
)

bot_app.add_handler(
    CommandHandler("prompt", repeat_prompt)
)

bot_app.add_handler(
    CommandHandler("help", help_command)
)

bot_app.add_handler(
    CallbackQueryHandler(
        check_membership,
        pattern=r"^check:"
    )
)


# =========================================================
# ASYNCIO LOOP
# =========================================================

async_loop = None
bot_ready = False


async def telegram_worker():

    global async_loop
    global bot_ready

    async_loop = asyncio.get_running_loop()

    print("Telegram application initializing...")

    await bot_app.initialize()

    await bot_app.start()

    webhook_url = (
        RENDER_EXTERNAL_URL.rstrip("/")
        + WEBHOOK_PATH
    )

    print(
        f"Setting webhook: {webhook_url}"
    )

    await bot_app.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )

    print(
        "Webhook successfully configured."
    )

    print(
        "Telegram application is running."
    )

    bot_ready = True

    # Keep asyncio loop alive forever
    await asyncio.Event().wait()


def start_telegram():

    asyncio.run(
        telegram_worker()
    )


# =========================================================
# WEBHOOK
# =========================================================

@app_web.route(
    WEBHOOK_PATH,
    methods=["POST"]
)
def telegram_webhook():

    try:

        update_data = request.get_json(
            force=True
        )

        if not update_data:
            return "No update", 400

        if not bot_ready or async_loop is None:

            print(
                "ERROR: Bot is not ready yet."
            )

            return "Bot not ready", 503

        update = Update.de_json(
            update_data,
            bot_app.bot
        )

        print(
            "Telegram update received."
        )

        future = (
            asyncio.run_coroutine_threadsafe(
                bot_app.process_update(update),
                async_loop
            )
        )

        try:

            future.result(
                timeout=15
            )

        except Exception as e:

            print(
                f"Error while processing update: {e}"
            )

        return "OK", 200

    except Exception as e:

        print(
            f"Webhook error: {e}"
        )

        return "ERROR", 500


# =========================================================
# START EVERYTHING
# =========================================================

if __name__ == "__main__":

    print(
        "Starting Telegram bot..."
    )

    telegram_thread = threading.Thread(
        target=start_telegram,
        daemon=True
    )

    telegram_thread.start()

    # کمی صبر می‌کنیم تا بات آماده شود
    time.sleep(2)

    app_web.run(
        host="0.0.0.0",
        port=PORT
    )
