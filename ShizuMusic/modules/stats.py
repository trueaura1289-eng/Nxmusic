import platform
import sys

import psutil
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot
from ShizuMusic.utils.db import (
    get_mongo_client,
    get_served_chats_count,
    get_served_users_count,
    get_banned_chats_count,
    get_total_plays,
    get_broadcast_count,
    is_connected,
)


@bot.on_message(
    filters.command("stats")
    & filters.user(config.OWNER_ID)
)
async def stats_cmd(_, message: Message) -> None:
    """Full system + MongoDB stats for the bot owner."""

    processing = await message.reply(
        "<b>❖ ɢᴀᴛʜᴇʀɪɴɢ sᴛᴀᴛs, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>",
        parse_mode=ParseMode.HTML,
    )

    # ── System stats ──────────────────────────────────────────────────────────
    try:
        cpu_percent  = psutil.cpu_percent(interval=1)
        cpu_freq     = psutil.cpu_freq()
        freq_str     = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        p_cores      = psutil.cpu_count(logical=False) or "N/A"
        t_cores      = psutil.cpu_count(logical=True)  or "N/A"

        ram          = psutil.virtual_memory()
        ram_total    = ram.total     / (1024 ** 3)
        ram_used     = ram.used      / (1024 ** 3)
        ram_free     = ram.available / (1024 ** 3)
        ram_percent  = ram.percent

        hdd          = psutil.disk_usage("/")
        disk_total   = hdd.total / (1024 ** 3)
        disk_used    = hdd.used  / (1024 ** 3)
        disk_free    = hdd.free  / (1024 ** 3)
        disk_percent = hdd.percent

        py_version   = sys.version.split()[0]
        os_name      = platform.system()
        os_release   = platform.release()

    except Exception as e:
        await processing.edit_text(
            f"<b>❖ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ sʏsᴛᴇᴍ sᴛᴀᴛs:</b> <code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # ── MongoDB stats ─────────────────────────────────────────────────────────
    db_line = "<b>❖ MongoDB :</b> <code>Not connected</code>"
    if is_connected():
        try:
            client   = get_mongo_client()
            db_stats = client["ShizuMusic"].command("dbstats")
            data_kb  = db_stats.get("dataSize",    0) / 1024
            stor_kb  = db_stats.get("storageSize", 0) / 1024
            col_cnt  = db_stats.get("collections", 0)
            obj_cnt  = db_stats.get("objects",     0)
            db_line  = (
                f"<b>⚘ DB Data    :</b> <code>{data_kb:.2f} KB</code>\n"
                f"<b>⚘ DB Storage :</b> <code>{stor_kb:.2f} KB</code>\n"
                f"<b>⚘ Collections:</b> <code>{col_cnt}</code>\n"
                f"<b>⚘ Objects    :</b> <code>{obj_cnt}</code>"
            )
        except Exception as e:
            db_line = f"<b>⚘ MongoDB stats error:</b> <code>{e}</code>"

    # ── Bot DB counts ─────────────────────────────────────────────────────────
    served_chats = get_served_chats_count()
    served_users = get_served_users_count()
    banned_chats = get_banned_chats_count()
    total_plays  = get_total_plays()
    bc           = get_broadcast_count()

    # ── Final message ─────────────────────────────────────────────────────────
    text = (
        "<b>~~ ᴇʟʏx ᴍᴜsɪᴄ sᴛᴀᴛs --</b>\n\n"

      "<b>❖ sʏsᴛᴇᴍ ᴅᴇᴛᴀɪʟs</b>\n"
f"<b> ᴏs       :</b> <code>{os_name} {os_release}</code>\n"
f"<b> ᴘʏᴛʜᴏɴ   :</b> <code>{py_version}</code>\n"
f"<b> ᴄᴘᴜ      :</b> <code>{cpu_percent}%</code>\n"
f"<b> ᴄᴘᴜ ғʀᴇǫ :</b> <code>{freq_str}</code>\n"
f"<b> ᴘ-ᴄᴏʀᴇs  :</b> <code>{p_cores}</code>\n"
f"<b> ᴛ-ᴄᴏʀᴇs  :</b> <code>{t_cores}</code>\n\n"

"<b>❖ ᴍᴇᴍᴏʀʏ</b>\n"
f"<b> ᴛᴏᴛᴀʟ :</b> <code>{ram_total:.2f} ɢʙ</code>\n"
f"<b> ᴜsᴇᴅ  :</b> <code>{ram_used:.2f} ɢʙ ({ram_percent}%)</code>\n"
f"<b> ғʀᴇᴇ  :</b> <code>{ram_free:.2f} ɢʙ</code>\n\n"

"<b>❖ sᴛᴏʀᴀɢᴇ</b>\n"
f"<b> ᴛᴏᴛᴀʟ :</b> <code>{disk_total:.2f} ɢʙ</code>\n"
f"<b> ᴜsᴇᴅ  :</b> <code>{disk_used:.2f} ɢʙ ({disk_percent}%)</code>\n"
f"<b> ғʀᴇᴇ  :</b> <code>{disk_free:.2f} ɢʙ</code>\n\n"

"<b>❖ ᴅᴀᴛᴀʙᴀsᴇ</b>\n"
f"{db_line}\n\n"

"<b>❖ ʙᴏᴛ ɪɴsɪɢʜᴛs</b>\n"
f"<b> ᴄʜᴀᴛs     :</b> <code>{served_chats}</code>\n"
f"<b> ᴜsᴇʀs     :</b> <code>{served_users}</code>\n"
f"<b> ʙʟᴏᴄᴋᴇᴅ   :</b> <code>{banned_chats}</code>\n"
f"<b> ᴘʟᴀʏs     :</b> <code>{total_plays}</code>\n\n"

"<b>❖ ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴀᴛᴀ</b>\n"
f"<b> ᴛᴏᴛᴀʟ     :</b> <code>{bc['total']}</code>\n"
f"<b> ɢʀᴏᴜᴘs    :</b> <code>{bc['groups']}</code>\n"
f"<b> ᴘʀɪᴠᴀᴛᴇ   :</b> <code>{bc['private']}</code>\n\n"

"<b>❖ ────────────────────────────────</b>"
        
        it_text(text, parse_mode=ParseMode.HTML)
