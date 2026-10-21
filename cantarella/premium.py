from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from database.db import db
from config import ADMINS
from datetime import date, datetime, timedelta
from logger import LOGGER

logger = LOGGER(__name__)


# ======================================================
# HELPERS
# ======================================================

async def get_user_data(user):
    if not user:
        return {}

    user_id = user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, user.first_name)

    return await db.col.find_one({"id": user_id}) or {}


def get_plan_text(user_data):
    is_premium = user_data.get("is_premium", False)
    expiry = user_data.get("premium_expiry")
    daily_usage = user_data.get("daily_usage", 0) or 0
    total_saves = user_data.get("total_saves", 0) or 0

    if is_premium:
        if expiry:
            try:
                if isinstance(expiry, datetime):
                    exp_date = expiry.date()
                elif isinstance(expiry, date):
                    exp_date = expiry
                else:
                    exp_date = date.fromisoformat(str(expiry)[:10])

                days_left = (exp_date - date.today()).days
                expiry_text = (
                    f"<code>{exp_date.isoformat()}</code> "
                    f"({days_left} days left)"
                )
            except (ValueError, TypeError):
                expiry_text = "<code>Active</code>"
        else:
            expiry_text = "<code>Permanent</code>"

        return (
            "<b>👑 Premium Status: Active</b>\n\n"
            f"<b>📅 Expiry:</b> {expiry_text}\n\n"
            "<b>♾️ Daily Tokens:</b> Unlimited\n"
            "<b>♾️ Batch Limit:</b> Unlimited\n"
            f"<b>📊 Total Lifetime Saves:</b> "
            f"<code>{total_saves}</code>\n\n"
            "<i>Thank you for supporting the bot! 🎉</i>"
        )

    daily_limit = 10
    tokens_left = max(0, daily_limit - daily_usage)

    return (
        "<b>👤 Plan: Free Tier</b>\n\n"
        f"<b>🎫 Daily Tokens:</b> "
        f"<code>{tokens_left} / {daily_limit}</code>\n"
        "<b>📦 File Size Limit:</b> <code>2 GB</code>\n"
        f"<b>📊 Total Lifetime Saves:</b> "
        f"<code>{total_saves}</code>\n\n"
        "<i>Upgrade to Premium for unlimited access! 🚀</i>"
    )


def get_plan_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 View Premium Plans",
                callback_data="premium_plans_btn",
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url="https://t.me/Tg_jiro/24",
            )
        ],
    ])


# ======================================================
# /myplan
# ======================================================

@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan(client: Client, message: Message):
    if not message.from_user:
        return

    try:
        user_data = await get_user_data(message.from_user)

        await message.reply_text(
            get_plan_text(user_data),
            reply_markup=get_plan_buttons(),
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception:
        logger.exception("Failed to show user plan")
        await message.reply_text(
            "❌ Plan load nahi ho paaya. Please try again later."
        )


# ======================================================
# /premium
# ======================================================

async def show_premium_plans(message_or_query):
    text = (
        "<b>💎 Premium Plans</b>\n\n"
        "<blockquote>"
        "<b>Why Go Premium?</b>\n"
        "• ♾️ <b>Unlimited</b> Daily Saves\n"
        "• 📂 <b>4GB+</b> File Support\n"
        "• ⚡ <b>Zero</b> Processing Delay\n"
        "• 🖼 <b>Custom</b> Thumbnails & Captions\n"
        "• 👑 <b>Premium</b> Badge\n"
        "</blockquote>\n\n"
        "<b>💲 Pricing:</b>\n"
        "• <b>1 Month:</b> ₹50 / $1\n"
        "• <b>Lifetime:</b> ₹200 / $4\n\n"
        "<i>Tap below to contact admin and buy Premium.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Buy Premium Now",
                url="https://t.me/Tg_jiro/24",
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back to My Plan",
                callback_data="myplan_back_btn",
            )
        ],
    ])

    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    else:
        await message_or_query.edit_message_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command("premium") & filters.private)
async def premium_info(client: Client, message: Message):
    await show_premium_plans(message)


# ======================================================
# ADMIN: /add_premium
# ======================================================

@Client.on_message(
    filters.command("add_premium")
    & filters.user(ADMINS)
    & filters.private
)
async def add_premium_admin(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(
            "<b>⚠️ Admin Usage:</b>\n"
            "<code>/add_premium &lt;user_id&gt; &lt;days&gt;</code>\n\n"
            "<i>Use 0 for permanent Premium.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])

        if days < 0:
            return await message.reply_text(
                "❌ Days cannot be negative."
            )

        if days == 0:
            expiry_date = None
            duration_text = "Permanent"
        else:
            expiry_date = (
                date.today() + timedelta(days=days)
            ).isoformat()
            duration_text = f"{days} days (until {expiry_date})"

        await db.add_premium(user_id, expiry_date)

        await message.reply_text(
            "<b>✅ Premium Added Successfully</b>\n\n"
            f"<b>User ID:</b> <code>{user_id}</code>\n"
            f"<b>Duration:</b> {duration_text}",
            parse_mode=enums.ParseMode.HTML,
        )

    except ValueError:
        await message.reply_text(
            "❌ User ID aur days numbers hone chahiye."
        )
    except Exception:
        logger.exception("Failed to add Premium")
        await message.reply_text(
            "❌ Premium add nahi ho paaya. Logs check karo."
        )


# ======================================================
# ADMIN: /remove_premium
# ======================================================

@Client.on_message(
    filters.command("remove_premium")
    & filters.user(ADMINS)
    & filters.private
)
async def remove_premium_admin(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>⚠️ Usage:</b>\n"
            "<code>/remove_premium &lt;user_id&gt;</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        user_id = int(message.command[1])
        await db.remove_premium(user_id)

        await message.reply_text(
            f"✅ Premium removed from <code>{user_id}</code>.",
            parse_mode=enums.ParseMode.HTML,
        )

    except ValueError:
        await message.reply_text(
            "❌ User ID number hona chahiye."
        )
    except Exception:
        logger.exception("Failed to remove Premium")
        await message.reply_text(
            "❌ Premium remove nahi ho paaya. Logs check karo."
        )


# ======================================================
# CALLBACK: VIEW PREMIUM PLANS
# ======================================================

@Client.on_callback_query(
    filters.regex("^premium_plans_btn$")
)
async def premium_plans_callback(
    client: Client,
    callback_query: CallbackQuery,
):
    await callback_query.answer()
    await show_premium_plans(callback_query)


# ======================================================
# CALLBACK: BACK TO MY PLAN
# ======================================================

@Client.on_callback_query(
    filters.regex("^myplan_back_btn$")
)
async def myplan_back_callback(
    client: Client,
    callback_query: CallbackQuery,
):
    await callback_query.answer()

    user = callback_query.from_user
    if not user:
        return

    try:
        user_data = await get_user_data(user)

        await callback_query.message.edit_text(
            get_plan_text(user_data),
            reply_markup=get_plan_buttons(),
            parse_mode=enums.ParseMode.HTML,
        )

    except Exception:
        logger.exception("Failed to return to user plan")

        await callback_query.message.reply_text(
            "❌ Plan load nahi ho paaya. /myplan command try karo."
        )