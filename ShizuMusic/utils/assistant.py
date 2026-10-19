"""
Assistant utility functions.
Handles checking whether the assistant is in a group and auto-joining it.
Includes smart anti-flood protection and dynamic unban-detection.
"""

import asyncio
import time

from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import RPCError, UserAlreadyParticipant, InviteHashExpired, FloodWait
from pyrogram.types import Message

from ShizuMusic import assistant, bot

# Cooldown dictionary to prevent spamming invite links on banned chats
# Format: {chat_id: expire_timestamp}
_JOIN_COOLDOWN = {}
COOLDOWN_DURATION = 300  # 5 minutes cooldown (in seconds)


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
        if "USER_BANNED" in err or "BANNED" in err or "USER_IS_BLOCKED" in err or "CHAT_ADMIN_REQUIRED" in err:
            return "banned"
        return False


async def try_join_assistant(chat_id: int, pm: Message) -> bool:
    """
    Attempt to make the assistant join the group via invite link with smart anti-flood protection.

    Args:
        chat_id: Target group chat ID.
        pm:      Status message to edit with progress / error text.

    Returns:
        True on success, False on failure.
    """
    current_time = time.time()
    
    # 1. Pehle check karo ki assistant group me present hai ya unban ho chuka hai.
    # Agar assistant ab unban ho chuka hai, toh cooldown ko turant hata do aur aage badho!
    status = await is_assistant_in(chat_id)
    if status is True:
        if chat_id in _JOIN_COOLDOWN:
            del _JOIN_COOLDOWN[chat_id]
        return True

    # 2. Agar assistant abhi bhi banned hai, toh check karo ki cooldown chal raha hai ya nahi.
    if chat_id in _JOIN_COOLDOWN:
        remaining = _JOIN_COOLDOWN[chat_id] - current_time
        if remaining > 0:
            # Cooldown active hai aur unban nahi hua, bina API call kiye seedha return karo (No Flood Wait / No Link Revoke)
            return False
        else:
            del _JOIN_COOLDOWN[chat_id]

    # 3. Agar status "banned" hai, toh cooldown set karo aur msg bhej do (Link export nahi hoga!)
    if status == "banned":
        _JOIN_COOLDOWN[chat_id] = current_time + COOLDOWN_DURATION
        await pm.edit_text(
            "<b>❖ Uɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ.</b>\n"
            "<code>Telegram says: Assistant is banned in this chat. Please unban the assistant first. @ElyxAssistant</code>",
            parse_mode=ParseMode.HTML,
        )
        return False

    try:
        # Export invite link via bot (Yeh tabhi chalega jab assistant banned nahi hoga)
        invite_link = await bot.export_chat_invite_link(chat_id)

    except FloodWait as e:
        _JOIN_COOLDOWN[chat_id] = current_time + e.value
        await pm.edit_text(
            f"<b>❖ ᴛᴇʟᴇɢʀᴀᴍ ғʟᴏᴏᴅ ᴡᴀɪᴛ</b>\n"
            f"<code>Please wait {e.value} seconds before trying again.</code>",
            parse_mode=ParseMode.HTML,
        )
        return False
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

    except FloodWait as e:
        _JOIN_COOLDOWN[chat_id] = current_time + e.value
        await pm.edit_text(
            f"<b>❖ ᴛᴇʟᴇɢʀᴀᴍ ғʟᴏᴏᴅ ᴡᴀɪᴛ</b>\n"
            f"<code>Assistant join rate-limited. Please wait {e.value} seconds.</code>",
            parse_mode=ParseMode.HTML,
        )
        return False

    except (InviteHashExpired, RPCError) as e:
        err_msg = str(e).upper()
        if "INVITE_HASH_EXPIRED" in err_msg or "BANNED" in err_msg:
            _JOIN_COOLDOWN[chat_id] = current_time + COOLDOWN_DURATION
            msg = (
                "<b>❖ Uɴᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ.</b>\n"
                "<code>The Assistant might be banned or restricted in this group. Unban the assistant to continue. @ElyxAssistant</code>"
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
