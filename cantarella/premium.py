from datetime import date, timedelta

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from config import ADMINS
from database.db import db


@Client.on_message(
    filters.command("add_premium") & filters.user(ADMINS) & filters.private
)
async def add_premium_admin(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text(
            "<b>Usage:</b> <code>/add_premium user_id days</code>\n"
            "Permanent premium ke liye days mein <code>0</code use karo.",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        user_id = int(message.command[1])
        days = int(message.command[2])

        if user_id <= 0 or days < 0:
            raise ValueError

        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, f"User {user_id}")

        expiry_date = (
            None if days == 0
            else (date.today() + timedelta(days=days)).isoformat()
        )
        await db.add_premium(user_id, expiry_date)

        duration = "Permanent" if days == 0 else f"{days} days"
        await message.reply_text(
            f"✅ <b>Premium activated</b>\n"
            f"User: <code>{user_id}</code>\n"
            f"Duration: <code>{duration}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    except ValueError:
        await message.reply_text(
            "❌ Valid user ID aur non-negative days enter karo.",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception:
        await message.reply_text(
            "❌ Premium activate nahi hua. Database aur logs check karo."
        )


@Client.on_message(
    filters.command("remove_premium") & filters.user(ADMINS) & filters.private
)
async def remove_premium_admin(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: <code>/remove_premium user_id</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        user_id = int(message.command[1])
        if user_id <= 0:
            raise ValueError

        if not await db.is_user_exist(user_id):
            return await message.reply_text("❌ User database mein nahi mila.")

        await db.remove_premium(user_id)
        await message.reply_text(
            f"✅ Premium removed from <code>{user_id}</code>.",
            parse_mode=enums.ParseMode.HTML,
        )
    except ValueError:
        await message.reply_text("❌ Valid numeric user ID enter karo.")
    except Exception:
        await message.reply_text("❌ Premium remove nahi hua. Logs check karo.")
