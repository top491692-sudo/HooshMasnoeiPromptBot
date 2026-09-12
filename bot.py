import os
import asyncio
import threading
import logging
from flask import Flask, request

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")

CHANNEL_USERNAME = "@HooshMasnoei_Tools"

WEBHOOK_PATH = "/telegram-webhook"


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# PROMPTS
# ============================================================
#
# Every prompt has its own unique ID.
#
# Channel button:
#
# https://t.me/HooshMasnoeiPromptBot?start=ID
#
# Example:
#
# https://t.me/HooshMasnoeiPromptBot?start=product
#
# ============================================================


PROMPTS = {

    # ========================================================
    # 1. PRODUCT COMMERCIAL
    # ========================================================

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
""",


    # ========================================================
    # 2. CINEMATIC PORTRAIT
    # ========================================================

    "cinematic": """
Transform the subject in the reference image into an ultra-premium cinematic portrait.

IDENTITY PRESERVATION — ABSOLUTE PRIORITY:

Use the uploaded image as the primary and exact identity reference.

Keep the EXACT SAME PERSON.

Preserve the person's identity completely and accurately, including:

facial structure,
facial proportions,
face shape,
eyes and eye shape,
eyebrows,
nose,
lips,
cheekbones,
jawline,
chin,
forehead,
hairline,
hairstyle,
hair texture,
skin tone,
natural skin texture,
age,
natural facial asymmetry,
and every other recognizable facial characteristic.

Do NOT generate a different person.

Do NOT redesign, beautify, reshape or reinterpret the face.

Do NOT change ethnicity, age, facial proportions or recognizable features.

The final result must remain immediately recognizable as the exact same person from the reference image.

CINEMATIC TRANSFORMATION:

Transform the ordinary smartphone photograph into a sophisticated cinematic movie-style portrait while keeping the person completely authentic.

Create a premium Hollywood-inspired visual atmosphere with realistic photographic characteristics.

LIGHTING:

Use dramatic cinematic lighting with:

a soft directional key light,
subtle fill light,
controlled rim lighting,
natural shadow transitions,
soft highlights,
realistic skin illumination,
and subtle atmospheric light.

Create dimensional lighting without overexposing the skin or creating artificial HDR effects.

BACKGROUND:

Create an elegant dark cinematic background with subtle atmospheric depth.

Use realistic environmental separation, soft bokeh and controlled background highlights.

The background should complement the subject without distracting from the face.

CAMERA:

Professional portrait photography.

85mm portrait lens aesthetic.

Natural optical compression.

Realistic depth of field.

Sharp focus on the subject's face.

Soft natural background falloff.

High dynamic range.

Realistic lens characteristics.

COLOR GRADING:

Apply sophisticated cinematic color grading.

Use controlled contrast, natural skin tones, subtle cool and warm color separation, realistic highlights and deep but detailed shadows.

Add extremely subtle film grain for a premium cinematic texture.

Keep the overall image photorealistic.

SKIN & DETAILS:

Preserve realistic skin texture and natural facial details.

Do not create plastic-looking skin.

Do not excessively smooth the face.

Keep pores, fine facial details and natural skin characteristics believable.

Do not add excessive makeup or artificial beauty retouching.

POSE & EXPRESSION:

Keep the original person's general pose, facial expression and camera angle whenever possible.

Do not dramatically alter the person's identity or expression.

The final portrait should feel natural, confident and authentic.

COMPOSITION:

Create a sophisticated vertical portrait composition.

Use balanced framing and professional visual hierarchy.

Keep the subject as the clear visual focus.

Use subtle negative space where appropriate.

OUTPUT:

Vertical 4:5 composition.

Ultra-photorealistic.

Extremely detailed.

Professional commercial portrait photography.

Premium cinematic movie aesthetic.

Natural realistic lighting.

Realistic skin texture.

High-end photographic quality.

NEGATIVE CONSTRAINTS:

No face replacement.
No identity change.
No different person.
No facial redesign.
No altered facial proportions.
No face reshaping.
No age change.
No ethnicity change.
No exaggerated beauty.
No plastic skin.
No excessive skin smoothing.
No unrealistic makeup.
No cartoon style.
No illustration.
No CGI appearance.
No distorted anatomy.
No unnatural eyes.
No artificial facial features.
No excessive HDR.
No extreme sharpening.
No unrealistic shadows.
No text.
No logo.
No watermark.
""",


    # ========================================================
    # 3. OBJECT / PERSON REMOVAL
    # ========================================================

    "object_remove": """
Edit the uploaded image as a professional photo retoucher.

OBJECT REMOVAL — ABSOLUTE PRIORITY:

Remove ONLY the unwanted object or person specified by the user:

[UNWANTED OBJECT OR PERSON]

Location in the image:

[LOCATION]

Do not remove, replace, redesign or modify anything else.

PRESERVE THE ORIGINAL IMAGE:

Keep the main subject completely unchanged.

Preserve:

- facial identity
- facial features
- skin tone
- hairstyle
- facial expression
- body proportions
- pose
- clothing
- accessories
- product shape and details
- logos and visible text
- camera angle
- framing
- crop
- perspective
- depth of field
- focus
- overall composition
- colors
- exposure
- original lighting style

Do not beautify, retouch, reshape or reinterpret the main subject.

Do not change any unrelated part of the image.

SEAMLESS BACKGROUND RECONSTRUCTION:

After removing the specified unwanted object or person, naturally reconstruct the area that was previously hidden.

Use the surrounding image as the primary visual reference.

Continue the existing:

- textures
- surfaces
- patterns
- architectural lines
- perspective
- depth
- colors
- lighting
- shadows
- reflections
- environmental details

The reconstructed area must look like it was naturally captured by the original camera.

Do not invent unnecessary objects or details.

LIGHTING CONSISTENCY:

Match the original image's lighting direction, intensity, color temperature, exposure and shadow behavior.

If the removed element casts a visible shadow, reflection or secondary visual effect, remove or reconstruct that effect naturally as part of the edit.

Do not introduce new lighting.

Do not relight the entire image.

Do not change the mood or color grading of the original photograph.

TEXTURE & PERSPECTIVE:

Maintain the correct scale, direction and continuity of surrounding textures.

For walls, floors, bricks, tiles, wood, grass, water, fabric or other patterned surfaces, continue the existing pattern naturally.

Keep straight architectural lines straight.

Keep perspective lines consistent.

Avoid duplicated or repeated textures.

Avoid blurry patches.

Avoid visible seams.

Avoid unnatural texture stretching.

SUBJECT PROTECTION:

If the unwanted object is close to the main subject, carefully preserve the subject's boundaries.

Do not alter:

hands,
face,
hair,
clothing,
jewelry,
body shape,
product edges,
important objects,
logos,
signs,
or other intentional details.

If the unwanted object overlaps an important subject, preserve the original subject rather than inventing or reconstructing it.

EDIT SCOPE:

This is a precise local edit.

Change ONLY the requested unwanted object or person and the minimum area required to reconstruct the space behind it.

Everything outside the edited region must remain visually consistent with the original image.

PHOTOREALISM:

The final image must look like an authentic photograph captured with the original camera.

Maintain realistic:

- texture
- sharpness
- grain
- depth
- lighting
- shadows
- reflections
- optical characteristics

Do not make the edited area look cleaner or sharper than the surrounding image.

Do not create an artificial AI-generated appearance.

FINAL QUALITY CHECK:

Before producing the final image, verify that:

- the requested object or person is completely removed
- no fragments of the removed element remain
- no unwanted shadow or reflection remains
- the reconstructed area matches its surroundings
- perspective lines remain correct
- textures remain continuous
- lighting remains consistent
- the main subject remains unchanged
- no new objects were accidentally introduced
- there are no visible seams or cloning artifacts
- the final image remains photorealistic

NEGATIVE CONSTRAINTS:

No unwanted object remaining.
No unwanted person remaining.
No object fragments.
No duplicated objects.
No repeated textures.
No blurry patches.
No visible seams.
No texture distortion.
No warped perspective.
No changed facial features.
No identity change.
No body deformation.
No clothing changes.
No color changes.
No global relighting.
No unnecessary retouching.
No invented objects.
No CGI appearance.
No illustration.
No cartoon style.
No text generation.
No watermark.
""",


    # ========================================================
    # 4. BACKGROUND REPLACEMENT
    # ========================================================

    "background_replace": """
Edit the uploaded image as a professional high-end photo compositor.

BACKGROUND REPLACEMENT — ABSOLUTE PRIORITY:

Replace ONLY the background behind the main subject with:

[NEW BACKGROUND]

The new background must look naturally photographed together with the original subject.

SUBJECT LOCK — ABSOLUTE:

Keep the EXACT SAME MAIN SUBJECT.

Do not regenerate, redesign, replace or reinterpret the subject.

Preserve exactly:

- facial identity
- facial structure
- face shape
- eyes
- eyebrows
- nose
- lips
- jawline
- skin tone
- natural skin texture
- hairstyle
- hairline
- age
- body proportions
- pose
- facial expression
- clothing
- accessories
- hands
- shoes
- product details if present
- all recognizable characteristics

Do not beautify the subject.

Do not change the subject's face.

Do not change the person's body.

Do not change the clothing.

Do not change the pose.

Do not change the expression.

Do not replace the person with a different person.

The subject must remain immediately recognizable as the exact person from the uploaded image.

EDIT SCOPE:

Only the background is editable.

Treat the entire main subject as locked content.

Do not modify any part of the subject unless a tiny edge adjustment is absolutely necessary to create a natural transition with the new background.

BACKGROUND:

Create the requested new environment:

[NEW BACKGROUND]

Design the environment according to the requested scene while maintaining realistic photographic characteristics.

The new background should have believable:

- architecture
- surfaces
- depth
- scale
- environmental details
- atmospheric perspective
- lighting
- shadows
- reflections when appropriate

Do not create unnecessary objects.

Do not overcrowd the scene.

Do not allow the background to distract from the main subject.

CAMERA & PERSPECTIVE:

Match the original camera position, camera height, viewing angle, focal perspective and composition.

The new background must have the correct perspective relative to the subject.

Maintain realistic scale.

Keep the horizon and major perspective lines consistent with the original camera position.

Do not make the subject appear too large or too small relative to the new environment.

LIGHTING MATCH:

Analyze the lighting already present on the subject.

Build the new background around the same lighting direction and photographic conditions.

Match:

- light direction
- light intensity
- color temperature
- shadow softness
- ambient illumination
- contrast
- exposure
- highlight behavior

The subject must not look cut out and pasted onto the new environment.

The lighting relationship between the subject and background must feel physically believable.

CONTACT SHADOW:

If the subject is standing, sitting or touching a surface, create a realistic contact shadow where appropriate.

The shadow must match the new environment's:

- light direction
- softness
- intensity
- distance
- surface material

Do not create a dark artificial outline around the subject.

EDGE QUALITY:

Preserve natural edges around:

- hair
- individual hair strands
- ears
- shoulders
- clothing
- hands
- fingers
- shoes
- transparent or semi-transparent materials

Do not create:

- white halos
- dark halos
- cutout edges
- jagged edges
- excessive blur
- artificial outlines

Hair and fine details should naturally interact with the new background.

DEPTH OF FIELD:

Create depth of field consistent with the original camera and lens characteristics.

If the original image has background blur, maintain a realistic level of blur in the new background.

If the original image is sharp throughout, do not introduce excessive artificial bokeh.

The depth relationship between the subject and background must look optically believable.

COLOR & IMAGE CHARACTER:

Maintain the original photographic character of the image.

Do not unnecessarily change:

- skin tone
- clothing colors
- exposure
- contrast
- saturation
- sharpness
- image grain

The new background should be color-balanced with the original photograph.

The final image should look like one photograph rather than two images composited together.

PHOTOREALISM:

The final result must look like an authentic photograph captured with a real camera.

Use realistic:

- optical characteristics
- depth
- perspective
- lighting
- shadows
- reflections
- textures
- atmospheric depth
- natural image noise

Avoid the artificial appearance commonly produced by AI-generated backgrounds.

FINAL QUALITY CHECK:

Before producing the final image, verify:

- the main subject is exactly preserved
- the person's identity has not changed
- the face has not changed
- the pose has not changed
- the clothing has not changed
- the background is completely replaced
- the new background has correct perspective
- the lighting matches the subject
- the color temperature is coherent
- contact shadows are realistic
- hair edges are natural
- there are no halos
- there are no cutout artifacts
- there are no distorted body parts
- there are no duplicated objects
- there are no unnecessary objects
- the final image looks like one authentic photograph

NEGATIVE CONSTRAINTS:

No identity change.
No face regeneration.
No different person.
No face redesign.
No body reshaping.
No pose change.
No clothing change.
No hairstyle change.
No skin tone change.
No artificial beauty retouching.
No cutout appearance.
No white halo.
No dark halo.
No jagged edges.
No excessive blur.
No artificial bokeh.
No incorrect perspective.
No floating subject.
No unrealistic contact shadow.
No mismatched lighting.
No inconsistent color temperature.
No CGI appearance.
No illustration.
No cartoon style.
No text.
No captions.
No logo.
No watermark.
""",
}


# ============================================================
# LAST PROMPT
# ============================================================

LAST_PROMPT = None


# ============================================================
# PROMPT FORMATTER
# ============================================================

def format_prompt(prompt_id: str) -> str:
    """
    Format a prompt inside a Telegram Markdown code block.
    """

    prompt = PROMPTS[prompt_id].strip()

    return (
        "🎁 *پرامپت کامل شما:*\n\n"
        "```\n"
        + prompt
        + "\n```"
    )


# ============================================================
# MEMBERSHIP CHECK
# ============================================================

async def is_user_member(
    user_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:

    try:

        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id,
        )

        return member.status in {
            "member",
            "administrator",
            "creator",
        }

    except Exception as e:

        logger.warning(
            "Membership check failed: %s",
            e
        )

        return False


# ============================================================
# CHANNEL JOIN MESSAGE
# ============================================================

def channel_join_keyboard() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 عضویت در کانال",
                url="https://t.me/HooshMasnoei_Tools",
            )
        ],
        [
            InlineKeyboardButton(
                "✅ بررسی عضویت",
                callback_data="check:last",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def send_membership_required(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = (
        "🔒 برای دریافت پرامپت ابتدا باید در کانال عضو شوید.\n\n"
        "بعد از عضویت روی «✅ بررسی عضویت» بزنید."
    )

    if update.callback_query:

        await update.callback_query.message.reply_text(
            text,
            reply_markup=channel_join_keyboard(),
        )

    elif update.effective_message:

        await update.effective_message.reply_text(
            text,
            reply_markup=channel_join_keyboard(),
        )


# ============================================================
# /START
# ============================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global LAST_PROMPT

    user = update.effective_user

    if not user:
        return

    # --------------------------------------------------------
    # Determine requested prompt
    # --------------------------------------------------------

    prompt_id = None

    if context.args:

        requested_id = context.args[0].strip().lower()

        if requested_id in PROMPTS:

            prompt_id = requested_id

    # --------------------------------------------------------
    # If valid prompt was requested, remember it
    # --------------------------------------------------------

    if prompt_id:

        LAST_PROMPT = prompt_id

    # --------------------------------------------------------
    # Membership check
    # --------------------------------------------------------

    if not await is_user_member(
        user.id,
        context,
    ):

        await send_membership_required(
            update,
            context,
        )

        return

    # --------------------------------------------------------
    # Valid prompt
    # --------------------------------------------------------

    if prompt_id:

        await update.effective_message.reply_text(
            format_prompt(prompt_id),
            parse_mode=ParseMode.MARKDOWN,
        )

        return

    # --------------------------------------------------------
    # Normal /start
    # --------------------------------------------------------

    text = (
        "🤖 *سلام! به ربات پرامپت هوش مصنوعی خوش اومدی.*\n\n"
        "📌 برای دریافت پرامپت، از لینک اختصاصی هر پست وارد ربات شو.\n\n"
        "مثال:\n"
        "`https://t.me/HooshMasnoeiPromptBot?start=product`\n\n"
        "✨ پرامپت‌های آماده و حرفه‌ای برای تولید و ویرایش تصویر."
    )

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
    )


# ============================================================
# /PROMPT
# ============================================================

async def prompt_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global LAST_PROMPT

    user = update.effective_user

    if not user:
        return

    # --------------------------------------------------------
    # Membership
    # --------------------------------------------------------

    if not await is_user_member(
        user.id,
        context,
    ):

        await send_membership_required(
            update,
            context,
        )

        return

    # --------------------------------------------------------
    # Requested ID
    # --------------------------------------------------------

    if not context.args:

        await update.effective_message.reply_text(
            "❌ شناسه پرامپت را وارد کنید.\n\n"
            "مثال:\n"
            "/prompt product"
        )

        return

    prompt_id = context.args[0].strip().lower()

    # --------------------------------------------------------
    # Check ID
    # --------------------------------------------------------

    if prompt_id not in PROMPTS:

        await update.effective_message.reply_text(
            "❌ این شناسه پرامپت وجود ندارد."
        )

        return

    # --------------------------------------------------------
    # Remember
    # --------------------------------------------------------

    LAST_PROMPT = prompt_id

    # --------------------------------------------------------
    # Send prompt
    # --------------------------------------------------------

    await update.effective_message.reply_text(
        format_prompt(prompt_id),
        parse_mode=ParseMode.MARKDOWN,
    )


# ============================================================
# /HELP
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = (
        "ℹ️ *راهنمای ربات*\n\n"
        "📌 هر پست کانال یک شناسه اختصاصی دارد.\n\n"
        "برای مثال:\n"
        "`/prompt product`\n\n"
        "یا از لینک مستقیم همان پست وارد ربات شوید.\n\n"
        "🛍️ product — تبلیغ حرفه‌ای محصول\n"
        "🎬 cinematic — پرتره سینمایی\n"
        "🪄 object_remove — حذف اشیا و افراد\n"
        "🌆 background_replace — تعویض پس‌زمینه"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
    )


# ============================================================
# CALLBACK QUERY
# ============================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global LAST_PROMPT

    query = update.callback_query

    if not query:
        return

    await query.answer()

    user = query.from_user

    # --------------------------------------------------------
    # Membership check
    # --------------------------------------------------------

    if not await is_user_member(
        user.id,
        context,
    ):

        await query.message.reply_text(
            "🔒 هنوز عضویت شما در کانال تأیید نشده است.\n\n"
            "ابتدا عضو کانال شوید و دوباره بررسی کنید.",
            reply_markup=channel_join_keyboard(),
        )

        return

    # --------------------------------------------------------
    # Callback data
    # --------------------------------------------------------

    data = query.data or ""

    # --------------------------------------------------------
    # Check specific prompt
    # --------------------------------------------------------

    if data.startswith("check:"):

        prompt_id = data.split(":", 1)[1]

        if prompt_id == "last":

            prompt_id = LAST_PROMPT

        if not prompt_id:

            await query.message.reply_text(
                "❌ هنوز پرامپتی انتخاب نشده است."
            )

            return

        if prompt_id not in PROMPTS:

            await query.message.reply_text(
                "❌ این پرامپت پیدا نشد."
            )

            return

        LAST_PROMPT = prompt_id

        await query.message.reply_text(
            format_prompt(prompt_id),
            parse_mode=ParseMode.MARKDOWN,
        )

        return

    # --------------------------------------------------------
    # Help
    # --------------------------------------------------------

    if data == "help":

        await help_command(
            update,
            context,
        )

        return

    # --------------------------------------------------------
    # Last prompt
    # --------------------------------------------------------

    if data == "last":

        if not LAST_PROMPT:

            await query.message.reply_text(
                "❌ هنوز پرامپتی انتخاب نشده است."
            )

            return

        await query.message.reply_text(
            format_prompt(LAST_PROMPT),
            parse_mode=ParseMode.MARKDOWN,
        )

        return


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():

    return "HooshMasnoeiPromptBot is running."


@app.route("/health", methods=["GET"])
def health():

    return "OK"


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================

telegram_application = None


@app.route(
    WEBHOOK_PATH,
    methods=["POST"],
)
def telegram_webhook():

    global telegram_application

    if telegram_application is None:

        return "Bot not ready", 503

    try:

        update_data = request.get_json(
            force=True
        )

        update = Update.de_json(
            update_data,
            telegram_application.bot,
        )

        asyncio.run_coroutine_threadsafe(
            telegram_application.process_update(update),
            bot_loop,
        )

        return "OK"

    except Exception as e:

        logger.exception(
            "Webhook error: %s",
            e,
        )

        return "ERROR", 500


# ============================================================
# ASYNCIO LOOP
# ============================================================

bot_loop = asyncio.new_event_loop()


def run_bot_loop():

    asyncio.set_event_loop(
        bot_loop
    )

    bot_loop.run_forever()


bot_thread = threading.Thread(
    target=run_bot_loop,
    daemon=True,
)

bot_thread.start()


# ============================================================
# INITIALIZE TELEGRAM
# ============================================================

if not BOT_TOKEN:

    raise RuntimeError(
        "BOT_TOKEN environment variable is missing."
    )


telegram_application = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)


# ============================================================
# HANDLERS
# ============================================================

telegram_application.add_handler(
    CommandHandler(
        "start",
        start_command,
    )
)

telegram_application.add_handler(
    CommandHandler(
        "prompt",
        prompt_command,
    )
)

telegram_application.add_handler(
    CommandHandler(
        "help",
        help_command,
    )
)

telegram_application.add_handler(
    CallbackQueryHandler(
        callback_handler,
    )
)


# ============================================================
# START BOT
# ============================================================

async def initialize_bot():

    await telegram_application.initialize()

    await telegram_application.start()

    # --------------------------------------------------------
    # Set webhook
    # --------------------------------------------------------

    if RENDER_EXTERNAL_URL:

        webhook_url = (
            RENDER_EXTERNAL_URL
            + WEBHOOK_PATH
        )

        await telegram_application.bot.set_webhook(
            url=webhook_url
        )

        logger.info(
            "Webhook set to: %s",
            webhook_url,
        )

    else:

        logger.warning(
            "RENDER_EXTERNAL_URL is not set. "
            "Webhook was not configured."
        )


asyncio.run_coroutine_threadsafe(
    initialize_bot(),
    bot_loop,
).result()


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Starting Flask server on port %s",
        PORT,
    )

    app.run(
        host="0.0.0.0",
        port=PORT,
    )
