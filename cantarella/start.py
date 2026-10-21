# Developed by: LastPerson07 × cantarella
# Telegram: @cantarellabots | @THEUPDATEDGUYS
import os
import asyncio
import random
import time
import shutil
import pyrogram
import requests
import hashlib 
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant,
    InviteHashExpired, UsernameNotOccupied, AuthKeyUnregistered, UserDeactivated, UserDeactivatedBan
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InputMediaPhoto
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
import math
from logger import LOGGER
logger = LOGGER(__name__)
SUBSCRIPTION = os.environ.get('SUBSCRIPTION', 'https://graph.org/file/1b59bc506d51764dbb953-863454c01a8f29f225.jpg')
FREE_LIMIT_SIZE = 2 * 1024 * 1024 * 1024
FREE_LIMIT_DAILY = 10
UPI_ID = os.environ.get("UPI_ID", "muftashir@fam")
QR_CODE = os.environ.get("QR_CODE", "https://graph.org/file/e935e5ee94c5d0aba496f-71e8d49a9d842cc9bf.jpg")
REACTIONS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
    "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
    "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
    "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
    "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️",
    "😡"
]


dev_text = "👨‍💻 Mind Behind This Bot:\n• @EmptyJohan\n• @GabimaruYami"
expected_dev_hash = "0241e1feed7ea131b3c4f236f5448a849465a92a81a9b564b5ea1278fd1c8158"
channels_text = "📢 Official Channels:\n• @Solurix_bots\n\nStay updated for new features!"
expected_channels_hash = "1ba12e97540509e8b240e6ecfc69871655a6c89bb4a3bdfdd0ce831026c95c7e"

if (
    hashlib.sha256(dev_text.encode('utf-8')).hexdigest() != expected_dev_hash or
    hashlib.sha256(channels_text.encode('utf-8')).hexdigest() != expected_channels_hash
):
    raise Exception("Tampered developer info detected! Bot will not start. Fuck the code - crashing now.")

