import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import peek_current, pop_current, queue_size
from ShizuMusic.modules.block import group_allowed, user_allowed
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.helpers import delete_file
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.command("skip")
    & group_allowed
    & user_allowed
)
async def skip_cmd(_, message: Message) -> None:

    chat_id = message.chat.id

    if not await is_user_authorized(message):
        await message.reply(
            "<b>❖ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    if not queue_size(chat_id):
        await message.reply(
            "<b>❖ ɴᴏ sᴏɴɢs ᴀʀᴇ ǫᴜᴇᴜᴇᴅ</b>\n"
            "<b>❖ ɴᴏ sᴏɴɢ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ sᴋɪᴘᴘɪɴɢ</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    sm = await message.reply(
        "<b>❖ sᴋɪᴘᴘɪɴɢ ᴛʜɪs ᴛʀᴀᴄᴋ...</b>",
        parse_mode=ParseMode.HTML,
    )

    skipped = pop_current(chat_id)

    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass

    await asyncio.sleep(2)

    try:
        delete_file(skipped.get("file_path", ""))
    except Exception:
        pass

    nxt = peek_current(chat_id)

    if nxt:
        await sm.edit_text(
            f"<b>❖ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ :</b> <code>{short(skipped['title'])}</code>\n"
            f"<b>❖ ᴄᴜʀʀᴇɴᴛʟʏ ᴘʟᴀʏɪɴɢ :</b>\n<code>{nxt['title']}</code>",
            parse_mode=ParseMode.HTML,
        )
        dm = await bot.send_message(
            chat_id,
            f"<b>❖ ᴜᴘᴄᴏᴍɪɴɢ ᴛʀᴀᴄᴋ :</b> <code>{nxt['title']}</code>",
            parse_mode=ParseMode.HTML,
        )
        await play_song(chat_id, dm, nxt)
    else:
        await sm.edit_text(
            f"<b>❖ sᴋɪᴘᴘᴇᴅ ᴛʀᴀᴄᴋ :</b> <code>{short(skipped['title'])}</code>\n"
            "<b>❖ ɴᴏ ᴛʀᴀᴄᴋs ʀᴇᴍᴀɪɴ ɪɴ ᴛʜᴇ ǫᴜᴇᴜᴇ</b>",
            parse_mode=ParseMode.HTML,
        )
