import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from ShizuMusic import bot, call_py
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import clear_queue, peek_current, pop_current, queue_size
from ShizuMusic.utils.db import is_user_blocked_db
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.helpers import delete_file
from ShizuMusic.utils.permissions import is_user_authorized


# ❖ help menu dashboard layout ❖
#
#    row 1 : [ᴍᴀɴᴀɢᴇʀ]  [ᴀ-ᴘʟᴀʏ]   [ʙʀᴏᴀᴅᴄᴀsᴛ]
#    row 2 : [ʙʟ-ᴄʜᴀᴛ]  [ʙʟ-ᴜsᴇʀs] [ᴘɪɴɢ]
#    row 3 : [ᴘʟᴀʏ]    [sᴘᴇᴇᴅ]    [ɪɴғᴏ]
#    row 4 :          [⌯ ʜᴏᴍᴇ ⌯]
#
# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖

_HELP_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴍᴀɴᴀɢᴇʀ",    callback_data="help_admin"),
        InlineKeyboardButton("ᴀ-ᴘʟᴀʏ",    callback_data="help_autoplay"),
        InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ",    callback_data="help_gcast"),
    ],
    [
        InlineKeyboardButton("ʙʟ-ᴄʜᴀᴛ",  callback_data="help_blchat"),
        InlineKeyboardButton("ʙʟ-ᴜsᴇʀs", callback_data="help_blusers"),
        InlineKeyboardButton("ᴘɪɴɢ",     callback_data="help_ping"),
    ],
    [
        InlineKeyboardButton("ᴘʟᴀʏ",     callback_data="help_play"),
        InlineKeyboardButton("sᴘᴇᴇᴅ",    callback_data="help_speed"),
        InlineKeyboardButton("ɪɴғᴏ",     callback_data="help_info"),
    ],
    [
        InlineKeyboardButton("⌯ ʜᴏᴍᴇ ⌯", callback_data="go_back"),
    ],
])

_BACK_KB = InlineKeyboardMarkup([[
    InlineKeyboardButton("⌯ ʙᴀᴄᴋ ⌯", callback_data="show_help"),
]])

# ❖ help text definitions directory ❖

