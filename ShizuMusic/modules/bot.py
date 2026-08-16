import random

from pyrogram import filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot
from ShizuMusic.utils.db import (
    add_broadcast_chat,
    add_served_chat,
    remove_broadcast_chat,
    remove_served_chat,
)

LEFT_PHOTOS = [
    "https://freeimage.host/i/KLc203F"
]


# ── Bot added to group ─────────────────────────────────────────────────────────

@bot.on_message(filters.new_chat_members, group=-10)
async def bot_added_watcher(_, message: Message) -> None:
    try:
        current_chat    = message.chat
        chat_identifier = current_chat.id
        bot_user_obj    = await bot.get_me()

        for member_item in message.new_chat_members:
            if member_item.id != bot_user_obj.id:
                continue

            add_served_chat(chat_identifier)
            add_broadcast_chat(chat_identifier, "group")

            inviter_user    = message.from_user
            inviter_mention = inviter_user.mention if inviter_user else "ᴜɴᴋɴᴏᴡɴ"

            admin_request_text = (
    "<b>✦ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ɪs ʀᴇᴀᴅʏ 🎧</b>\n\n"
    "<b>❖ ᴏɴᴇ ʟᴀsᴛ sᴛᴇᴘ : ᴘʟᴇᴀsᴇ ɢʀᴀɴᴛ ᴍᴇ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss.</b>\n\n"
    "<b>ᴛʜɪs ᴀʟʟᴏᴡs ᴍᴇ ᴛᴏ :</b>\n"
    "<b>• ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs</b>\n"
    "<b>• ᴄᴏɴᴛʀᴏʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs</b>\n"
    "<b>• ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴘᴇʀᴍɪssɪᴏɴ</b>\n\n"
    "<b>❖ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs, ᴠᴏɪᴄᴇ ᴘʟᴀʏʙᴀᴄᴋ ᴍᴀʏ ɴᴏᴛ ᴡᴏʀᴋ ᴘʀᴏᴘᴇʀʟʏ.</b>"
)
            admin_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ɴᴏᴡ", url=f"tg://user?id={bot_user_obj.id}")
            ]])
            try:
                await message.reply_text(admin_request_text, parse_mode=ParseMode.HTML, reply_markup=admin_kb)
            except Exception:
                pass

            if not config.LOGGER_ID:
                return

            try:
                chat_invite_link = await bot.export_chat_invite_link(chat_identifier)
                link_text        = f"<a href='{chat_invite_link}'>ᴏʙᴛᴀɪɴ ʟɪɴᴋ</a>"
            except (ChatAdminRequired, Exception):
                link_text = "ɴᴏ ʟɪɴᴋ"

            try:
                member_count = await bot.get_chat_members_count(chat_identifier)
            except Exception:
                member_count = "N/A"

            group_username  = f"@{current_chat.username}" if current_chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
            chat_photo_path = None
            try:
                if current_chat.photo:
                    chat_photo_path = await bot.download_media(
                        current_chat.photo.big_file_id,
                        file_name=f"grppp_{chat_identifier}.png",
                    )
            except Exception:
                chat_photo_path = None

            log_text = (
                "<b>❖ #ɴᴇᴡɢʀᴏᴜᴘ ❖ ʙᴏᴛ ɪɴᴄᴏʀᴘᴏʀᴀᴛᴇᴅ!</b>\n\n"
                f"<b>❖ ᴄʜᴀᴛ ᴛɪᴛʟᴇ  :</b> {current_chat.title}\n"
                f"<b>❖ ᴄʜᴀᴛ ɪᴅ     :</b> <code>{chat_identifier}</code>\n"
                f"<b>❖ ᴜsᴇʀɴᴀᴍᴇ   :</b> {group_username}\n"
                f"<b>❖ ɪɴᴠɪᴛᴇ ᴜʀʟ  :</b> {link_text}\n"
                f"<b>❖ ᴛᴏᴛᴀʟ ᴜsᴇʀs :</b> {member_count}\n"
                f"<b>❖ ɪɴᴠɪᴛᴇᴅ ʙʏ :</b> {inviter_mention}"
            )
            log_kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"❖ {inviter_user.first_name if inviter_user else 'ᴜsᴇʀ'}",
                    user_id=inviter_user.id if inviter_user else config.OWNER_ID,
                )
            ]]) if inviter_user else None

            try:
                if chat_photo_path:
                    await bot.send_photo(
                        config.LOGGER_ID, photo=chat_photo_path,
                        caption=log_text, parse_mode=ParseMode.HTML, reply_markup=log_kb,
                    )
                else:
                    await bot.send_message(
                        config.LOGGER_ID, log_text,
                        parse_mode=ParseMode.HTML, reply_markup=log_kb,
                        disable_web_page_preview=True,
                    )
            except Exception:
                pass

    except Exception as err_msg:
        print(f"[watcher] bot_added_watcher error: {err_msg}")


# ── Bot left / removed ─────────────────────────────────────────────────────────

@bot.on_message(filters.left_chat_member, group=-12)
async def bot_left_watcher(_, message: Message) -> None:
    try:
        departed_member = message.left_chat_member
        if not departed_member:
            return

        bot_user_obj = await bot.get_me()
        if departed_member.id != bot_user_obj.id:
            return

        current_chat    = message.chat
        chat_identifier = current_chat.id

        remove_served_chat(chat_identifier)
        remove_broadcast_chat(chat_identifier)

        banner_user    = message.from_user
        banner_mention = banner_user.mention if banner_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        group_username = f"@{current_chat.username}" if current_chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"

        if not config.LOGGER_ID:
            return

        left_text = (
            "<b>❖ #ʟᴇғᴛɢʀᴏᴜᴘ ❖ ʙᴏᴛ ᴇᴊᴇᴄᴛᴇᴅ!</b>\n\n"
            f"<b>❖ ᴄʜᴀᴛ ᴛɪᴛʟᴇ  :</b> {current_chat.title}\n"
            f"<b>❖ ᴄʜᴀᴛ ɪᴅ     :</b> <code>{chat_identifier}</code>\n"
            f"<b>❖ ᴜsᴇʀɴᴀᴍᴇ   :</b> {group_username}\n"
            f"<b>❖ ᴇᴊᴇᴄᴛᴇᴅ ʙʏ :</b> {banner_mention}\n"
            f"<b>❖ ʙᴏᴛ ᴀᴄᴄᴏᴜɴᴛ:</b> @{bot_user_obj.username}"
        )

        try:
            await bot.send_photo(
                config.LOGGER_ID,
                photo=random.choice(LEFT_PHOTOS),
                caption=left_text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            try:
                await bot.send_message(config.LOGGER_ID, left_text, parse_mode=ParseMode.HTML)
            except Exception:
                pass

    except Exception as err_msg:
        print(f"[watcher] bot_left_watcher error: {err_msg}")
