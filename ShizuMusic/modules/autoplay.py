import asyncio

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot
from ShizuMusic.core.autoplay import (
    get_autoplay_query,
    is_autoplay,
    start_autoplay,
    stop_autoplay,
)
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import peek_current, queue_size
from ShizuMusic.modules.block import group_allowed, user_allowed
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.regex(r"^/autoplay(?:@\w+)?(?:\s+(?P<q>.+))?$")
    & group_allowed
    & user_allowed
)
async def autoplay_cmd(_, message: Message) -> None:

    chat_id = message.chat.id
    user    = message.from_user

 if not await is_user_authorized(message):
        await message.reply(
            "<b>❖ ᴘʟᴀʏ ᴀᴄᴄᴇss ʀᴇsᴛʀɪᴄᴛᴇᴅ</b>\n"
            "<b>❖ /ᴀᴜᴛᴏᴘʟᴀʏ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    match = message.matches[0]
    query = (match.group("q") or "").strip()

    if not query:
        current_q = get_autoplay_query(chat_id)
        if is_autoplay(chat_id) and current_q:
         await message.reply(
    f"<b>❖ ᴀᴜᴛᴏᴘʟᴀʏ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ</b>\n"
    f"<b>❖ ᴄᴜʀʀᴇɴᴛ ǫᴜᴇʀʏ :</b> <code>{current_q}</code>\n"
    f"<b>❖ ᴜsᴇ /ᴇɴᴅ ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ ʙᴇғᴏʀᴇ sᴛᴀʀᴛɪɴɢ ᴀɢᴀɪɴ</b>",
    parse_mode=ParseMode.HTML,
)
        else:
           await message.reply(
    "<b>❖ ᴀᴜᴛᴏᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅ :</b> <code>/autoplay Tere liye</code>\n"
    "<b>❖ ᴇɴᴛᴇʀ ᴀ ᴛᴏᴘɪᴄ ᴀɴᴅ ʟᴇᴛ ᴛʜᴇ ʙᴏᴛ ᴋᴇᴇᴘ ᴛʜᴇ ᴍᴜsɪᴄ ɢᴏɪɴɢ</b>",
    parse_mode=ParseMode.HTML,
)
        return

    pm = await message.reply(
    f"<b>❖ ᴀᴜᴛᴏᴘʟᴀʏ ɪs ʙᴇɪɴɢ ᴘʀᴇᴘᴀʀᴇᴅ</b>\n"
    f"<b>❖ sᴇᴀʀᴄʜɪɴɢ ғᴏʀ :</b> <code>{query}</code>",
    parse_mode=ParseMode.HTML,
)

    req    = user.first_name if user else "AutoPlay"
    req_id = user.id         if user else 0

    was_playing = queue_size(chat_id) > 0
    count       = await start_autoplay(chat_id, query, req, req_id)

    if count == 0:
        stop_autoplay(chat_id)
        await pm.edit_text(
    "<b>❖ ᴄᴏᴜʟᴅɴ'ᴛ sᴛᴀʀᴛ ᴀᴜᴛᴏᴘʟᴀʏ</b>\n"
    "<b>❖ ᴛʜᴇʀᴇ ᴡᴀs ɴᴏ ᴛʀᴀᴄᴋ ᴍᴀᴛᴄʜɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ</b>",
    parse_mode=ParseMode.HTML,
)
        return

    first = peek_current(chat_id)

   await pm.edit_text(
    f"<b>❖ ᴀᴜᴛᴏᴘʟᴀʏ ɪs ɴᴏᴡ ʟɪᴠᴇ</b>\n"
    f"<b>❖ sᴇᴀʀᴄʜ :</b> <code>{query}</code>\n"
    f"<b>❖ {count} ᴛʀᴀᴄᴋs ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ᴘʟᴀʏʟɪsᴛ</b>\n"
    f"<b>❖ ᴛʏᴘᴇ /ᴇɴᴅ ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏᴘʟᴀʏ</b>",
    parse_mode=ParseMode.HTML,
)

    if not was_playing and first:
        dm = await bot.send_message(
            chat_id,
            f"<b>❖ ᴄᴜʀʀᴇɴᴛʟʏ ᴘʟᴀʏɪɴɢ :</b> <code>{short(first['title'])}</code>",
            parse_mode=ParseMode.HTML,
        )
        await play_song(chat_id, dm, first)

    try:
        await message.delete()
    except Exception:
        pass