class script(object):
   
    START_TXT = """<b>👋 Hello {},</b>
<b>🤖 I am <a href=https://t.me/{}>{}</a></b>
<i>Your Professional Restricted Content Saver Bot.</i>
<blockquote><b>🚀 System Status: 🟢 Online</b>
<b>⚡ Performance: 10x High-Speed Processing</b>
<b>🔐 Security: End-to-End Encrypted</b>
<b>📊 Uptime: 99.9% Guaranteed</b></blockquote>
<b>👇 Select an Option Below to Get Started:</b>
"""
    HELP_TXT = """<b>📚 Comprehensive Help & User Guide</b>
<blockquote><b>1️⃣ Public Channels (No Login Required)</b></blockquote>
• Forward or send the post link directly.
• Compatible with any public channel or group.
• <i>Example Link:</i> <code>https://t.me/channel/123</code>
<blockquote><b>2️⃣ Private/Restricted Channels (Login Required)</b></blockquote>
• Use <code>/login</code> to securely connect your Telegram account.
• Send the private link (e.g., <code>t.me/c/123...</code>).
• Bot accesses content using your authenticated session.
<blockquote><b>3️⃣ Batch Downloading Mode</b></blockquote>
• Initiate with <code>/batch</code> for multiple files.
• Follow interactive prompts for seamless processing.
<blockquote><b>🛑 Free User Limitations:</b></blockquote>
• <b>Daily Quota:</b> 10 Files / 24 Hours
• <b>File Size Cap:</b> 2GB Maximum
<blockquote><b>💎 Premium Membership Benefits:</b></blockquote>
• Unlimited Downloads & No Restrictions.
• Priority Support & Advanced Features.
"""
    ABOUT_TXT = """<b>ℹ️ About This Bot</b>
<blockquote><b>╭────[ 🧩 Technical Stack ]────⍟</b>
<b>├⍟ 🤖 Bot Name : <a href=http://t.me/PRO_Save_Restricted_Bot>Save Content</a></b>
<b>├⍟ 👨‍💻 Developer : <a href=https://t.me/Tg_jiro/24>Jɪʀᴏ</a></b>
<b>├⍟ 📚 Library : <a href='https://docs.pyrogram.org/'>Pyrogram Async</a></b>
<b>├⍟ 🐍 Language : <a href='https://www.python.org/'>Python 3.11+</a></b>
<b>├⍟ 🗄 Database : <a href='https://www.mongodb.com/'>MongoDB Atlas Cluster</a></b>
<b>├⍟ 📡 Hosting : Dedicated High-Speed VPS</b>
<b>╰───────────────⍟</b></blockquote>
"""
    PREMIUM_TEXT = """<b>💎 Pʀᴇᴍɪᴜᴍ Mᴇᴍʙᴇʀsʜɪᴘ Pʟᴀɴs</b>
<b>Uɴʟᴏᴄᴋ Uɴʟɪᴍɪᴛᴇᴅ Aᴄᴄᴇss & Aᴅᴠᴀɴᴄᴇᴅ Fᴇᴀᴛᴜʀᴇs!</b>
<blockquote><b>✨ Key Benefits:</b>
<b>♾️ Uɴʟɪᴍɪᴛᴇᴅ Dᴀɪʟʏ Dᴏᴡɴʟᴏᴀᴅs</b>
<b>📂 Sᴜᴘᴘᴏʀᴛ ꜰᴏʀ 𝟺GB+ Fɪʟᴇ Sɪᴢᴇs</b>
<b>⚡ Iɴsᴛᴀɴᴛ Pʀᴏᴄᴇssɪɴɢ (Zero Delay)</b>
<b>🖼 Cᴜsᴛᴏᴍɪᴢᴀʙʟᴇ Tʜᴜᴍʙɴᴀɪʟs</b>
<b>📝 Pᴇʀsᴏɴᴀʟɪᴢᴇᴅ Cᴀᴘᴛɪᴏɴs</b>
<b>🛂 𝟸𝟺/𝟽 Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ</b></blockquote>
<blockquote><b>💳 Pʀɪᴄɪɴɢ Oᴘᴛɪᴏɴs:</b></blockquote>
• <b>1 Mᴏɴᴛʜ Pʟᴀɴ:</b> ₹59 / $1 (Bɪʟʟᴇᴅ Mᴏɴᴛʜʟʏ)
• <b>3 Mᴏɴᴛʜ Pʟᴀɴ:</b> ₹130 / $3 (Sᴀᴠᴇ 20%)
• <b>Lɪꜰᴇᴛɪᴍᴇ Aᴄᴄᴇss::</b> ₹555 / $5 (Oɴᴇ-Tɪᴍᴇ Pᴀʏᴍᴇɴᴛ)
<blockquote><b>👇 Sᴇᴄᴜʀᴇ Pᴀʏᴍᴇɴᴛ:</b></blockquote>
<b>💸 UPI ID:</b> <code>{}</code>
<b>📸 QR Code:</b> <a href='{}'>Sᴄᴀɴ ᴛᴏ Pᴀʏ</a>
<i>Aꜰᴛᴇʀ Pᴀʏᴍᴇɴᴛ: Sᴇɴᴅ Sᴄʀᴇᴇɴsʜᴏᴛ ᴛᴏ Aᴅᴍɪɴ ꜰᴏʀ Iɴsᴛᴀɴᴛ Aᴄᴛɪᴠᴀᴛɪᴏɴ.</i>
"""
    PROGRESS_BAR = """\
<b>⚡ Processing Task...</b>
<blockquote>
<b>Progress: {bar} {percentage:.1f}%</b>
<b>🚀 Speed:</b> <code>{speed}/s</code>
<b>💾 Size:</b> <code>{current} of {total}</code>
<b>⏱ Elapsed:</b> <code>{elapsed}</code>
<b>⏳ ETA:</b> <code>{eta}</code>
</blockquote>
"""
    CAPTION = """<b><a href="https://t.me/Solurix_bots"></a></b>\n\n<b>⚜️ Powered By : <a href="https://t.me/Solurix_bots">THE UPDATED GUYS 😎</a></b>"""
    LIMIT_REACHED = """<b>🚫 Daily Limit Exceeded</b>
<b>Your 10 free saves for today have been used.</b>
<i>Quota resets automatically after 24 hours from first download.</i>
<blockquote><b>🔓 Upgrade to Premium for Unlimited Access!</b></blockquote>
Remove all restrictions and enjoy seamless downloading.
"""
    SIZE_LIMIT = """<b>⚠️ File Size Exceeded</b>
<b>Free tier limited to 2GB per file.</b>
<blockquote><b>🔓 Upgrade to Premium</b></blockquote>
Download files up to 4GB and beyond with no limits!
"""
def humanbytes(size):
    try:
        size = max(0, float(size or 0))
    except (TypeError, ValueError):
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB")
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{int(size)} B" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] if tmp else "0s"
class batch_temp(object):
    IS_BATCH = {}
