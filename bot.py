import os
import asyncio
import threading

from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "@HooshMasnoei_Tools"

PORT = int(os.getenv("PORT", "10000"))

RENDER_EXTERNAL_URL = os.getenv(
    "RENDER_EXTERNAL_URL",
    "https://hooshmasnoeipromptbot.onrender.com"
)

WEBHOOK_PATH = "/telegram-webhook"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


# =========================
# PROMPTS
# =========================

PROMPTS = {

    "cinematic": """
Transform the subject in the reference image into an ultra-premium cinematic portrait.

Keep the EXACT SAME person and preserve their identity completely:
same face, eyes, nose, lips, jawline, facial proportions, hairstyle, skin tone, age, body proportions and all recognizable features.

Do NOT generate a different person or change the person's identity.

Turn the ordinary smartphone photo into a stunning cinematic movie-style portrait.

Use dramatic cinematic lighting, soft rim light, subtle blue highlights, realistic skin texture, natural facial details, sophisticated cinematic color grading, shallow depth of field, beautiful bokeh, realistic shadows, subtle film grain, and a premium Hollywood movie aesthetic.

Professional 85mm lens photography, realistic depth of field, high dynamic range, photorealistic, extremely detailed.

Keep the same general pose, facial expression and camera angle while dramatically upgrading the lighting, environment and photographic quality.

Create an elegant dark cinematic background with subtle atmospheric depth and a sophisticated, luxurious visual mood.

Vertical 4:5 composition.

No face replacement, no facial redesign, no identity change, no altered facial proportions, no plastic skin, no excessive makeup, no cartoon style, no text, no logo, no watermark.
""",

    "product": """
Transform the provided product photo into an ultra-premium commercial advertising image suitable for a high-end brand campaign.

PRODUCT PRESERVATION — ABSOLUTE PRIORITY:

Keep the EXACT SAME PRODUCT from the reference image.

Preserve its exact shape, proportions, dimensions, geometry, materials, texture, colors, surface details, buttons, ports, stitching, edges, branding and every recognizable physical characteristic.

Do NOT redesign, reshape, resize, replace, simplify or modify the product in any way.

Do NOT invent missing details or add features that are not present in the original product.

The product must remain physically accurate and immediately recognizable as the exact same item.

COMMERCIAL PHOTOGRAPHY:

Transform the ordinary product photo into a sophisticated premium advertising photograph.

Create professional studio-quality lighting with a soft directional key light, subtle fill light, controlled rim lighting, realistic reflections and naturally diffused shadows.

Use physically accurate lighting and materials with realistic highlights, reflections and surface textures.

Create a refined luxury advertising atmosphere inspired by premium global product campaigns.

COMPOSITION:

Make the product the clear hero subject.

Use a carefully balanced commercial composition with strong visual hierarchy, clean negative space and elegant framing.

Place the product naturally within a sophisticated environment without allowing the background or decorative elements to distract from it.

Create realistic depth and dimensionality while maintaining the exact scale and proportions of the product.

BACKGROUND:

Create a premium, elegant and visually sophisticated background that complements the product.

Use subtle gradients, realistic surfaces, atmospheric depth and carefully controlled environmental details.

The background should feel luxurious and intentional rather than generic or artificial.

Choose the environment and background style based on the product category while keeping the product as the primary focus.

CAMERA & QUALITY:

Professional commercial product photography.

High-end studio camera look.

85mm lens aesthetic.

Natural depth of field.

High dynamic range.

Extremely detailed textures.

Sharp focus on the product.

Realistic optical characteristics.

Physically accurate shadows and reflections.

Photorealistic rendering.

Premium cinematic color grading.

SUBTLE ENHANCEMENT:

Improve the overall photographic quality, lighting, atmosphere and presentation dramatically while keeping the actual product completely unchanged.

The final image should look like it was photographed for a premium international advertising campaign.

FORMAT:

Vertical 4:5 composition optimized for Instagram, social media and online product presentation.

NEGATIVE CONSTRAINTS:

No product redesign.
No altered proportions.
No geometry distortion.
No shape changes.
No color changes.
No fake materials.
No invented features.
No replacement product.
No fake branding.
No altered logo.
No distorted text on the product.
No unnecessary props touching the product.
No excessive reflections.
No unrealistic shadows.
No plastic-looking surfaces.
No cartoon style.
No illustration.
No CGI appearance.
No text.
No captions.
No watermark.
"""
}


# =========================
# FLASK
# =========================

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "HooshMasnoei Prompt Bot is running."


@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    try:
        update = Update.de_json(
            request.get_json(force=True),
            bot_app.bot
        )

        asyncio.run_coroutine_threadsafe(
            bot_app.process_update(update),
            loop
        )

        return "OK", 200

    except Exception as e:
        print("Webhook error:", e)
        return "ERROR", 500


# =========================
# USER STATE
# =========================

LAST_PROMPT = {}


# =========================
# MEMBERSHIP CHECK
# =========================

async def is_user_member(user_id: int) -> bool:
    try:
        member = await bot_app.bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:
        print("Membership check error:", e)
        return False


# =========================
# SEND PROMPT
# =========================

