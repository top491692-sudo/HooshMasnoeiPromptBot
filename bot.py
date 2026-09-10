import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

CHANNEL_USERNAME = "@HooshMasnoei_Tools"

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_id = context.args[0] if context.args else "cinematic"

    keyboard = [
        [InlineKeyboardButton(
            "🔵 عضویت در کانال",
            url="https://t.me/HooshMasnoei_Tools"
        )],
        [InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data=f"check:{prompt_id}"
        )]
    ]

    await update.message.reply_text(
        "🔐 برای دریافت پرامپت، ابتدا عضو کانال ما شو:\n\n"
        "🔵 @HooshMasnoei_Tools\n\n"
        "بعد از عضویت، روی «✅ بررسی عضویت» بزن.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prompt_id = query.data.split(":", 1)[1]

    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=query.from_user.id
        )

        if member.status in ["member", "administrator", "creator"]:
            prompt = PROMPTS.get(prompt_id)

            if not prompt:
                await query.message.reply_text(
                    "❌ این پرامپت پیدا نشد."
                )
                return

            await query.message.reply_text(
                "🎉 عضویتت تأیید شد!\n\n"
                "🎁 این هم پرامپت:\n\n"
                f"```text\n{prompt}\n```",
                parse_mode="Markdown"
            )

        else:
            await query.answer(
                "❌ هنوز عضو کانال نیستی!",
                show_alert=True
            )

    except Exception:
        await query.message.reply_text(
            "⚠️ در بررسی عضویت مشکلی پیش آمد. "
            "مطمئن شو ربات در کانال ادمین است و دوباره امتحان کن."
        )


def main():
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN is not configured.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_membership, pattern=r"^check:"))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
