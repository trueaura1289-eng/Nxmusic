import asyncio
import logging
import re

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    ChatAdminRequired,
    ChatForwardsRestricted,
    ChatWriteForbidden,
    FloodWait,
    MediaEmpty,
    MessageIdInvalid,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message

import config
from ShizuMusic import bot
from ShizuMusic.utils.db import (
    get_broadcast_chats,
    get_broadcast_count,
    remove_broadcast_chat,
)

logger = logging.getLogger(__name__)

# ❖ broadcast safety guard lock ❖
_is_broadcasting_active = False
_broadcast_sync_lock  = asyncio.Lock()

# ❖ execution flags info ❖
#
#   /broadcast or /gcast — reply to any text or pass message right after cmd
#
#   -pin        → stick message silently inside groups
#   -pinloud    → stick message with alert sound in groups
#   -nogroup    → skip groups, route strictly to dm users
#   -user       → send copies to dm users as well
#
#   examples:
#     /broadcast -pin               (reply to msg — groups only, silent stick)
#     /broadcast -pinloud -user     (reply to msg — groups plus users, loud stick)
#     /broadcast -nogroup -user     (reply to msg — dm users only)
#     /broadcast hey guys           (text mode — groups)
#     /gcast -user hi               (text mode — groups plus users)
#
# ❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖❖


def _extract_flag_options(content: str) -> tuple[bool, bool, bool, bool]:
    """
    returns tuple: (pin, pinloud, nogroup, user).
    fix applied: regex word-boundary utilized so -pin won't trigger inside -pinloud.
    """
    pin     = bool(re.search(r"-pin(?!loud)", content))
    pinloud = "-pinloud" in content
    nogroup = "-nogroup" in content
    user    = "-user"    in content
    return pin, pinloud, nogroup, user


def _clean_out_flags(txt: str) -> str:
    """strip all control flags out, yielding purely core payload text."""
    for tag in ("-pinloud", "-nogroup", "-user", "-pin"):
        txt = txt.replace(tag, "")
    return txt.strip()


# ❖ delivery handler — forward payload with safe fallback copy routine for protected chats ❖

async def _dispatch_single(receiver_id: int, base_msg: Message, mode_type: str, payload_text: str) -> Message:
    """
    pushes broadcast item to a single destination chat.
    for reply payload type: attempts native forward first, falls back to copy_message
    so restricted/protected group contents go through smoothly without breaking.
    raises error on hard failure.
    """
    if mode_type == "text":
        return await bot.send_message(receiver_id, payload_text, parse_mode=ParseMode.HTML)

    # try native forward pass first
    try:
        return await bot.forward_messages(receiver_id, base_msg.chat.id, base_msg.id)
    except (ChatForwardsRestricted, MediaEmpty, MessageIdInvalid):
        # fallback path: copy content cleanly without forwarding tag headers
        return await bot.copy_message(receiver_id, base_msg.chat.id, base_msg.id)


# ❖ primary command routing ❖

@bot.on_message(
    filters.command(["broadcast", "gcast"])
    & filters.user(config.OWNER_ID)
)
async def broadcast_command_entry(_, message: Message) -> None:
    global _is_broadcasting_active

    async with _broadcast_sync_lock:
        if _is_broadcasting_active:
            await message.reply(
                "<b>❖ ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ʀɪɢʜᴛ ɴᴏᴡ.</b>\n"
                "<b>❖ ᴘʟᴇᴀsᴇ ʜᴏʟᴅ ᴏɴ ᴜɴᴛɪʟ ɪᴛ ᴄᴏᴍᴘʟᴇᴛᴇs.</b>",
                parse_mode=ParseMode.HTML,
            )
            return
        _is_broadcasting_active = True

    try:
        await _execute_broadcast_routine(message)
    finally:
        _is_broadcasting_active = False