async def send_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    prompt_id: str
):

    if prompt_id not in PROMPTS:
        await update.message.reply_text(
            "❌ این پرامپت وجود ندارد یا لینک آن اشتباه است."
        )
        return

    user_id = update.effective_user.id

    if not await is_user_member(user_id):

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
            "🔒 برای دریافت پرامپت ابتدا در کانال ما عضو شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    LAST_PROMPT[user_id] = prompt_id

    await update.message.reply_text(
        "🎁 پرامپت کامل شما:\n\n"
        + PROMPTS[prompt_id].strip()
    )


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    args = context.args

    # Deep Link
    if args:

        prompt_id = args[0].lower().strip()

        if prompt_id in PROMPTS:
            await send_prompt(
                update,
                context,
                prompt_id
            )
            return

        await update.message.reply_text(
            "❌ این پرامپت وجود ندارد یا لینک آن اشتباه است."
        )

        return

    # Normal /start
    keyboard = [
        [
            InlineKeyboardButton(
                "🎁 دریافت پرامپت",
                callback_data="last"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ راهنما",
                callback_data="help"
            )
        ]
    ]

    await update.message.reply_text(
        "🤖 سلام!\n\n"
        "به ربات دریافت پرامپت‌های کانال هوش مصنوعی خوش آمدید. 🔵\n\n"
        "برای دریافت آخرین پرامپت از دکمه زیر استفاده کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# PROMPT COMMAND
# =========================

async def prompt_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    prompt_id = LAST_PROMPT.get(user_id)

    if not prompt_id:
        await update.message.reply_text(
            "❌ هنوز پرامپتی برای شما ثبت نشده است."
        )
        return

    await send_prompt(
        update,
        context,
        prompt_id
    )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ راهنمای ربات\n\n"
        "🎁 برای دریافت پرامپت، روی لینک دریافت آن در پست کانال بزنید.\n\n"
        "🔒 برای دریافت پرامپت باید عضو کانال باشید.\n\n"
        "/start - شروع ربات\n"
        "/prompt - دریافت مجدد آخرین پرامپت\n"
        "/help - راهنما"
    )


# =========================
# CALLBACKS
# =========================

async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    data = query.data

    # Check membership
    if data.startswith("check:"):

        prompt_id = data.split(":", 1)[1]

        if prompt_id == "last":
            prompt_id = LAST_PROMPT.get(user_id)

        if not prompt_id or prompt_id not in PROMPTS:

            await query.edit_message_text(
                "❌ این پرامپت وجود ندارد یا لینک آن اشتباه است."
            )

            return

        if await is_user_member(user_id):

            LAST_PROMPT[user_id] = prompt_id

            await query.edit_message_text(
                "✅ عضویت شما تأیید شد!\n\n"
                "🎁 پرامپت کامل:\n\n"
                + PROMPTS[prompt_id].strip()
            )

        else:

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

            await query.edit_message_text(
                "❌ هنوز عضو کانال نیستید.\n\n"
                "ابتدا عضو شوید و سپس دوباره روی «بررسی عضویت» بزنید.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        return

    # Last prompt
    if data == "last":

        prompt_id = LAST_PROMPT.get(user_id)

        if not prompt_id or prompt_id not in PROMPTS:

            await query.edit_message_text(
                "❌ هنوز پرامپتی برای شما ثبت نشده است."
            )

            return

        if not await is_user_member(user_id):

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
                        callback_data=f"check:last"
                    )
                ]
            ]

            await query.edit_message_text(
                "🔒 ابتدا باید عضو کانال شوید.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return

        await query.edit_message_text(
            "🎁 پرامپت کامل:\n\n"
            + PROMPTS[prompt_id].strip()
        )

        return

    # Help
    if data == "help":

        await query.edit_message_text(
            "ℹ️ راهنمای ربات\n\n"
            "🎁 برای دریافت پرامپت، روی لینک آن در پست کانال بزنید.\n\n"
            "🔒 برای دریافت پرامپت باید عضو کانال باشید.\n\n"
            "/start - شروع ربات\n"
            "/prompt - دریافت مجدد آخرین پرامپت\n"
            "/help - راهنما"
        )


# =========================
# BOT SETUP
# =========================

async def post_init(application: Application):

    await application.bot.set_my_commands([
        ("start", "🏠 شروع"),
        ("prompt", "🎁 دریافت مجدد پرامپت"),
        ("help", "ℹ️ راهنما"),
    ])


bot_app = (
    Application.builder()
    .token(BOT_TOKEN)
    .post_init(post_init)
    .build()
)

bot_app.add_handler(
    CommandHandler("start", start)
)

bot_app.add_handler(
    CommandHandler("prompt", prompt_command)
)

bot_app.add_handler(
    CommandHandler("help", help_command)
)

bot_app.add_handler(
    CallbackQueryHandler(button_callback)
)


# =========================
# TELEGRAM WORKER
# =========================

loop = asyncio.new_event_loop()


def telegram_worker():

    asyncio.set_event_loop(loop)

    async def runner():

        await bot_app.initialize()
        await bot_app.start()

        webhook_url = (
            RENDER_EXTERNAL_URL
            + WEBHOOK_PATH
        )

        await bot_app.bot.set_webhook(
            url=webhook_url
        )

        print(
            "Webhook set:",
            webhook_url
        )

        await asyncio.Event().wait()

    loop.run_until_complete(runner())


# =========================
# START
# =========================

if __name__ == "__main__":

    worker_thread = threading.Thread(
        target=telegram_worker,
        daemon=True
    )

    worker_thread.start()

    app.run(
        host="0.0.0.0",
        port=PORT
    )
