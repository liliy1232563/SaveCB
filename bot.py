
import asyncio
import datetime
from datetime import timezone, timedelta

from pyrogram import Client, filters, __version__ as pyrogram_version
from pyrogram.types import Message, BotCommand
from pyrogram.errors import FloodWait

from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, ADMINS
from database.db import db
from logger import LOGGER

# Keep-alive server (Render / Heroku)
try:
    from keep_alive import keep_alive
except ImportError:
    keep_alive = None

logger = LOGGER(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

# Cache to reduce repeated database checks
USER_CACHE = set()

LOGO = r"""
  ██████╗  ██╗  ██╗  █████╗  ███╗   ██╗ ██████╗
  ██╔══██╗ ██║  ██║ ██╔══██╗ ████╗  ██║ ██╔══██╗
  ██║  ██║ ███████║ ███████║ ██╔██╗ ██║ ██████╔╝
  ██║  ██║ ██╔══██║ ██╔══██╗ ██║╚██╗██║ ██╔═══╝
  ██████╔╝ ██║  ██║ ██║  ██║ ██║ ╚████║ ██║
       BOT WORKING PROPERLY....
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="cantarella_Login_Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="cantarella"),
            workers=10,
            sleep_threshold=15,
            max_concurrent_transmissions=5,
            ipv6=False,
            in_memory=False,
        )
        self._keep_alive_started = False

    async def start(self):
        print(LOGO)

        # Prevent duplicate client startup
        if self.is_connected:
            logger.warning("Client is already connected; skipping start.")
            return

        # Start keep-alive once
        if keep_alive and not self._keep_alive_started:
            try:
                loop = asyncio.get_running_loop()
                try:
                    keep_alive(loop)
                except TypeError:
                    keep_alive()

                self._keep_alive_started = True
                logger.info("Keep-alive server started.")

            except Exception as e:
                logger.warning(f"Keep-alive failed: {e}")

        # Retry FloodWait only. Other errors must stop startup.
        while True:
            try:
                await super().start()
                break
            except FloodWait as e:
                wait_time = int(e.value) + 10
                logger.warning(
                    f"FloodWait: retrying in {wait_time} seconds."
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Critical Startup Error: {e}")
                raise

        me = await self.get_me()

        # Database statistics
        try:
            user_count = await db.total_users_count()
            logger.info(
                f"MongoDB connected: {user_count} users found."
            )
        except Exception as e:
            logger.error(f"DB stats failed: {e}")
            user_count = "Unknown"

        # Startup notification
        now = datetime.datetime.now(IST)
        startup_text = (
            "<b><i>🤖 Bot Successfully Started ♻️</i></b>\n\n"
            f"<b>Bot:</b> @{me.username}\n"
            f"<b>Users:</b> <code>{user_count} / 200</code>\n"
            f"<b>Time:</b> <code>{now.strftime('%I:%M %p')} IST</code>\n\n"
            "<b>Developed by @cantarellabots</b>"
        )

        try:
            await self.send_message(LOG_CHANNEL, startup_text)
            logger.info("Startup log sent.")
        except Exception as e:
            logger.error(f"Failed to send startup log: {e}")

        try:
            await self.set_bot_commands_list()
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")

    async def stop(self, *args):
        try:
            if self.is_connected:
                await self.send_message(
                    LOG_CHANNEL,
                    "<b><i>❌ Bot is going Offline</i></b>"
                )
        except Exception as e:
            logger.warning(f"Offline notification failed: {e}")

        try:
            if self.is_connected:
                await asyncio.shield(super().stop())
        except Exception as e:
            logger.error(f"Bot stop failed: {e}")

        logger.info("Bot stopped cleanly.")

    async def set_bot_commands_list(self):
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
            BotCommand("login", "Login"),
            BotCommand("logout", "Logout"),
            BotCommand("cancel", "Cancel current action"),
            BotCommand("myplan", "Check your plan"),
            BotCommand("premium", "Premium info"),
            BotCommand("setchat", "Set target chat"),
            BotCommand("set_thumb", "Set thumbnail"),
            BotCommand("view_thumb", "View thumbnail"),
            BotCommand("del_thumb", "Delete thumbnail"),
            BotCommand("set_caption", "Set caption"),
            BotCommand("see_caption", "View caption"),
            BotCommand("del_caption", "Delete caption"),
            BotCommand("set_del_word", "Add delete word"),
            BotCommand("rem_del_word", "Remove delete word"),
            BotCommand("set_repl_word", "Add replace word"),
            BotCommand("rem_repl_word", "Remove replace word"),
        ]

        await self.set_bot_commands(commands)
        logger.info("Bot commands updated.")


BotInstance = Bot()


@BotInstance.on_message(
    filters.private & filters.incoming,
    group=-1
)
async def new_user_log(bot: Client, message: Message):
    user = message.from_user

    if not user or user.id in USER_CACHE:
        return

    try:
        if not await db.is_user_exist(user.id):
            await db.add_user(user.id, user.first_name)

            now = datetime.datetime.now(IST)
            log_text = (
                "<b>#NewUser 👤</b>\n"
                f"<b>User:</b> {user.mention}\n"
                f"<b>ID:</b> <code>{user.id}</code>\n"
                f"<b>Time:</b> {now.strftime('%I:%M %p')} IST"
            )

            try:
                await bot.send_message(LOG_CHANNEL, log_text)
            except Exception as e:
                logger.warning(f"New user log failed: {e}")

        USER_CACHE.add(user.id)

    except Exception as e:
        logger.error(f"New user database logging failed: {e}")


@BotInstance.on_message(
    filters.command("cmd") & filters.user(ADMINS)
)
async def update_commands(bot: Client, message: Message):
    try:
        await bot.set_bot_commands_list()
        await message.reply_text("✅ Commands menu updated!")
    except Exception as e:
        logger.error(f"Command update failed: {e}")
        await message.reply_text(f"❌ Error: {e}")


if __name__ == "__main__":
    BotInstance.run()
