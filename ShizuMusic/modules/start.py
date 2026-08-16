import asyncio
import random

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot
from config import START_ANIMATIONS
from ShizuMusic.modules.block import user_allowed
from ShizuMusic.utils.db import add_broadcast_chat, add_served_chat, add_served_user

# ── Message effect IDs (Telegram premium effects) ─────────────────────────────
EFFECT_ID = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

# ── /start ────────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("start") & user_allowed)
async def start_handler(_, message: Message) -> None:

    uid       = message.from_user.id
    name      = message.from_user.first_name or "User"
    chat_id   = message.chat.id
    chat_type = message.chat.type
    animation = random.choice(START_ANIMATIONS)

    # ── Delete the user's /start command message ──────────────────────────────
    try:
        await message.delete()
    except Exception:
        pass

    try:
        add_served_user(uid)
        add_served_chat(chat_id)
    except Exception:
        pass

# ── Private ───────────────────────────────────────────────────────────────
    if chat_type == ChatType.PRIVATE:
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
    
    sent = await message.reply_animation(
        animation,
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
        message_effect_id=random.choice(EFFECT_ID),
    )
        try:
            add_broadcast_chat(chat_id, "private")
        except Exception:
            pass

        if config.LOGGER_ID:
            try:
                await bot.send_message(
                    config.LOGGER_ID,
                    "<b>#ɴᴇᴡᴜsᴇʀ sᴛᴀʀᴛᴇᴅ</b>\n\n"
                    f"<b>❖ Nᴀᴍᴇ     :</b> <a href='tg://user?id={uid}'>{name}</a>\n"
                    f"<b>❖ Iᴅ       :</b> <code>{uid}</code>\n"
                    f"<b>❖ Usᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username or 'N/A'}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

    # ── Group ─────────────────────────────────────────────────────────────────
   else:
    chat_title = message.chat.title or "ᴛʜɪs ᴄʜᴀᴛ"
    caption = (
        f"<b>✦ ʜᴇʏ</b> <a href='tg://user?id={uid}'>{name}</a> 👋\n\n"
        f"<b>╰┈➤ ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ {config.BOT_NAME} ᴛᴏ "
        f"{chat_title}.</b>\n\n"
        "<b>❖ ɪ'ᴍ ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ ᴍᴜsɪᴄ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.</b>\n"
        "<b>❖ ᴜsᴇ ᴛʜᴇ ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ.</b>"
    )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴀᴅᴅ мᴇ",
                                     url=f"{config.BOT_LINK}?startgroup=true"),
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=config.UPDATES_CHANNEL),
            ],
            [InlineKeyboardButton("ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs",
                                  callback_data="show_help")],
        ])

        sent = await message.reply_animation(
            animation,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )

       admin_msg = (
    "<b>✦ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ɪs ʀᴇᴀᴅʏ 🎧</b>\n\n"
    "<b>❖ ᴏɴᴇ ʟᴀsᴛ sᴛᴇᴘ : ᴘʟᴇᴀsᴇ ɢʀᴀɴᴛ ᴍᴇ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss.</b>\n\n"
    "<b>ᴛʜɪs ᴀʟʟᴏᴡs ᴍᴇ ᴛᴏ :</b>\n"
    "<b>• ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs</b>\n"
    "<b>• ᴄᴏɴᴛʀᴏʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs</b>\n"
    "<b>• ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴘᴇʀᴍɪssɪᴏɴ</b>\n\n"
    "<b>❖ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs, ᴠᴏɪᴄᴇ ᴘʟᴀʏʙᴀᴄᴋ ᴍᴀʏ ɴᴏᴛ ᴡᴏʀᴋ ᴘʀᴏᴘᴇʀʟʏ.</b>"
)

admin_kb = InlineKeyboardMarkup([[
    InlineKeyboardButton(
        "➕ ɢʀᴀɴᴛ ᴀᴅᴍɪɴ ᴀᴄᴄᴇss",
        url=f"tg://user?id={(await bot.get_me()).id}",
    )
]])
        try:
            admin_sent = await message.reply_text(
                admin_msg,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_kb,
            )
        except Exception:
            pass

        try:
            add_broadcast_chat(chat_id, "group")
        except Exception:
            pass


# ── /help ─────────────────────────────────────────────────────────────────────

@bot.on_message(filters.command("help") & user_allowed)
async def help_handler(_, message: Message) -> None:

    uid  = message.from_user.id
    name = message.from_user.first_name or "User"

    # ── Delete the user's /help command message ───────────────────────────────
    try:
        await message.delete()
    except Exception:
        pass

   kb = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴘʟᴀʏ",    callback_data="help_play"),
        InlineKeyboardButton("ᴀ-ᴘʟᴀʏ",  callback_data="help_autoplay"),
        InlineKeyboardButton("sᴘᴇᴇᴅ",   callback_data="help_speed"),
    ],
    [
        InlineKeyboardButton("ᴀᴅᴍɪɴ",   callback_data="help_admin"),
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
    animation = random.choice(START_ANIMATIONS)

    sent = await message.reply_animation(
        animation,
       caption = (
    f"<b>✦ ʜᴇʏ</b> <a href='tg://user?id={uid}'>{name}</a> 👋\n\n"
    "<b>❖ sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ :</b>"
),
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )
