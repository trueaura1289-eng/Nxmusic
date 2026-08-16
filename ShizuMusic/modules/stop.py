from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.queue import clear_queue, queue_size
from ShizuMusic.modules.block import group_allowed, user_allowed
from ShizuMusic.utils.permissions import is_user_authorized


# ── /stop & /end ──────────────────────────────────────────────────────────────

@bot.on_message(
    filters.group
    & filters.command(["stop", "end"])
    & group_allowed
    & user_allowed
)
async def stop_cmd(_, message: Message) -> None:

    if not await is_user_authorized(message):
        await message.reply(
            "<b>❖ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    await leave_vc(message.chat.id)

    await message.reply(
        "<b>❖ ᴍᴜsɪᴄ ᴇɴᴅᴇᴅ • ǫᴜᴇᴜᴇ ʀᴇsᴇᴛ • ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇxɪᴛᴇᴅ</b>",
        parse_mode=ParseMode.HTML,
    )


# ── /clear ─────────────────────────────────────────────────────────────────────

@bot.on_message(
    filters.group
    & filters.command("clear")
    & group_allowed
    & user_allowed
)
async def clear_cmd(_, message: Message) -> None:

    if not await is_user_authorized(message):
        await message.reply(
            "<b>❖ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    chat_id = message.chat.id

    try:
        from ShizuMusic.core.autoplay import stop_autoplay
        stop_autoplay(chat_id)
    except Exception:
        pass

    if not queue_size(chat_id):
        await message.reply(
            "<b>❖ ɴᴏ sᴏɴɢs ᴀʀᴇ ǫᴜᴇᴜᴇᴅ</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    clear_queue(chat_id)
    await message.reply(
        "<b>❖ ᴀʟʟ ᴛʀᴀᴄᴋs ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ǫᴜᴇᴜᴇ</b>\n"
        "<b>❖ ǫᴜᴇᴜᴇ ʜᴀs ʙᴇᴇɴ ᴇᴍᴘᴛɪᴇᴅ</b>",
        parse_mode=ParseMode.HTML,
    )


# ── /reboot ────────────────────────────────────────────────────────────────────

@bot.on_message(
    filters.command("reboot")
    & group_allowed
    & user_allowed
)
async def reboot_cmd(_, message: Message) -> None:
    await leave_vc(message.chat.id)
    await message.reply(
        "<b>❖ ᴄʜᴀᴛ ʀᴇʙᴏᴏᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ</b>\n"
        "<b>❖ ᴄʜᴀᴛ sᴛᴀᴛᴇ ʜᴀs ʙᴇᴇɴ ʀᴇsᴇᴛ ᴄʟᴇᴀʀʟʏ</b>",
        parse_mode=ParseMode.HTML,
    )
