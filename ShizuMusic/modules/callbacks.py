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
#    row 1 : [ᴍᴀɴᴀɢᴇʀ]  [ᴀ-ᴘʟᴀʏ]    [ʙʀᴏᴀᴅᴄᴀsᴛ]
#    row 2 : [ʙʟ-ᴄʜᴀᴛ]  [ʙʟ-ᴜsᴇʀs] [ᴘɪɴɢ]
#    row 3 : [ᴘʟᴀʏ]    [sᴘᴇᴇᴅ]    [ɪɴғᴏ]
#    row 4 :          [⌯ ʜᴏᴍᴇ ⌯]
#
# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖

_HELP_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴘʟᴀʏ",    callback_data="help_play"),
        InlineKeyboardButton("ᴀ-ᴘʟᴀʏ",  callback_data="help_autoplay"),
        InlineKeyboardButton("sᴘᴇᴇᴅ",    callback_data="help_speed"),
    ],
    [
        InlineKeyboardButton("ᴀᴅᴍɪɴ",    callback_data="help_admin"),
        InlineKeyboardButton("ɢ-ᴄᴀsᴛ",  callback_data="help_gcast"),
        InlineKeyboardButton("ᴘɪɴɢ",    callback_data="help_ping"),
    ],
    [
        InlineKeyboardButton("ʙʟ-ᴄʜᴀᴛ",  callback_data="help_blchat"),
        InlineKeyboardButton("ʙʟ-ᴜsᴇʀs", callback_data="help_blusers"),
        InlineKeyboardButton("ɪɴғᴏ",     callback_data="help_info"),
    ],
    [
        InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_help"),
    ],
])
_BACK_KB = InlineKeyboardMarkup([[
    InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="show_help"),
]])

# ❖ help text definitions directory ❖

