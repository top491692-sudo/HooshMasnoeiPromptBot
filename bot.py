import os
import threading

from flask import Flask, request
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

# =========================
# CONFIG
# =========================

CHANNEL_USERNAME = "@HooshMasnoei_Tools"

PORT = int(os.environ.get("PORT", 10000))
RENDER_EXTERNAL_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "https://hooshmasnoeipromptbot.onrender.com"
)

WEBHOOK_PATH = "/telegram-webhook"


# =========================
# PROMPTS
# =========================

PROMPTS = {
    "cinematic": """Transform the subject in the reference image into an ultra-premium cinematic portrait.

Keep the EXACT SAME person and preserve their identity completely:
same face, eyes, nose, lips, jawline, facial proportions, hairstyle, skin tone, age, body proportions and all recognizable features.

Do NOT generate a different person or change the person's identity.

Turn the ordinary smartphone photo into a stunning cinematic movie-style portrait.

Use dramatic cinematic lighting, soft rim light, subtle blue highlights, realistic skin texture, natural facial details, sophisticated cinematic color grading, shallow depth of field, beautiful bokeh, realistic shadows, subtle film grain, and a premium Hollywood movie aesthetic.

Professional 85mm lens photography, realistic depth of field, high dynamic range, photorealistic, extremely detailed.

Keep the same general pose, facial expression and camera angle while dramatically upgrading the lighting, environment and photographic quality.

Create an elegant dark cinematic background with subtle atmospheric depth and a sophisticated, luxurious visual mood.

Vertical 4:5 composition.

No face replacement, no facial redesign, no identity change, no altered facial proportions, no plastic skin, no excessive makeup, no cartoon style, no text, no logo, no watermark."""
}


# =========================
# FLASK
# =========================

app_web = Flask(__name__)


@app_web.route("/", methods=["GET", "HEAD"])
def home():
    return "Bot is running!", 200


# =========================
# USER STATE
# =========================

LAST_PROMPT = {}


# =========================
# MEMBERSHIP
# =========================

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


# =========================
# SEND PROMPT
# =========================

async def send_prompt(message, prompt_id):

    prompt = PROMPTS.get(prompt_id)

    if not prompt:
        await message.reply_text(
            "❌ این پرامپت پیدا نشد."
        )
        return

    await message.reply_text(
        "🎁 پرامپت شما:\n\n"
        f"```text\n{prompt}\n```",
        parse_mode="Markdown"
    )


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user_id = update.effective_user.id

    prompt_id = (
        context.args[0]
        if context.args
        else None
    )

    # -------------------------
    # START WITH PROMPT ID
    # -------------------------

    if prompt_id:

        if prompt_id not in PROMPTS:

            await update.message.reply_text(
                "❌ این پرامپت وجود ندارد یا لینک آن اشتباه است."
            )

            return

        LAST_PROMPT[user_id] = prompt_id

        member = await is_user_member(
            context,
            user_id
        )

        # USER IS MEMBER
        if member:

            await send_prompt(
                update.message,
                prompt_id
            )

            return

        # USER IS NOT MEMBER

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

            "🔐 برای دریافت این پرامپت، "
            "ابتدا عضو کانال ما شو:\n\n"

            "🔵 @HooshMasnoei_Tools\n\n"

            "بعد از عضویت، روی "
            "«✅ بررسی عضویت» بزن.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    # -------------------------
    # NORMAL START
    # -------------------------

    member = await is_user_member(
        context,
        user_id
    )

    if member:

        await update.message.reply_text(

            "👋 سلام! خوش اومدی 🌟\n\n"

            "از منوی ربات می‌تونی "
            "به امکانات مختلف دسترسی داشته باشی.\n\n"

            "🎁 اگر قبلاً پرامپتی دریافت کردی، "
            "می‌تونی از گزینه "
            "«دریافت مجدد پرامپت» "
            "دوباره دریافتش کنی."
        )

        return

    # NOT MEMBER

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

        "🔐 برای استفاده از ربات "
        "ابتدا باید عضو کانال ما باشی:\n\n"

        "🔵 @HooshMasnoei_Tools",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================