def get_message_type(msg):
    if getattr(msg, 'document', None): return "Document"
    if getattr(msg, 'video', None): return "Video"
    if getattr(msg, 'photo', None): return "Photo"
    if getattr(msg, 'audio', None): return "Audio"
    if getattr(msg, 'text', None): return "Text"
    return None
async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as downread:
                txt = downread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except:
            await asyncio.sleep(5)
async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as upread:
                txt = upread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except:
            await asyncio.sleep(5)
def progress(current, total, message, type):
    if batch_temp.IS_BATCH.get(message.from_user.id):
        raise Exception("Cancelled")
    if not hasattr(progress, "cache"):
        progress.cache = {}
   
    now = time.time()
    task_id = f"{message.id}{type}"
    last_time = progress.cache.get(task_id, 0)
   
    if not hasattr(progress, "start_time"):
        progress.start_time = {}
    if task_id not in progress.start_time:
        progress.start_time[task_id] = now
       
    if (now - last_time) > 5 or current == total:
        try:
            percentage = current * 100 / total
            speed = current / (now - progress.start_time[task_id]) if (now - progress.start_time[task_id]) > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            elapsed = now - progress.start_time[task_id]
           
            filled_length = int(percentage / 5)
            bar = '█' * filled_length + ' ' * (20 - filled_length)
           
            status = script.PROGRESS_BAR.format(
                bar=bar,
                percentage=percentage,
                current=humanbytes(current),
                total=humanbytes(total),
                speed=humanbytes(speed),
                elapsed=TimeFormatter(elapsed * 1000),
                eta=TimeFormatter(eta * 1000)
            )
           
            with open(f'{message.id}{type}status.txt', "w", encoding='utf-8') as fileup:
                fileup.write(status)
               
            progress.cache[task_id] = now
           
            if current == total:
                progress.start_time.pop(task_id, None)
                progress.cache.pop(task_id, None)
        except:
            pass

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    photos = [
        "https://graph.org/file/df8726fb8d213845f1c3b-3a9fa28c3c2e0057d1.jpg",
        "https://graph.org/file/f3875fabc99223d7e09f2-d771797c300ff6fd46.jpg",
        "https://graph.org/file/aaaa17394fbb1f5abcc57-a66026bd65c8c63453.jpg",
        "https://graph.org/file/56936ca35108ec198b186-e2ec779372d574ecf7.jpg"
    ]
    photo_url = random.choice(photos)

    buttons = [
        [
            InlineKeyboardButton("💎 Bᴜʏ Pʀᴇᴍɪᴜᴍ", callback_data="buy_premium"),
            InlineKeyboardButton("🆘 Hᴇʟᴘ & Gᴜɪᴅᴇ", callback_data="help_btn")
        ],
        [
            InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs Pᴀɴᴇʟ", callback_data="settings_btn"),
            InlineKeyboardButton("ℹ️ Aʙᴏᴜᴛ Bᴏᴛ", callback_data="about_btn")
        ],
        [
            InlineKeyboardButton("📢 Cʜᴀɴɴᴇʟs", callback_data="channels_info"),
            InlineKeyboardButton("👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀs", callback_data="dev_info")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    bot = await client.get_me()

    await client.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=script.START_TXT.format(
            message.from_user.mention,
            bot.username,
            bot.first_name
        ),
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    buttons = [[InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]]
    await client.send_message(
        chat_id=message.chat.id,
        text=script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
@Client.on_message(filters.command(["plan", "myplan", "premium"]))
async def send_plan(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("📸 Sᴇɴᴅ Pᴀʏᴍᴇɴᴛ Pʀᴏᴏꜰ", url="https://t.me/EmptyJohan")],
        [InlineKeyboardButton("❌ Cʟᴏsᴇ Mᴇɴᴜ", callback_data="close_btn")]
    ]
    await client.send_photo(
        chat_id=message.chat.id,
        photo=SUBSCRIPTION,
        caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply_text("❌ Batch Process Cancelled Successfully.")
async def settings_panel(client, callback_query):
    """
    Renders the Settings Menu with professional layout.
    """
    user_id = callback_query.from_user.id
    is_premium = await db.check_premium(user_id)
    badge = "💎 Premium Member" if is_premium else "👤 Standard User"
   
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Command List", callback_data="cmd_list_btn")],
        [InlineKeyboardButton("📊 Usage Stats", callback_data="user_stats_btn")],
        [InlineKeyboardButton("🗑 Dump Chat Settings", callback_data="dump_chat_btn")],
        [InlineKeyboardButton("🖼 Manage Thumbnail", callback_data="thumb_btn")],
        [InlineKeyboardButton("📝 Edit Caption", callback_data="caption_btn")],
        [InlineKeyboardButton("⬅️ Return to Home", callback_data="start_btn")]
    ])
   
    text = f"<b>⚙️ Settings Dashboard</b>\n\n<b>Account Status:</b> {badge}\n<b>User ID:</b> <code>{user_id}</code>\n\n<i>Customize and manage your bot preferences below for an optimized experience:</i>"
   
    await callback_query.edit_message_caption(
        caption=text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )
@Client.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def save(client: Client, message: Message):
    user = message.from_user
    text = message.text or ""
    if not user or "t.me/" not in text:
        return

    user_id = user.id
    if await db.check_limit(user_id):
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]])
        return await message.reply_photo(
            photo=SUBSCRIPTION,
            caption=script.LIMIT_REACHED,
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML,
        )

    if batch_temp.IS_BATCH.get(user_id) is False:
        return await message.reply_text(
            "<b>⚠️ A Task is Currently Processing.</b>\n"
            "<i>Please wait for completion or use /cancel to stop.</i>",
            parse_mode=enums.ParseMode.HTML,
        )

    from urllib.parse import urlparse
    try:
        parsed = urlparse(text.strip())
        if parsed.scheme not in ("http", "https") or parsed.netloc.lower() not in ("t.me", "www.t.me"):
            raise ValueError
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError

        is_private_link = parts[0] == "c"
        is_batch = parts[0] == "b"

        if is_private_link:
            if len(parts) != 3 or not parts[1].isdigit():
                raise ValueError
            chat_target = int("-100" + parts[1])
            message_part = parts[2]
        elif is_batch:
            if len(parts) != 3:
                raise ValueError
            chat_target = parts[1]
            message_part = parts[2]
        else:
            if len(parts) != 2:
                raise ValueError
            chat_target = parts[0]
            message_part = parts[1]

        bounds = message_part.split("-", 1)
        from_id = int(bounds[0])
        to_id = int(bounds[1]) if len(bounds) == 2 else from_id
        if from_id <= 0 or to_id < from_id or to_id - from_id > 1000:
            raise ValueError
    except (ValueError, IndexError):
        return await message.reply_text(
            "❌ Invalid Telegram link. Link check karke dobara bhejo."
        )

    batch_temp.IS_BATCH[user_id] = False
    try:
        for msgid in range(from_id, to_id + 1):
            if batch_temp.IS_BATCH.get(user_id):
                break

            if not is_private_link and not is_batch:
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=chat_target,
                        message_id=msgid,
                        reply_to_message_id=message.id,
                    )
                    await db.add_traffic(user_id)
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    logger.info(f"Public copy failed; trying saved session: {e}")

            user_data = await db.get_session(user_id)
            if not user_data:
                await message.reply_text(
                    "<b>🔒 Authentication Required</b>\n\n"
                    "<i>Is content ke liye /login se account authorize karo.</i>",
                    parse_mode=enums.ParseMode.HTML,
                )
                return

            acc = Client(
                "saverestricted",
                session_string=user_data,
                api_hash=API_HASH,
                api_id=API_ID,
                in_memory=True,
                max_concurrent_transmissions=10,
            )
            try:
                await acc.connect()
                await handle_restricted_content(
                    client, acc, message, chat_target, msgid
                )
            except Exception as e:
                logger.exception(f"Restricted download failed for user {user_id}: {e}")
                await message.reply_text(
                    "❌ Download failed. Session expire ho sakta hai; "
                    "/logout karke /login dobara try karo."
                )
                return
            finally:
                try:
                    if getattr(acc, "is_connected", False):
                        await acc.disconnect()
                except Exception as e:
                    logger.warning(f"Temporary client disconnect failed: {e}")

            await asyncio.sleep(1)
    finally:
        batch_temp.IS_BATCH[user_id] = True