_HELP_TEXTS = {

    # ── admin utilities ────────────────────────────────────────────────────────
   "help_admin": (
    "<b>⚙️ ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟs</b>\n\n"
    "<b>/pause</b> — ᴘᴀᴜsᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏʙᴀᴄᴋ\n"
    "<b>/resume</b> — ʀᴇsᴜᴍᴇ ᴘᴀᴜsᴇᴅ ᴘʟᴀʏʙᴀᴄᴋ\n"
    "<b>/skip</b> — ᴘʟᴀʏ ɴᴇxᴛ ᴛʀᴀᴄᴋ\n"
    "<b>/stop</b> <i>ᴏʀ</i> <b>/end</b> — sᴛᴏᴘ ᴘʟᴀʏʙᴀᴄᴋ & ʟᴇᴀᴠᴇ ᴠᴄ\n"
    "<b>/clear</b> — ʀᴇᴍᴏᴠᴇ ᴜɴᴘʟᴀʏᴇᴅ ᴛʀᴀᴄᴋs\n"
    "<b>/seek</b> <code>&lt;seconds&gt;</code> — sᴇᴇᴋ ғᴏʀᴡᴀʀᴅ\n"
    "<b>/seekback</b> <code>&lt;seconds&gt;</code> — sᴇᴇᴋ ʙᴀᴄᴋᴡᴀʀᴅ\n"
    "<b>/reboot</b> — ʀᴇsᴇᴛ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ sᴛᴀᴛᴇ"
),

"help_autoplay": (
    "<b>🔁 ᴀᴜᴛᴏᴘʟᴀʏ</b>\n\n"
    "<b>/autoplay</b> <code>&lt;query&gt;</code>\n"
    "ᴋᴇᴇᴘs ᴛʜᴇ ᴍᴜsɪc ǫᴜᴇᴜᴇ ᴍᴏᴠɪɴɢ ᴡɪᴛʜ ɴᴇᴡ ᴛʀᴀᴄᴋs.\n\n"
    "<b>ᴇxᴀᴍᴘʟᴇs</b>\n"
    "<code>/autoplay trending hits</code>\n"
    "<code>/autoplay lo-fi beats</code>\n\n"
    "<b>/stop</b> <i>ᴏʀ</i> <b>/end</b> — ᴇɴᴅ ᴀᴜᴛᴏᴘʟᴀʏ"
),

"help_gcast": (
    "<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ</b>\n"
    "<i>ᴏᴡɴᴇʀ ᴏɴʟʏ</i>\n\n"
    "<b>/broadcast</b> <i>ᴏʀ</i> <b>/gcast</b>\n"
    "ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ sᴇɴᴅ ᴛᴇxᴛ ᴅɪʀᴇᴄᴛʟʏ.\n\n"
    "<b>ᴏᴘᴛɪᴏɴs</b>\n"
    "<code>-pin</code> — ᴘɪɴ ɪɴ ɢʀᴏᴜᴘs\n"
    "<code>-pinloud</code> — ᴘɪɴ ᴡɪᴛʜ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n"
    "<code>-nogroup</code> — sᴋɪᴘ ɢʀᴏᴜᴘs\n"
    "<code>-user</code> — sᴇɴᴅ ᴛᴏ ᴜsᴇʀs\n\n"
    "<b>ᴇxᴀᴍᴘʟᴇ</b>\n"
    "<code>/gcast -user hello!</code>"
),

"help_blchat": (
    "<b>🚫 ᴄʜᴀᴛ ʙʟᴏᴄᴋɪɴɢ</b>\n"
    "<i>ᴏᴡɴᴇʀ ᴏɴʟʏ</i>\n\n"
    "<b>/gblock</b> — ʙʟᴏᴄᴋ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ\n"
    "<b>/gblock</b> <code>-100xxxxxxx</code> — ʙʟᴏᴄᴋ ʙʏ ᴄʜᴀᴛ ɪᴅ\n"
    "<b>/gunblock</b> — ʀᴇᴍᴏᴠᴇ ᴄʜᴀᴛ ʙʟᴏᴄᴋ\n"
    "<b>/gunblock</b> <code>-100xxxxxxx</code> — ᴜɴʙʟᴏᴄᴋ ʙʏ ɪᴅ\n"
    "<b>/blocklist</b> — ᴠɪᴇᴡ ʙʟᴏᴄᴋᴇᴅ ᴄʜᴀᴛs & ᴜsᴇʀs"
),

"help_blusers": (
    "<b>🚫 ᴜsᴇʀ ʙʟᴏᴄᴋɪɴɢ</b>\n"
    "<i>ᴏᴡɴᴇʀ ᴏɴʟʏ</i>\n\n"
    "<b>/ublock</b> — ʀᴇᴘʟʏ ᴛᴏ ʙʟᴏᴄᴋ ᴀ ᴜsᴇʀ\n"
    "<b>/ublock</b> <code>123456789</code> — ʙʟᴏᴄᴋ ʙʏ ɪᴅ\n"
    "<b>/uunblock</b> — ʀᴇᴍᴏᴠᴇ ᴜsᴇʀ ʙʟᴏᴄᴋ\n"
    "<b>/uunblock</b> <code>123456789</code> — ᴜɴʙʟᴏᴄᴋ ʙʏ ɪᴅ\n"
    "<b>/blocklist</b> — ᴠɪᴇᴡ ʙʟᴏᴄᴋᴇᴅ ᴀᴄᴄᴏᴜɴᴛs"
),

"help_ping": (
    "<b>🏓 ʙᴏᴛ ᴍᴇᴛʀɪᴄs</b>\n\n"
    "<b>/ping</b> — ᴄʜᴇᴄᴋ ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ & sʏsᴛᴇᴍ ʟᴏᴀᴅ\n"
    "<b>/speedtest</b> <i>ᴏʀ</i> <b>/spt</b> — ʀᴜɴ ᴀ sᴘᴇᴇᴅ ᴛᴇsᴛ\n"
    "<b>/stats</b> — ᴠɪᴇᴡ sʏsᴛᴇᴍ & ᴅᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs\n\n"
    "<i>⚡ sᴏᴍᴇ ᴍᴇᴛʀɪᴄs ᴀʀᴇ ᴏᴡɴᴇʀ-ᴏɴʟʏ.</i>"
),

"help_play": (
    "<b>🎵 ᴘʟᴀʏʙᴀᴄᴋ</b>\n\n"
    "<b>/play</b> <code>&lt;song or url&gt;</code> — ᴘʟᴀʏ ᴀᴜᴅɪᴏ\n"
    "<b>/vplay</b> <code>&lt;song or url&gt;</code> — ᴘʟᴀʏ ᴠɪᴅᴇᴏ\n"
    "<b>ʀᴇᴘʟʏ + /play</b> — ᴘʟᴀʏ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ\n\n"
    "<b>ʟɪᴍɪᴛs</b>\n"
    f"ᴍᴀxɪᴍᴜᴍ ᴅᴜʀᴀᴛɪᴏɴ : <code>{config.MAX_DURATION_SECONDS // 60} ᴍɪɴ</code>\n"
    f"ǫᴜᴇᴜᴇ ʟɪᴍɪᴛ : <code>{config.QUEUE_LIMIT} ᴛʀᴀᴄᴋs</code>"
),

"help_speed": (
    "<b>🎚️ sᴘᴇᴇᴅ & ᴇғғᴇᴄᴛs</b>\n\n"
    "<b>/speed</b> <code>&lt;0.25 – 4.0&gt;</code> — ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ\n"
    "<b>/speedreset</b> — ʀᴇsᴛᴏʀᴇ 1.0x\n"
    "<b>/bass</b> <code>&lt;1 – 20&gt;</code> — ᴀᴅᴊᴜsᴛ ʙᴀss ʙᴏᴏsᴛ\n"
    "<b>/bassoff</b> — ᴅɪsᴀʙʟᴇ ʙᴀss ʙᴏᴏsᴛ\n"
    "<b>/effecton</b> — ᴇɴᴀʙʟᴇ ᴀᴜᴅɪᴏ ᴇғғᴇᴄᴛs\n"
    "<b>/effectoff</b> — ᴅɪsᴀʙʟᴇ ᴇғғᴇᴄᴛs\n"
    "<b>/effects</b> — ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs"
),

"help_info": (
    "<b>ℹ️ ɪɴғᴏ & ᴜᴛɪʟɪᴛɪᴇs</b>\n\n"
    "<b>/id</b> — ɢᴇᴛ ᴜsᴇʀ, ᴄʜᴀᴛ ᴏʀ ᴍᴇssᴀɢᴇ ɪᴅ\n"
    "<b>/id</b> <code>@username</code> — ʟᴏᴏᴋ ᴜᴘ ᴀ ᴜsᴇʀ ɪᴅ\n"
    "<b>/repo</b> — ᴏᴘᴇɴ ᴛʜᴇ sᴏᴜʀᴄᴇ ʀᴇᴘᴏsɪᴛᴏʀʏ\n"
    "<b>/stats</b> — ᴠɪᴇᴡ sʏsᴛᴇᴍ & ᴅʙ sᴛᴀᴛɪsᴛɪᴄs"
),
}


# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖
#    callback query handler router
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
        f"<b>✦ ʜᴇʟʟᴏ</b> <a href='tg://user?id={uid}'>{name}</a> 👋\n\n"
        f"<b>╰┈➤ ɪ'ᴍ {config.BOT_NAME}</b> — ʏᴏᴜʀ ᴍᴜsɪᴄ ʙᴏᴛ ғᴏʀ ᴄʜᴀᴛs.\n\n"
        "<b>❖ ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ</b>\n\n"
        "<b>› ᴘʟᴀʏ ʏᴏᴜʀ ғᴀᴠᴏᴜʀɪᴛᴇ sᴏɴɢs ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.</b>\n\n"
        "<b>› ᴇɴᴊᴏʏ ғᴀsᴛ & sᴍᴏᴏᴛʜ ʜᴅ ᴘʟᴀʏʙᴀᴄᴋ.</b>\n\n"
        "<b>› ᴍᴜᴄʜ ᴍᴏʀᴇ ᴛᴏ ᴇxᴘʟᴏʀᴇ.</b>\n\n"
        "<b>╰─➤ ᴛᴀᴘ ʜᴇʟᴘ ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs & ᴍᴏʀᴇ ɪɴғᴏ.</b>"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ",
                url=f"{config.BOT_LINK}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                "ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs",
                callback_data="show_help"
            ),
            InlineKeyboardButton(
                "ᴏᴡɴᴇʀ",
                url="https://t.me/nyxzre"
            )
        ],
        [
            InlineKeyboardButton(
                "ᴜᴘᴅᴀᴛᴇs",
                url=config.UPDATES_CHANNEL
            )
        ]
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
