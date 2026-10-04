"""
Assistant utility functions.
Handles checking whether the assistant is in a group and auto-joining it.
Previously this logic was inline in play.py — now centralised here.
"""

import asyncio

from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import RPCError, UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import Message

from ShizuMusic import assistant, bot


async def is_assistant_in(chat_id: int):
    """
    Check whether the assistant is a member of the given group.

    Returns:
        True     — assistant is present
        False    — assistant is not present
        "banned" — assistant was banned from the group
    """
    try:
        me = await assistant.get_me()
        member = await assistant.get_chat_member(chat_id, me.id)
        
        # Check if the user is banned or left/kicked
        if member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]:
            return "banned"
            
        return True

    except Exception as e:
        err = str(e).upper()
        if "USER_BANNED" in err or "BANNED" in err or "USER_IS_BLOCKED" in err:
            return "banned"
        return False


async def try_join_assistant(chat_id: int, pm: Message) -> bool:
    """
    Attempt to make the assistant join the group via invite link.

    Args:
        chat_id: Target group chat ID.
        pm:      Status message to edit with progress / error text.

    Returns:
        True on success, False on failure.
    """
    # Pehle hi check kar lo kya assistant banned to nahi hai is chat me
    status = await is_assistant_in(chat_id)
    if status == "banned":
        await pm.edit_text(
            "<b>❖ ᴜɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ.</b>\n"
            "<code>Telegram says: Assistant is banned in this chat. Please unban the assistant first.</code>",
            parse_mode=ParseMode.HTML,
        )
        return False

    try:
        invite_link = await bot.export_chat_invite_link(chat_id)

    except Exception as e:
        await pm.edit_text(
            f"<b>❖ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴘᴇʀᴍɪssɪᴏɴ ɪs ʀᴇǫᴜɪʀᴇᴅ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.</b>\n"
            f"<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return False

    try:
        # Normalise joinchat link format
        if invite_link.startswith("https://t.me/+"):
            invite_link = invite_link.replace(
                "https://t.me/+",
                "https://t.me/joinchat/",
            )

        await assistant.join_chat(invite_link)
        await asyncio.sleep(2)
        return True

    except UserAlreadyParticipant:
        return True

    except (InviteHashExpired, RPCError) as e:
        err_msg = str(e)
        if "INVITE_HASH_EXPIRED" in err_msg:
            msg = (
                "<b>❖ Uɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ.</b>\n"
                "<code>Tʜᴇ Aѕѕɪѕᴛᴀɴᴛ Mɪɢʜᴛ Bᴇ Bᴀɴɴᴇᴅ Oʀ Rᴇѕᴛʀɪᴄᴛᴇᴅ Iɴ Tʜɪѕ Gʀᴏᴜᴘ. Uɴʙᴀɴ Tʜᴇ Aѕѕɪѕᴛᴀɴᴛ Tᴏ Cᴏɴᴛɪɴᴜᴇ @ElyxAssistant.</code>"
            )
        else:
            msg = (
                f"<b>❖ Uɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ.</b>\n"
                f"<code>{e}</code>"
            )
        
        await pm.edit_text(msg, parse_mode=ParseMode.HTML)
        return False

    except Exception as e:
        await pm.edit_text(
            f"<b>● ᴊᴏɪɴ ᴇʀʀᴏʀ</b>\n"
            f"<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return False
