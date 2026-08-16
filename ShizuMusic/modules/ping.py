import asyncio as a_sync
import time as tm
from datetime import timedelta as time_delta

import psutil as ps_util
from pyrogram import filters as py_filters
from pyrogram.enums import ParseMode as p_mode
from pyrogram.types import InlineKeyboardButton as Btn, InlineKeyboardMarkup as Markup, Message as Py_Msg

import config as cfg
from ShizuMusic import bot as tg_bot, assistant as tg_ast, bot_start_time as start_epoch


def supp_markup():
    return Markup([[
        Btn(text="❖ sᴜᴘᴘᴏʀᴛ ❖", url=cfg.SUPPORT_GROUP),
    ]])


# ❖ /ping command handler ❖

@tg_bot.on_message(py_filters.command("ping") & py_filters.user(cfg.OWNER_ID) if hasattr(cfg, 'OWNER_ID') else py_filters.command("ping"))
async def ping_cmd(client, message: Py_Msg) -> None:
    t_start = tm.perf_counter()
    status_msg = await message.reply_text(
        f"<b>❖ {client.me.first_name} ɪs ᴄʜᴇᴄᴋɪɴɢ ᴘɪɴɢ... ❖</b>",
        parse_mode=p_mode.HTML,
    )
    
    latency_ms = round((tm.perf_counter() - t_start) * 1000)
    uptime_str = str(time_delta(seconds=int(tm.time() - start_epoch)))
    cpu_usage  = ps_util.cpu_percent(interval=1)

    proc_ref   = ps_util.Process()
    ram_usage  = proc_ref.memory_info().rss / 1024 / 1024

    try:
        ast_start = tm.perf_counter()
        await tg_ast.get_me()
        pytg_ms = round((tm.perf_counter() - ast_start) * 1000)
    except Exception:
        pytg_ms = "N/A"

    await status_msg.delete()

    resp_caption = (
        f"<b>❖ ᴘᴏɴɢ : <code>{latency_ms}ms</code> ❖</b>\n\n"
        f"<b><u>❖ {client.me.first_name} sʏsᴛᴇᴍ ᴍᴇᴛʀɪᴄs : ❖</u></b>\n\n"
        f"<b>❖ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime_str}</code>\n"
        f"<b>❖ ʀᴀᴍ    :</b> <code>{ram_usage:.2f} mb</code>\n"
        f"<b>❖ cᴘᴜ    :</b> <code>{cpu_usage}%</code>\n"
        f"<b>❖ ᴘʏᴛɢᴄ  :</b> <code>{pytg_ms}ms</code>\n\n"
        f"<b>● ᴍᴀɴᴀɢᴇᴅ ʙʏ » <a href=\"{cfg.SUPPORT_GROUP}\">Eʟʏx Mᴜsɪᴄ</a> ❖</b>"
    )

    await message.reply_photo(
        photo=cfg.PING_IMG_URL,
        caption=resp_caption,
        parse_mode=p_mode.HTML,
        reply_markup=supp_markup(),
    )