_HELP_TEXTS = {

    # ── admin utilities ────────────────────────────────────────────────────────
    "help_admin": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│⚙️ ᴍᴀɴᴀɢᴇʀ ᴄᴏᴍᴍᴀɴᴅs sᴇᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /pause</b>\n"
        "<b>│   ᴘᴀᴜsᴇ ᴀᴄᴛɪᴠᴇ sᴛʀᴇᴀᴍ ɴᴏᴡ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /resume</b>\n"
        "<b>│   ʀᴇsᴛᴀʀᴛ ᴘᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /skip</b>\n"
        "<b>│   ᴊᴜᴍᴩ ᴛᴏ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stop  ᴏʀ  /end</b>\n"
        "<b>│   ʜᴀʟᴛ ᴍᴜsɪᴄ & ᴇxɪᴛ ᴠᴄ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /clear</b>\n"
        "<b>│   ᴡɪᴩᴇ ᴀʟʟ ǫᴜᴇᴜᴇᴅ sᴏɴɢs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /seek</b> <code>&lt;seconds&gt;</code>\n"
        "<b>│   ᴊᴜᴍᴩ ғᴏʀᴡᴀʀᴅ ʙʏ sᴇᴄᴏɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /seekback</b> <code>&lt;seconds&gt;</code>\n"
        "<b>│   sᴋɪᴩ ʙᴀᴄᴋᴡᴀʀᴅ ʙʏ sᴇᴄᴏɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /reboot</b>\n"
        "<b>│   ʀᴇsᴇᴛ sᴛᴀᴛᴇ & ʟᴇᴀᴠᴇ ᴠᴄ</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── autoplay system ────────────────────────────────────────────────────────
    "help_autoplay": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🔁 ᴀᴜᴛᴏ-ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /autoplay</b> <code>&lt;query&gt;</code>\n"
        "<b>│   ᴋᴇᴇᴩ ᴘʟᴀʏɪɴɢ ᴛʀᴀᴄᴋs</b>\n"
        "<b>│   ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ɪɴᴩᴜᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /end  ᴏʀ  /stop</b>\n"
        "<b>│   sᴛᴏᴩ ᴀᴜᴛᴏᴩʟᴀʏ & ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│💡 sᴀᴍᴩʟᴇs :</b>\n"
        "<b>│</b> <code>/autoplay trending hits</code>\n"
        "<b>│</b> <code>/autoplay lo-fi beats</code>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── broadcast suite ────────────────────────────────────────────────────────
    "help_gcast": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏᴏʟs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /broadcast  ᴏʀ  /gcast</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴍsɢ ᴏʀ ᴡʀɪᴛᴇ ᴛᴇxᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ғʟᴀɢs ʟɪsᴛ :</b>\n"
        "<b>│</b> <code>-pin</code>      <b>→ sᴛɪᴄᴋ sɪʟᴇɴᴛʟʏ ɪɴ ɢʀᴏᴜᴩs</b>\n"
        "<b>│</b> <code>-pinloud</code>   <b>→ sᴛɪᴄᴋ ᴡɪᴛʜ ᴀʟᴇʀᴛ</b>\n"
        "<b>│</b> <code>-nogroup</code>   <b>→ sᴋɪᴩ ɢʀᴏᴜᴩs</b>\n"
        "<b>│</b> <code>-user</code>      <b>→ sᴇɴᴅ ᴛᴏ ᴅᴍ ᴜsᴇʀs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│💡 ᴇxᴀᴍᴩʟᴇs :</b>\n"
        "<b>│</b> <code>/gcast -pin</code>            <i>(reply)</i>\n"
        "<b>│</b> <code>/gcast -user hello!</code>    <i>(text)</i>\n"
        "<b>│</b> <code>/gcast -nogroup -user</code>  <i>(dm only)</i>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── chat restriction ───────────────────────────────────────────────────────
    "help_blchat": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🚫 ʙʟᴏᴄᴋ ᴄʜᴀᴛ ᴛᴏᴏʟs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gblock</b>\n"
        "<b>│   ʙʟᴏᴄᴋ ᴛʜɪs ɢʀᴏᴜᴩ ɪɴsᴛᴀɴᴛʟʏ</b>\n"
        "<b>│   ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ᴡɪʟʟ ʀᴜɴ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gblock</b> <code>-100xxxxxxx</code>\n"
        "<b>│   ʙʟᴏᴄᴋ ᴄʜᴀᴛ ᴠɪᴀ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gunblock</b>\n"
        "<b>│   ʀᴇsᴛᴏʀᴇ ᴛʜɪs ɢʀᴏᴜᴩ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gunblock</b> <code>-100xxxxxxx</code>\n"
        "<b>│   ᴜɴʙʟᴏᴄᴋ ᴠɪᴀ ᴄʜᴀᴛ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /blocklist</b>\n"
        "<b>│   ᴠɪᴇᴡ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ᴄʜᴀᴛs & ᴜsᴇʀs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── user restriction ───────────────────────────────────────────────────────
    "help_blusers": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🚫 ʙʟᴏᴄᴋ ᴜsᴇʀs ᴛᴏᴏʟs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ublock</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴜsᴇʀ ᴛᴏ ʙʟᴏᴄᴋ</b>\n"
        "<b>│   ᴜsᴇʀ ɢᴇᴛs ʙᴀɴɴᴇᴅ ғʀᴏᴍ ʙᴏᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ublock</b> <code>123456789</code>\n"
        "<b>│   ʙᴀɴ ᴜsᴇʀ ᴠɪᴀ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /uunblock</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴜsᴇʀ ᴛᴏ ᴜɴʙᴀɴ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /uunblock</b> <code>123456789</code>\n"
        "<b>│   ᴜɴʙᴀɴ ᴜsᴇʀ ᴠɪᴀ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /blocklist</b>\n"
        "<b>│   ᴄʜᴇᴄᴋ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀ ʟɪsᴛ</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── ping metrics ───────────────────────────────────────────────────────────
    "help_ping": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🏓 ᴘɪɴɢ & sᴛᴀᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ping</b>\n"
        "<b>│   ᴄʜᴇᴄᴋ ʟᴀᴛᴇɴᴄʏ, ʀᴀᴍ, ᴄᴩᴜ</b>\n"
        "<b>│   ᴀɴᴅ ᴜᴩᴛɪᴍᴇ ᴍᴇᴛʀɪᴄs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speedtest  ᴏʀ  /spt</b>\n"
        "<b>│   ʀᴜɴ sᴩᴇᴇᴅ ᴛᴇsᴛ</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stats</b>\n"
        "<b>│   ғᴜʟʟ sʏsᴛᴇᴍ + ᴅʙ ᴅᴀᴛᴀ</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── playback commands ──────────────────────────────────────────────────────
    "help_play": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🎵 ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /play</b> <code>&lt;song or url&gt;</code>\n"
        "<b>│   sᴛʀᴇᴀᴍ ᴀᴜᴅɪᴏ ɪɴ ᴠᴄ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /vplay</b> <code>&lt;song or url&gt;</code>\n"
        "<b>│   sᴛʀᴇᴀᴍ ᴠɪᴅᴇᴏ ɪɴ ᴠᴄ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ʀᴇᴩʟʏ ᴍᴇᴅɪᴀ + /play</b>\n"
        "<b>│   ᴩʟᴀʏ ғɪʟᴇ ᴅɪʀᴇᴄᴛʟʏ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋs sᴜᴩᴩᴏʀᴛᴇᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ʟɪᴍɪᴛ : {config.MAX_DURATION_SECONDS // 60} ᴍɪɴs</b>\n"
        "<b>│❍ ǫᴜᴇᴜᴇ : {config.QUEUE_LIMIT} ᴛʀᴀᴄᴋs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── speed & audio effects ──────────────────────────────────────────────────
    "help_speed": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🎚️ sᴩᴇᴇᴅ & ᴇғғᴇᴄᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speed</b> <code>&lt;0.25 – 4.0&gt;</code>\n"
        "<b>│   ᴄʜᴀɴɢᴇ sᴛʀᴇᴀᴍ sᴩᴇᴇᴅ</b>\n"
        "<b>│   ᴇ.ɢ. : /speed 1.5</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speedreset</b>\n"
        "<b>│   ʀᴇsᴇᴛ sᴩᴇᴇᴅ ᴛᴏ 1.0x</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /bass</b> <code>&lt;1 – 20&gt;</code>\n"
        "<b>│   ʙᴀss ʙᴏᴏsᴛ ɪɴ ᴅʙ</b>\n"
        "<b>│   ᴇ.ɢ. : /bass 10</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /bassoff</b>\n"
        "<b>│   ᴛᴜʀɴ ᴏғғ ʙᴀss ʙᴏᴏsᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effecton</b>\n"
        "<b>│   ᴀᴩᴩʟʏ ᴇғғᴇᴄᴛs ᴛᴏ ᴀʟʟ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effectoff</b>\n"
        "<b>│   ᴛᴜʀɴ ᴏғғ ᴀᴜᴛᴏ ᴇғғᴇᴄᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effects</b>\n"
        "<b>│   ᴄʜᴇᴄᴋ ᴀᴄᴛɪᴠᴇ sᴛᴀᴛᴜs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── info commands ──────────────────────────────────────────────────────────
    "help_info": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│ℹ️ ɪɴғᴏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /id</b>\n"
        "<b>│   ɢᴇᴛ ɪᴅs ғᴏʀ ᴜsᴇʀ/ᴄʜᴀᴛ/ᴍsɢ</b>\n"
        "<b>│   ᴡᴏʀᴋs ᴡɪᴛʜ ʀᴇᴩʟʏ ᴛᴏᴏ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /id</b> <code>@username</code>\n"
        "<b>│   ғᴇᴛᴄʜ ᴀɴʏ ᴜsᴇʀ's ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /repo</b>\n"
        "<b>│   ɢᴇᴛ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʟɪɴᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stats</b>\n"
        "<b>│   sʏsᴛᴇᴍ + ᴅʙ ᴅᴀᴛᴀ (ᴏᴡɴᴇʀ)</b>\n"
        "<b>╰────────────────────▣</b>"
    ),
}


# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖
#   callback query handler router
# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖

@bot.on_callback_query()
async def on_callback(client, cbq: CallbackQuery) -> None:

    chat_id = cbq.message.chat.id
    user    = cbq.from_user
    data    = cbq.data

    # ── user block check filter ───────────────────────────────────────────────
    if user and is_user_blocked_db(user.id):
        await cbq.answer()
        return

    # ── player authorization check ────────────────────────────────────────────
    if data in ("pause", "resume", "skip", "stop", "clear"):
        if not await is_user_authorized(cbq):
            await cbq.answer("❖ ᴍᴀɴᴀɢᴇʀs ᴏɴʟʏ", show_alert=True)
            return

    # ── PAUSE ─────────────────────────────────────────────────────────────────
    if data == "pause":
        try:
            await call_py.pause(chat_id)
            await cbq.answer("Paused")
            await client.send_message(
                chat_id,
                f"<b>❖ sᴛʀᴇᴀᴍ ᴩᴀᴜsᴇᴅ</b>\n<b>❖ ʙʏ :</b> {user.mention}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("Failed To Pause", show_alert=True)

    # ── RESUME ────────────────────────────────────────────────────────────────
    elif data == "resume":
        try:
            await call_py.resume(chat_id)
            await cbq.answer("Resumed")
            await client.send_message(
                chat_id,
                f"<b>❖ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ</b>\n<b>❖ ʙʏ :</b> {user.mention}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("Failed To Resume", show_alert=True)

    # ── SKIP ──────────────────────────────────────────────────────────────────
    elif data == "skip":
        if not queue_size(chat_id):
            await cbq.answer("Queue Is Empty", show_alert=True)
            return

        skipped = pop_current(chat_id)

        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass

        await asyncio.sleep(1.5)

        try:
            delete_file(skipped.get("file_path", ""))
        except Exception:
            pass

        await client.send_message(
            chat_id,
            f"<b>❖ ᴛʀᴀᴄᴋ sᴋɪᴩᴩᴇᴅ</b>\n"
            f"<b>❖ ʙʏ :</b> {user.mention}\n"
            f"<b>❖ sᴏɴɢ :</b> <code>{short(skipped['title'])}</code>",
            parse_mode=ParseMode.HTML,
        )

        nxt = peek_current(chat_id)
        if nxt:
            await cbq.answer("Playing Next")
            dm = await bot.send_message(
                chat_id,
                f"<b>❖ ɴᴇxᴛ ᴛʀᴀᴄᴋ :</b> <code>{nxt['title']}</code>",
                parse_mode=ParseMode.HTML,
            )
            await play_song(chat_id, dm, nxt)
        else:
            await cbq.answer("Queue Empty", show_alert=True)

    # ── STOP ──────────────────────────────────────────────────────────────────
    elif data == "stop":
        await leave_vc(chat_id)
        await cbq.answer("Stopped")
        await client.send_message(
            chat_id,
            f"<b>❖ ᴩʟᴀʏʙᴀᴄᴋ sᴛᴏᴩᴩᴇᴅ</b>\n<b>❖ ʙʏ :</b> {user.mention}",
            parse_mode=ParseMode.HTML,
        )

    # ── CLEAR ─────────────────────────────────────────────────────────────────
    elif data == "clear":
        clear_queue(chat_id)
        await cbq.answer("Queue Cleared")
        await cbq.message.edit_text(
            f"<b>❖ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ</b>\n<b>❖ ʙʏ :</b> {user.mention}",
            parse_mode=ParseMode.HTML,
        )

    # ── NOOP ──────────────────────────────────────────────────────────────────
    elif data == "noop":
        await cbq.answer()

    # ── CLOSE HELP ────────────────────────────────────────────────────────────
    elif data == "close_help":
        await cbq.answer()
        try:
            await cbq.message.delete()
        except Exception:
            pass

    # ── HELP DASHBOARD ────────────────────────────────────────────────────────
    elif data == "show_help":
        await cbq.answer()
        try:
            await cbq.message.edit_text(
                "<b>❖ sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=_HELP_KB,
            )
        except Exception:
            await cbq.message.edit_caption(
                caption="<b>❖ sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=_HELP_KB,
            )

    elif data == "go_back":
        await _go_back(cbq)

    elif data.startswith("help_"):
        await cbq.answer()
        text = _HELP_TEXTS.get(data)
        if text:
            try:
                await cbq.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=_BACK_KB,
                )
            except Exception:
                pass


# ── return to home start view routine ─────────────────────────────────────────

async def _go_back(cbq: CallbackQuery) -> None:
    await cbq.answer()
    uid  = cbq.from_user.id
    name = cbq.from_user.first_name or "User"

    caption = (
        "<b>╭────────────────────▣</b>\n"
        f"<b>│❖ ʜᴇʟʟᴏ</b> <a href='tg://user?id={uid}'>{name}</a>, 🥀\n"
        f"<b>│❖ ᴛʜɪs ɪs {config.BOT_NAME} !</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❖ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ʙᴏᴛ.</b>\n"
        "<b>├────────────────────▣</b>\n"
        f"<b>│❖ ᴩᴏᴡᴇʀᴇᴅ ʙʏ » "
        f"<a href='https://t.me/PBXCHATS'>sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>\n"
        "<b>╰────────────────────▣</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛩️ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ⛩️",
                            url=f"{config.BOT_LINK}?startgroup=true")],
        [
            InlineKeyboardButton("🍬 sᴜᴩᴩᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("🍹 ᴜᴩᴅᴀᴛᴇs 🍹",  url=config.UPDATES_CHANNEL),
        ],
        [InlineKeyboardButton("🏩 ʜᴇʟᴩ & ᴄᴏᴍᴍᴀɴᴅs 🏩",
                            callback_data="show_help")],
        [
            InlineKeyboardButton("🫧 ᴏᴡɴᴇʀ 🫧",
                                url=f"tg://user?id={config.OWNER_ID}"),
            InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ 🍡",
                                url="https://github.com/Badmunda05/ShizuMusic/fork"),
        ],
    ])

    try:
        await cbq.message.edit_caption(
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
    except Exception:
        try:
            await cbq.message.edit_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        except Exception:
            pass
