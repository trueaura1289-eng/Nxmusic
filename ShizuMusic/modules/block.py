from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot
from ShizuMusic.utils.db import (
    block_group,
    unblock_group,
    is_group_blocked,
    get_blocked_groups,
    block_user,
    unblock_user,
    is_user_blocked_db,
    get_blocked_users,
)


# ── Pyrogram filters (import these in other modules) ──────────────────────────

def _group_not_blocked(_, __, message: Message) -> bool:
    if message.chat and message.chat.id:
        return not is_group_blocked(message.chat.id)
    return True


def _user_not_blocked(_, __, message: Message) -> bool:
    if message.from_user and message.from_user.id:
        return not is_user_blocked_db(message.from_user.id)
    return True


group_allowed = filters.create(_group_not_blocked)
user_allowed  = filters.create(_user_not_blocked)


# ── /gblock ────────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("gblock") & filters.user(config.OWNER_ID))
async def gblock_cmd(_, message: Message) -> None:
    """Block a group — /gblock or /gblock -100xxxxxxx"""
    parameters = message.command[1:]

    if parameters:
        try:
            target_chat_id = int(parameters[0])
        except ValueError:
            await message.reply(
                "<b>❖ ᴘʀovɪᴅᴇᴅ ᴄʜᴀᴛ ɪᴅ ɪs ɪɴᴄoʀʀᴇᴄᴛ</b>\n"
                "<b>❖ ᴄᴏʀʀᴇᴄᴛ sʏɴᴛᴀx : /gblock -100xxxxxxx</b>",
                parse_mode=ParseMode.HTML,
            )
        return
    else:
        if message.chat.type.name == "PRIVATE":
           await message.reply(
    "<b>❖ ᴛʜɪs ᴜᴛɪʟɪᴛʏ ɪs sᴛʀɪᴄᴛʟʏ ғᴏʀ ɢʀᴏᴜᴘs</b>\n"
    "<b>❖ ᴏʀ ɪɴᴘᴜᴛ ᴀ ᴄʜᴀᴛ ɪᴅ : /gblock -100xxxxxxx</b>",
parse_mode=ParseMode.HTML,
)
return
target_chat_id = message.chat.id

if is_group_blocked(target_chat_id):
    await message.reply(
        f"<b>❖ ᴛʜɪs ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ʙʟᴏᴄᴋʟɪsᴛᴇᴅ</b>\n"
        f"<b>❖ ᴄʜᴀᴛ ɪᴅ :</b> <code>{target_chat_id}</code>",
        parse_mode=ParseMode.HTML,
    )
    return

block_group(target_chat_id)
await message.reply(
    f"<b>❖ ᴄʜᴀᴛ ʜᴀs ʙᴇᴇɴ ʙʟᴏᴄᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ</b>\n"
    f"<b>❖ ɪᴅ :</b> <code>{target_chat_id}</code>\n"
    f"<b>❖ ʙᴏᴛ ғᴜɴᴄᴛɪᴏɴs ᴀʀᴇ ɴᴏᴡ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ ʜᴇʀᴇ</b>",
    parse_mode=ParseMode.HTML,
)


# ── /gunblock ──────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("gunblock") & filters.user(config.OWNER_ID))
async def gunblock_cmd(_, message: Message) -> None:
    """Unblock a group — /gunblock or /gunblock -100xxxxxxx"""
    parameters = message.command[1:]

    if parameters:
        try:
           target_chat_id = int(parameters[0])
except ValueError:
    await message.reply(
        "<b>❖ ᴛʜᴇ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀᴛ ɪᴅ ɪs ғᴀᴜʟᴛʏ</b>\n"
        "<b>❖ sᴀᴍᴘʟᴇ : /gunblock -100xxxxxxx</b>",
        parse_mode=ParseMode.HTML,
    )
    return
else:
    if message.chat.type.name == "PRIVATE":
        await message.reply(
            "<b>❖ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ɪɴsɪᴅᴇ ᴀ ɢʀᴏᴜᴘ</b>\n"
            "<b>❖ ᴏʀ ᴘᴀss ᴀ ᴄʜᴀᴛ ɪᴅ : /gunblock -100xxxxxxx</b>",
            parse_mode=ParseMode.HTML,
        )
            return
        target_chat_id = message.chat.id

  if not is_group_blocked(target_chat_id):
    await message.reply(
        f"<b>❖ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴘʀᴇsᴇɴᴛ ᴏɴ ʙʟᴏᴄᴋʟɪsᴛ</b>\n"
        f"<b>❖ ᴄʜᴀᴛ ɪᴅ :</b> <code>{target_chat_id}</code>",
        parse_mode=ParseMode.HTML,
    )
    return

unblock_group(target_chat_id)
await message.reply(
    f"<b>❖ ᴄʜᴀᴛ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ʀᴇɪɴsᴛᴀᴛᴇᴅ</b>\n"
    f"<b>❖ ᴄʜᴀᴛ ɪᴅ :</b> <code>{target_chat_id}</code>\n"
    f"<b>❖ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ɴᴏᴡ ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ</b>",
    parse_mode=ParseMode.HTML,
)