async def _execute_broadcast_routine(message: Message) -> None:

    # ❖ parse input arguments ❖
    raw_content = message.text or ""
    try:
        parsed_args = raw_content.split(None, 1)[1]
    except IndexError:
        parsed_args = ""

    f_pin, f_pinloud, f_nogroup, f_user = _extract_flag_options(parsed_args)
    pure_payload = _clean_out_flags(parsed_args)

    # ❖ figure out content payload type ❖
    if message.reply_to_message:
        base_msg   = message.reply_to_message
        mode_type = "reply"
    elif pure_payload:
        base_msg   = None
        mode_type = "text"
    else:
        await message.reply(
            "<b>❖ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴛʏᴘᴇ ᴛᴇxᴛ ᴄᴏɴᴛᴇɴᴛ.</b>\n\n"
            "<b>❖ ᴀᴠᴀɪʟᴀʙʟᴇ ғʟᴀɢs :</b>\n"
            "<code>-pin</code>     → sᴛɪᴄᴋ sɪʟᴇɴᴛʟʏ ɪɴ ɢʀᴏᴜᴘs\n"
            "<code>-pinloud</code>  → sᴛɪᴄᴋ ᴡɪᴛʜ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ\n"
            "<code>-nogroup</code>  → sᴋɪᴘ ɢʀᴏᴜᴘ ᴄʜᴀᴛs\n"
            "<code>-user</code>     → ᴀʟsᴏ ᴅɪsᴘᴀᴛᴄʜ ᴛᴏ ᴅᴍ ᴜsᴇʀs",
            parse_mode=ParseMode.HTML,
        )
        return

    # ❖ fetch data records from database ❖
    all_chat_docs = get_broadcast_chats()
    totals_info   = get_broadcast_count()
    group_list    = [d for d in all_chat_docs if d.get("type") == "group"]
    private_list  = [d for d in all_chat_docs if d.get("type") == "private"]

    computed_targets = (0 if f_nogroup else len(group_list)) + (len(private_list) if f_user else 0)

    if computed_targets == 0:
        await message.reply(
            "<b>❖ ɴᴏ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛs ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ʀᴇᴄᴏʀᴅs.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    # active flag tags string summary
    active_flags_str = " ".join(filter(None, [
        "-pin"     if f_pin     else "",
        "-pinloud" if f_pinloud else "",
        "-nogroup" if f_nogroup else "",
        "-user"    if f_user    else "",
    ])) or "ɴᴏɴᴇ"

    status_tracker_msg = await message.reply(
        f"<b>❖ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
        f"<b>❖ ᴛᴏᴛᴀʟ   :</b> <code>{totals_info['total']}</code>\n"
        f"<b>❖ ɢʀᴏᴜᴘs  :</b> <code>{len(group_list)}</code>\n"
        f"<b>❖ ᴜsᴇʀs   :</b> <code>{len(private_list)}</code>\n"
        f"<b>❖ ᴛᴀʀɢᴇᴛs :</b> <code>{computed_targets}</code>\n"
        f"<b>❖ ғʟᴀɢs   :</b> <code>{active_flags_str}</code>",
        parse_mode=ParseMode.HTML,
    )

    success_groups_count = success_users_count = pinned_count = failed_count = 0

    # ❖ group routing phase ❖
    if not f_nogroup:
        for item_doc in group_list:
            chat_identifier = int(item_doc["chat_id"])
            try:
                sent_msg = await _dispatch_single(chat_identifier, base_msg, mode_type, pure_payload)
                success_groups_count += 1

                if f_pin or f_pinloud:
                    try:
                        await bot.pin_chat_message(
                            chat_identifier, sent_msg.id,
                            disable_notification=not f_pinloud,
                        )
                        pinned_count += 1
                    except ChatAdminRequired:
                        pass
                    except Exception:
                        pass

            except FloodWait as flood_err:
                wait_duration = int(flood_err.value)
                if wait_duration > 200:
                    failed_count += 1
                    continue
                await asyncio.sleep(wait_duration)
                try:
                    await _dispatch_single(chat_identifier, base_msg, mode_type, pure_payload)
                    success_groups_count += 1
                except Exception:
                    failed_count += 1

            except (UserIsBlocked, ChatWriteForbidden, PeerIdInvalid):
                remove_broadcast_chat(chat_identifier)
                failed_count += 1

            except Exception as runtime_err:
                logger.warning(f"[Broadcast] group target {chat_identifier}: {runtime_err}")
                failed_count += 1

            await asyncio.sleep(1.5)

    # ❖ private dm routing phase ❖
    if f_user:
        for item_doc in private_list:
            user_identifier = int(item_doc["chat_id"])
            try:
                await _dispatch_single(user_identifier, base_msg, mode_type, pure_payload)
                success_users_count += 1

            except FloodWait as flood_err:
                wait_duration = int(flood_err.value)
                if wait_duration > 200:
                    failed_count += 1
                    continue
                await asyncio.sleep(wait_duration)
                try:
                    await _dispatch_single(user_identifier, base_msg, mode_type, pure_payload)
                    success_users_count += 1
                except Exception:
                    failed_count += 1

            except (UserIsBlocked, PeerIdInvalid):
                remove_broadcast_chat(user_identifier)
                failed_count += 1

            except Exception as runtime_err:
                logger.warning(f"[Broadcast] user target {user_identifier}: {runtime_err}")
                failed_count += 1

            await asyncio.sleep(1.5)

    # ❖ wrap up final update ❖
    await status_tracker_msg.edit_text(
        "<b>❖ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅</b>\n\n"
        f"<b>❖ ɢʀᴏᴜᴘs :</b> <code>{success_groups_count}</code>\n"
        f"<b>❖ ᴜsᴇʀs  :</b> <code>{success_users_count}</code>\n"
        f"<b>❖ ᴘɪɴɴᴇᴅ :</b> <code>{pinned_count}</code>\n"
        f"<b>❖ ғᴀɪʟᴇᴅ :</b> <code>{failed_count}</code>",
        parse_mode=ParseMode.HTML,
    )