async def handle_restricted_content(client: Client, acc, message: Message, chat_target, msgid):
    user = message.from_user
    if not user:
        return

    try:
        msg = await acc.get_messages(chat_target, msgid)
    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        return

    if not msg or getattr(msg, "empty", False):
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    file_size = 0
    media = getattr(msg, msg_type.lower(), None)
    if media:
        file_size = getattr(media, "file_size", 0) or 0

    if file_size > FREE_LIMIT_SIZE and not await db.check_premium(user.id):
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]
        ])
        await client.send_message(
            message.chat.id,
            script.SIZE_LIMIT,
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML,
        )
        return

    if msg_type == "Text":
        try:
            await client.send_message(
                message.chat.id,
                msg.text,
                entities=msg.entities,
                reply_to_message_id=message.id,
            )
        except Exception as e:
            logger.warning(f"Text copy failed: {e}")
        return

    await db.add_traffic(user.id)
    smsg = await client.send_message(
        message.chat.id,
        "<b>⬇️ Starting Download...</b>",
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML,
    )

    temp_dir = os.path.join("downloads", str(message.id))
    down_file = f"{message.id}downstatus.txt"
    up_file = f"{message.id}upstatus.txt"
    down_task = None
    up_task = None
    file = None

    try:
        os.makedirs(temp_dir, exist_ok=True)
        down_task = asyncio.create_task(
            downstatus(client, down_file, smsg, message.chat.id)
        )

        file = await acc.download_media(
            msg,
            file_name=f"{temp_dir}/",
            progress=progress,
            progress_args=[message, "down"],
        )
        if not file or not os.path.isfile(file):
            raise RuntimeError("Downloaded file not found.")

        if down_task:
            down_task.cancel()
            down_task = None
        if os.path.exists(down_file):
            os.remove(down_file)

        await smsg.edit("<b>⬆️ Uploading...</b>", parse_mode=enums.ParseMode.HTML)
        up_task = asyncio.create_task(
            upstatus(client, up_file, smsg, message.chat.id)
        )

        ph_path = None
        thumb_id = await db.get_thumbnail(user.id)
        if thumb_id:
            try:
                ph_path = await client.download_media(
                    thumb_id,
                    file_name=f"{temp_dir}/custom_thumb.jpg",
                )
            except Exception as e:
                logger.warning(f"Custom thumbnail download failed: {e}")

        if not ph_path:
            try:
                thumbs = getattr(media, "thumbs", None) or []
                if thumbs:
                    ph_path = await acc.download_media(
                        thumbs[0].file_id,
                        file_name=f"{temp_dir}/thumb.jpg",
                    )
            except Exception as e:
                logger.info(f"Original thumbnail unavailable: {e}")

        custom_caption = await db.get_caption(user.id)
        filename = os.path.basename(file)
        try:
            if custom_caption:
                final_caption = custom_caption.format(
                    filename=filename,
                    file_name=filename,
                    size=humanbytes(file_size),
                )
            else:
                final_caption = script.CAPTION.format(file_name=filename)
                if msg.caption:
                    final_caption += f"\n\n{msg.caption}"
        except (KeyError, IndexError, ValueError) as e:
            logger.warning(f"Caption formatting failed: {e}")
            final_caption = filename

        common = {
            "chat_id": message.chat.id,
            "caption": final_caption,
            "reply_to_message_id": message.id,
        }
        if msg_type == "Document":
            await client.send_document(
                document=file, thumb=ph_path, progress=progress,
                progress_args=[message, "up"], **common
            )
        elif msg_type == "Video":
            await client.send_video(
                video=file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=ph_path,
                progress=progress,
                progress_args=[message, "up"],
                **common,
            )
        elif msg_type == "Audio":
            await client.send_audio(
                audio=file, thumb=ph_path, progress=progress,
                progress_args=[message, "up"], **common
            )
        elif msg_type == "Photo":
            await client.send_photo(photo=file, **common)

    except Exception as e:
        logger.exception(f"Download/upload failed for user {user.id}: {e}")
        try:
            await smsg.edit_text(
                "❌ Download/upload failed. Please try again."
            )
        except Exception:
            pass
    finally:
        for task in (down_task, up_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

        for status_file in (down_file, up_file):
            try:
                if os.path.exists(status_file):
                    os.remove(status_file)
            except OSError as e:
                logger.warning(f"Status file cleanup failed: {e}")

        try:
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except OSError as e:
            logger.warning(f"Temporary directory cleanup failed: {e}")

        try:
            await smsg.delete()
        except Exception:
            pass

@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    if not message: return
   # --- DEVELOPER INFO ---
    if data == "dev_info":
        await callback_query.answer(
            text=dev_text,
            show_alert=True
        )
    elif data == "channels_info":
        await callback_query.answer(
            text=channels_text,
            show_alert=True
        )
    elif data == "settings_btn":
        await settings_panel(client, callback_query)
    elif data == "buy_premium":
        buttons = [
            [InlineKeyboardButton("📸 Sᴇɴᴅ Pᴀʏᴍᴇɴᴛ Pʀᴏᴏꜰ", url="https://t.me/Tg_jiro/24")],
            [InlineKeyboardButton("⬅️ Bᴀᴄᴋ ᴛᴏ Hᴏᴍᴇ", callback_data="start_btn")]
        ]
        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=SUBSCRIPTION,
                caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE),
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "help_btn":
        buttons = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ ᴛᴏ Hᴏᴍᴇ", callback_data="start_btn")]]
        await client.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.id,
            caption=script.HELP_TXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
  
    elif data == "about_btn":
        buttons = [[InlineKeyboardButton("⬅️ Bᴀᴄᴋ ᴛᴏ Hᴏᴍᴇ", callback_data="start_btn")]]
        await client.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.id,
            caption=script.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "start_btn":
        bot = await client.get_me()

        photos = [
            "https://graph.org/file/df8726fb8d213845f1c3b-3a9fa28c3c2e0057d1.jpg",
            "https://graph.org/file/f3875fabc99223d7e09f2-d771797c300ff6fd46.jpg",
            "https://graph.org/file/aaaa17394fbb1f5abcc57-a66026bd65c8c63453.jpg",
            "https://graph.org/file/56936ca35108ec198b186-e2ec779372d574ecf7.jpg"
        ]
        photo_url = random.choice(photos)

        buttons = [
            [
                InlineKeyboardButton("💎 Bᴜʏ Pʀᴇᴍɪᴜᴍ", callback_data="buy_premium"),
                InlineKeyboardButton("🆘 Hᴇʟᴘ & Gᴜɪᴅᴇ", callback_data="help_btn")
            ],
            [
                InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs Pᴀɴᴇʟ", callback_data="settings_btn"),
                InlineKeyboardButton("ℹ️ Aʙᴏᴜᴛ Bᴏᴛ", callback_data="about_btn")
            ],
            [
                InlineKeyboardButton("📢 Cʜᴀɴɴᴇʟs", callback_data="channels_info"),
                InlineKeyboardButton("👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀs", callback_data="dev_info")
            ]
        ]

        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=photo_url,
                caption=script.START_TXT.format(
                    callback_query.from_user.mention,
                    bot.username,
                    bot.first_name
                ),
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "close_btn":
        await message.delete()
    elif data in ["cmd_list_btn", "user_stats_btn", "dump_chat_btn", "thumb_btn", "caption_btn"]:
        pass
    await callback_query.answer()