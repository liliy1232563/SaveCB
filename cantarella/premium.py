from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.db import db
from config import ADMINS
from datetime import date, datetime, timedelta
from logger import LOGGER

logger = LOGGER(__name__)

# ======================================================
# USER COMMANDS
# ======================================================

# /myplan
@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    user_data = await db.col.find_one({"id": user_id}) or {}

    is_premium = user_data.get("is_premium", False)
    expiry = user_data.get("premium_expiry")
    daily_usage = user_data.get("daily_usage", 0)
    total_saves = user_data.get("total_saves", 0)

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

        plan_text = (
            "<b>👑 Premium Status: Active</b>\n\n"
            f"<b>📅 Expiry:</b> {expiry_text}\n\n"
            "<b>♾️ Daily Tokens:</b> Unlimited\n"
            "<b>♾️ Batch Limit:</b> Unlimited\n"
            f"<b>📊 Total Lifetime Saves:</b> <code>{total_saves}</code>\n\n"
            "<i>Thank you for supporting the bot! 🎉</i>"
        )
    else:
        daily_limit = 10
        tokens_left = max(0, daily_limit - daily_usage)

        plan_text = (
            "<b>👤 Plan: Free Tier</b>\n\n"
            f"<b>🎫 Daily Tokens:</b> "
            f"<code>{tokens_left} / {daily_limit}</code>\n"
            "<b>📦 File Size Limit:</b> <code>2 GB</code>\n"
            f"<b>📊 Total Lifetime Saves:</b> <code>{total_saves}</code>\n\n"
            "<i>Upgrade to Premium for unlimited access! 🚀</i>"
        )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 View Premium Plans",
                callback_data="premium_plans_btn"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url="https://t.me/Tg_jiro/24"
            )
        ]
    ])

    await message.reply_text(
        plan_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )


# ======================================================
# /premium
# ======================================================

@Client.on_message(filters.command("premium") & filters.private)
async def premium_info(client: Client, message: Message):
    await show_premium_plans(message)


# ======================================================
# PREMIUM PLANS VIEW
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
        "<i>Tap below to view payment details.</i>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Buy Premium Now",
                callback_data="buy_premium"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Back to My Plan",
                callback_data="myplan_back_btn"
            )
        ]
    ])

    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    else:
        await message_or_query.edit_message_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )


# ======================================================
# BUY PREMIUM CALLBACK
# Uses payment details configured in plugins/start.py
# ======================================================

@Client.on_callback_query(filters.regex("^buy_premium$"))
async def buy_premium_callback(
    client: Client,
    callback_query: CallbackQuery
):
    await callback_query.answer()

    try:
        from plugins.start import script, UPI_ID, QR_CODE, SUBSCRIPTION

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📸 Send Payment Proof",
                    url="https://t.me/EmptyJohan"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Close Menu",
                    callback_data="close_btn"
                )
            ]
        ])

        await callback_query.message.reply_photo(
            photo=SUBSCRIPTION,
            caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE),
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception:
        logger.exception("Failed to display premium payment details")
        await callback_query.message.reply_text(
            "❌ Payment details load nahi ho paaye. Please contact admin."
        )


# ======================================================
# BACK TO MY PLAN CALLBACK
# ======================================================

@Client.on_callback_query(filters.regex("^myplan_back_btn$"))
async def myplan_back_callback(
    client: Client,
    callback_query: CallbackQuery
):
    await callback_query.answer()

    if not callback_query.from_user:
        return

    user_id = callback_query.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(
            user_id,
            callback_query.from_user.first_name
        )

    user_data = await db.col.find_one({"id": user_id}) or {}

    is_premium = user_data.get("is_premium", False)
    expiry = user_data.get("premium_expiry")
    daily_usage = user_data.get("daily_usage", 0)
    total_saves = user_data.get("total_saves", 0)

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

        plan_text = (
            "<b>👑 Premium Status: Active</b>\n\n"
            f"<b>📅 Expiry:</b> {expiry_text}\n\n"
            "<b>♾️ Daily Tokens:</b> Unlimited\n"
            "<b>♾️ Batch Limit:</b> Unlimited\n"
            f"<b>📊 Total Lifetime Saves:</b> <code>{total_saves}</code>\n\n"
            "<i>Thank you for supporting the bot! 🎉</i>"
        )
    else:
        daily_limit = 10
        tokens_left = max(0, daily_limit - daily_usage)

        plan_text = (
            "<b>👤 Plan: Free Tier</b>\n\n"
            f"<b>🎫 Daily Tokens:</b> "
            f"<code>{tokens_left} / {daily_limit}</code>\n"
            "<b>📦 File Size Limit:</b> <code>2 GB</code>\n"
            f"<b>📊 Total Lifetime Saves:</b> <code>{total_saves}</code>\n\n"
            "<i>Upgrade to Premium for unlimited access! 🚀</i>"
        )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 View Premium Plans",
                callback_data="premium_plans_btn"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Contact Admin",
                url="https://t.me/Tg_jiro/24"
            )
        ]
    ])

    try:
        await callback_query.message.edit_text(
            plan_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        await callback_query.message.reply_text(
            plan_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )


# ======================================================
# ADMIN COMMANDS
# ======================================================

@Client.on_message(
    filters.command("add_premium") & filters.user(ADMINS) & filters.private
)
async def add_premium_admin(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(
            "<b>⚠️ Admin Usage:</b>\n"
            "<code>/add_premium &lt;user_id&gt; &lt;days&gt;</code>\n\n"
            "<i>Use 0 for permanent premium.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])

        if days < 0:
            return await message.reply_text(
                "❌ Days negative nahi ho sakte."
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
            parse_mode=enums.ParseMode.HTML
        )

    except ValueError:
        await message.reply_text(
            "❌ <b>Error:</b> User ID and Days must be numbers.",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        logger.exception("Failed to add premium")
        await message.reply_text(
            "❌ Premium add nahi ho paaya. Logs check karo."
        )


@Client.on_message(
    filters.command("remove_premium") & filters.user(ADMINS) & filters.private
)
async def remove_premium_admin(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>⚠️ Usage:</b> "
            "<code>/remove_premium &lt;user_id&gt;</code>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        user_id = int(message.command[1])
        await db.remove_premium(user_id)

        await message.reply_text(
            f"✅ Premium removed from <code>{user_id}</code>.",
            parse_mode=enums.ParseMode.HTML
        )

    except ValueError:
        await message.reply_text(
            "❌ User ID number hona chahiye."
        )
    except Exception:
        logger.exception("Failed to remove premium")
        await message.reply_text(
            "❌ Premium remove nahi ho paaya. Logs check karo."
        )


# ======================================================
# EXISTING CALLBACK
# ======================================================

@Client.on_callback_query(filters.regex("^premium_plans_btn$"))
async def premium_plans_callback(
    client: Client,
    callback_query: CallbackQuery
):
    await callback_query.answer()
    await show_premium_plans(callback_query)