# ── /ublock ────────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("ublock") & filters.user(config.OWNER_ID))
async def ublock_cmd(_, message: Message) -> None:
    """Block a user — reply to their message or /ublock 123456789"""
    parameters = message.command[1:]
    target_member_id = None
    target_member_name = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_member_id = message.reply_to_message.from_user.id
        target_member_name = message.reply_to_message.from_user.first_name
    elif parameters:
        try:
            target_member_id = int(parameters[0])
        except ValueError:
           await message.reply(
    "<b>❖ ᴜsᴇʀ ɪᴅ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴘᴀʀsᴇᴅ</b>\n"
    "<b>❖ ғᴏʀᴍᴀᴛ : /ublock 123456789 ᴏʀ ʀᴇᴘʟʏ</b>",
    parse_mode=ParseMode.HTML,
)
return
else:
    await message.reply(
        "<b>❖ ᴍᴇɴᴛɪᴏɴ ᴀ ᴜsᴇʀ ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇɪʀ ᴛᴇxᴛ</b>\n"
        "<b>❖ sᴀᴍᴘʟᴇ : /ublock 123456789</b>",
        parse_mode=ParseMode.HTML,
    )
        return

    if target_member_id == config.OWNER_ID:
await message.reply(
    "<b>❖ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴɴᴏᴛ ʙᴇ ʀᴇsᴛʀɪᴄᴛᴇᴅ</b>",
    parse_mode=ParseMode.HTML,
)
return

if is_user_blocked_db(target_member_id):
    await message.reply(
        f"<b>❖ ᴛʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ</b>\n"
        f"<b>❖ ᴜsᴇʀ ɪᴅ :</b> <code>{target_member_id}</code>",
        parse_mode=ParseMode.HTML,
    )
        return

    block_user(target_member_id)
    name_str = f" (<b>{target_member_name}</b>)" if target_member_name else ""
    await message.reply(
        f"<b>❖ ᴍᴇᴍʙᴇʀ ʙʟᴏᴄᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅</b>\n"
        f"<b>❖ ᴜsᴇʀ ɪᴅ :</b> <code>{target_member_id}</code>{name_str}\n"
        f"<b>❖ ᴛʜɪs ᴘᴇʀsᴏɴ ᴄᴀɴ ɴᴏ ʟᴏɴɢᴇʀ ᴇxᴇᴄᴜᴛᴇ ᴄᴏᴍᴍᴀɴᴅs.</b>",
        parse_mode=ParseMode.HTML,
    )


# ── /uunblock ──────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("uunblock") & filters.user(config.OWNER_ID))
async def uunblock_cmd(_, message: Message) -> None:
    """Unblock a user — reply to their message or /uunblock 123456789"""
    parameters = message.command[1:]
    target_member_id = None
    target_member_name = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_member_id = message.reply_to_message.from_user.id
        target_member_name = message.reply_to_message.from_user.first_name
    elif parameters:
        try:
            target_member_id = int(parameters[0])
        except ValueError:
            await message.reply(
                "<b>❖ ᴍᴀʟғᴏʀᴍᴇᴅ ᴜsᴇʀ ɪᴅ ᴘʀᴏᴠɪᴅᴇᴅ.</b>\n"
                "<b>❖ ᴜsᴀɢᴇ: /uunblock 123456789 ᴏʀ ʀᴇᴘʟʏ.</b>",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        await message.reply(
            "<b>❖ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɪɴᴘᴜᴛ ᴀ ᴜsᴇʀ ɪᴅ.</b>\n"
            "<b>❖ ᴜsᴀɢᴇ: /uunblock 123456789</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    if not is_user_blocked_db(target_member_id):
        await message.reply(
            f"<b>❖ ᴍᴇᴍʙᴇʀ <code>{target_member_id}</code> ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    unblock_user(target_member_id)
    name_str = f" (<b>{target_member_name}</b>)" if target_member_name else ""
    await message.reply(
        f"<b>❖ ᴍᴇᴍʙᴇʀ ᴜɴʙʟᴏᴄᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅</b>\n"
        f"<b>❖ ᴜsᴇʀ ɪᴅ :</b> <code>{target_member_id}</code>{name_str}\n"
        f"<b>❖ ᴛʜɪs ᴘᴇʀsᴏɴ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs.</b>",
        parse_mode=ParseMode.HTML,
    )


# ── /blocklist ─────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("blocklist") & filters.user(config.OWNER_ID))
async def blocklist_cmd(_, message: Message) -> None:
    """Show all blocked groups and users."""
    blocked_groups_collection = get_blocked_groups()
    blocked_users_collection = get_blocked_users()

    g_text = (
        "\n".join(f"   • <code>{g}</code>" for g in blocked_groups_collection)
        if blocked_groups_collection else "   ɴɪʟ"
    )
    u_text = (
        "\n".join(f"   • <code>{u}</code>" for u in blocked_users_collection)
        if blocked_users_collection else "   ɴɪʟ"
    )

    await message.reply(
        "<b>❖ ʀᴇsᴛʀɪᴄᴛɪᴏɴ ʀᴇᴄᴏʀᴅs</b>\n\n"
        f"<b>❖ ʙʟᴏᴄᴋᴇᴅ ᴄʜᴀᴛs ({len(blocked_groups_collection)}):</b>\n{g_text}\n\n"
        f"<b>❖ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs ({len(blocked_users_collection)}):</b>\n{u_text}",
        parse_mode=ParseMode.HTML,
    )
