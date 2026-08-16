from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ShizuMusic import bot, call_py
from ShizuMusic.modules.block import group_allowed, user_allowed
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_message(
    filters.group
    & filters.command("resume")
    & group_allowed
    & user_allowed
)
async def resume_cmd(_, message: Message) -> None:

    if not await is_user_authorized(message):
        await message.reply(
            "<b>❖ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        await call_py.resume(message.chat.id)
        await message.reply(
            "<b>❖ ʀᴇsᴜᴍᴇᴅ, sᴛʀᴇᴀᴍ ɪs ʙᴀᴄᴋ ᴜᴘ ᴀɴᴅ ʀᴜɴɴɪɴɢ</b>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply(
            f"<b>❖ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇsᴜᴍᴇ ᴘʟᴀʏʙᴀᴄᴋ</b>\n<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