# CHECK MEMBERSHIP
# =========================

async def check_membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = query.data

    prompt_id = data.split(
        ":",
        1
    )[1]

    # LAST PROMPT

    if prompt_id == "last":

        prompt_id = LAST_PROMPT.get(
            user_id
        )

        if not prompt_id:

            await query.message.reply_text(

                "ℹ️ هنوز پرامپتی برای این "
                "کاربر ثبت نشده است.\n\n"

                "برای دریافت یک پرامپت، "
                "از یکی از پست‌های کانال "
                "وارد ربات شو."
            )

            return

    # CHECK MEMBER

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

    # SAVE LAST PROMPT

    LAST_PROMPT[user_id] = prompt_id

    # SEND PROMPT

    await send_prompt(
        query.message,
        prompt_id
    )


# =========================
# REPEAT PROMPT
# =========================

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

    # NOT MEMBER

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

            "🔐 برای استفاده از این "
            "قابلیت ابتدا عضو کانال شو.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    # GET LAST PROMPT

    prompt_id = LAST_PROMPT.get(
        user_id
    )

    if not prompt_id:

        await update.message.reply_text(

            "ℹ️ هنوز پرامپتی دریافت نکردی.\n\n"

            "از یکی از پست‌های کانال روی "
            "«🎁 دریافت پرامپت» بزن."
        )

        return

    # SEND

    await send_prompt(
        update.message,
        prompt_id
    )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(

        "ℹ️ راهنمای ربات\n\n"

        "🎁 برای دریافت پرامپت، "
        "از پست‌های کانال روی "
        "«دریافت پرامپت» بزن.\n\n"

        "🔄 اگر قبلاً پرامپتی دریافت کرده‌ای، "
        "از گزینه "
        "«دریافت مجدد پرامپت» استفاده کن.\n\n"

        "🤖 @HooshMasnoeiPromptBot"
    )


# =========================
# BOT COMMANDS
# =========================

async def post_init(application):

    await application.bot.set_my_commands([

        BotCommand(
            "start",
            "🏠 شروع"
        ),

        BotCommand(
            "prompt",
            "🎁 دریافت مجدد پرامپت"
        ),

        BotCommand(
            "help",
            "ℹ️ راهنما"
        )

    ])


# =========================
# CREATE APPLICATION
# =========================

TOKEN = os.environ.get(
    "BOT_TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "BOT_TOKEN is not configured."
    )


bot_app = (
    Application
    .builder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)


# =========================
# HANDLERS
# =========================

bot_app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

bot_app.add_handler(
    CommandHandler(
        "prompt",
        repeat_prompt
    )
)

bot_app.add_handler(
    CommandHandler(
        "help",
        help_command
    )
)

bot_app.add_handler(
    CallbackQueryHandler(
        check_membership,
        pattern=r"^check:"
    )
)


# =========================
# WEBHOOK
# =========================

@app_web.route(
    WEBHOOK_PATH,
    methods=["POST"]
)
def telegram_webhook():

    try:

        update_data = request.get_json(
            force=True
        )

        update = Update.de_json(
            update_data,
            bot_app.bot
        )

        # Process update asynchronously
        bot_app.update_queue.put_nowait(
            update
        )

        return "OK", 200

    except Exception as e:

        print(
            f"Webhook error: {e}"
        )

        return "ERROR", 500


# =========================
# SET WEBHOOK
# =========================

async def setup_webhook():

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


# =========================
# START BOT
# =========================

def run_bot():

    import asyncio

    async def runner():

        await bot_app.initialize()

        await bot_app.start()

        await setup_webhook()

    asyncio.run(
        runner()
    )


# =========================
# START
# =========================

if __name__ == "__main__":

    print(
        "Starting Telegram bot..."
    )

    # Start Telegram application
    run_bot()

    # Start Flask web server
    app_web.run(
        host="0.0.0.0",
        port=PORT
    )
