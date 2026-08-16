import asyncio as a_sync
import os as sys_os

from pyrogram import filters as py_filters
from pyrogram.enums import ParseMode as p_mode
from pyrogram.types import Message as Py_Msg

from ShizuMusic import LOGGER as log_mod, bot as tg_bot, call_py as call_client
from ShizuMusic.core.queue import peek_current as get_curr_song
from ShizuMusic.modules.block import group_allowed as g_allow, user_allowed as u_allow
from ShizuMusic.utils.formatters import short as shorten_txt

# ❖ db helpers using utils.db ❖

def _db_save(chat_id: int) -> None:
    try:
        from ShizuMusic.utils.db import save_chat_effects as save_eff
        s = _get(chat_id)
        save_eff(chat_id, s["speed"], s["bass"], s["enabled"])
    except Exception as err_msg:
        log_mod.warning(f"❖ [effects] db save error: {err_msg} ❖")


def _db_load(chat_id: int) -> dict:
    try:
        from ShizuMusic.utils.db import load_chat_effects as load_eff
        return load_eff(chat_id)
    except Exception:
        return {"speed": 1.0, "bass": 0, "enabled": False}


# ❖ in-memory cache storage ❖
_cache_store: dict[int, dict] = {}

SPEED_DEFAULT = 1.0
BASS_DEFAULT  = 0


def _get(chat_id: int) -> dict:
    if chat_id not in _cache_store:
        _cache_store[chat_id] = _db_load(chat_id)
    return _cache_store[chat_id]


def get_effects(chat_id: int) -> dict:
    return _get(chat_id).copy()


def set_speed(chat_id: int, speed: float) -> None:
    _get(chat_id)["speed"] = speed
    _db_save(chat_id)


def set_bass(chat_id: int, bass: int) -> None:
    _get(chat_id)["bass"] = bass
    _db_save(chat_id)


def set_enabled(chat_id: int, val: bool) -> None:
    _get(chat_id)["enabled"] = val
    _db_save(chat_id)


def is_effects_on(chat_id: int) -> bool:
    return _get(chat_id).get("enabled", False)


def clear_effects(chat_id: int) -> None:
    _cache_store.pop(chat_id, None)
    try:
        from ShizuMusic.utils.db import delete_chat_effects as del_eff
        del_eff(chat_id)
    except Exception:
        pass


# ❖ ffmpeg filter constructor ❖

def _build_af(speed: float, bass: int) -> str | None:
    chunks = []

    if bass and bass > 0:
        chunks.append(f"equalizer=f=80:t=h:width=200:g={min(bass, 20)}")

    if speed and speed != 1.0:
        speed = round(max(0.25, min(speed, 4.0)), 2)
        if 0.5 <= speed <= 2.0:
            chunks.append(f"atempo={speed}")
        elif speed < 0.5:
            chunks.append("atempo=0.5,atempo=0.5")
        else:
            chain_list = []
            rem_val    = speed
            while rem_val > 2.0:
                chain_list.append("atempo=2.0")
                rem_val /= 2.0
            chain_list.append(f"atempo={round(rem_val, 2)}")
            chunks.append(",".join(chain_list))

    return ",".join(chunks) if chunks else None


# ❖ process file via ffmpeg utility ❖

async def _process_file(src: str, speed: float, bass: int) -> str:
    audio_f = _build_af(speed, bass)
    if not audio_f:
        return src

    sys_os.makedirs("downloads/effects", exist_ok=True)
    base_name = sys_os.path.splitext(sys_os.path.basename(src))[0]
    tag_name  = f"s{str(speed).replace('.', '')}_b{bass}"
    out_path  = f"downloads/effects/{base_name}_{tag_name}.mp3"

    if sys_os.path.exists(out_path) and sys_os.path.getsize(out_path) > 0:
        return out_path

    cmd_args = [
        "ffmpeg", "-y", "-i", src,
        "-af", audio_f,
        "-vn", "-acodec", "libmp3lame", "-b:a", "192k",
        out_path,
    ]
    proc_obj = await a_sync.create_subprocess_exec(
        *cmd_args,
        stdout=a_sync.subprocess.DEVNULL,
        stderr=a_sync.subprocess.DEVNULL,
    )
    await a_sync.wait_for(proc_obj.communicate(), timeout=120)

    if proc_obj.returncode != 0 or not sys_os.path.exists(out_path):
        raise Exception("ffmpeg audio processing failed")

    return out_path


# ❖ streaming helper utility ❖

async def _stream_from(chat_id: int, file_path: str, seek_sec: int = 0) -> None:
    from pytgcalls.types import AudioQuality, MediaStream

    ms_params = dict(
        audio_parameters=AudioQuality.HIGH,
        video_flags=MediaStream.Flags.IGNORE,
    )
    if seek_sec > 0:
        ms_params["ffmpeg_parameters"] = f"-ss {seek_sec}"

    try:
        await call_client.change_stream(chat_id, MediaStream(file_path, **ms_params))
    except Exception:
        await call_client.play(chat_id, MediaStream(file_path, **ms_params))


# ❖ apply active effects to current track ❖

async def apply_effects_now(chat_id: int, message: Py_Msg, *, seek_sec: int = -1) -> None:
    from ShizuMusic.utils.youtube import resolve_stream as res_stream
    from ShizuMusic.modules.seek import get_current_position as get_pos, set_seek_state as set_seek

    track = get_curr_song(chat_id)
    if not track:
        await message.reply("<b>❖ No music track is currently active. ❖</b>", parse_mode=p_mode.HTML)
        return

    st_data = _get(chat_id)
    speed_val = st_data["speed"]
    bass_val  = st_data["bass"]

    progress_msg = await message.reply("<b>❖ Applying effects, kindly hold on... ❖</b>", parse_mode=p_mode.HTML)

    try:
        src = await res_stream(track["url"])
    except Exception as err_ex:
        await progress_msg.edit_text(f"<b>❖ Stream lookup failed. ❖</b>\n<code>{err_ex}</code>", parse_mode=p_mode.HTML)
        return

    try:
        processed_file = await _process_file(src, speed_val, bass_val)
    except Exception as err_ex:
        await progress_msg.edit_text(f"<b>❖ ffmpeg execution error:</b> <code>{err_ex}</code>", parse_mode=p_mode.HTML)
        return

    current_pos = get_pos(chat_id) if seek_sec == -1 else seek_sec

    try:
        await _stream_from(chat_id, processed_file, seek_sec=current_pos)
    except Exception as err_ex:
        await progress_msg.edit_text(f"<b>❖ Audio stream playback failed:</b> <code>{err_ex}</code>", parse_mode=p_mode.HTML)
        return

    set_seek(chat_id, current_pos)

    spd_txt = f"{speed_val}x" if speed_val != 1.0 else "Normal (1.0x)"
    bss_txt = f"{bass_val} dB boost" if bass_val > 0 else "Off"
    pos_txt = f"{current_pos // 60}:{current_pos % 60:02d}"

    await progress_msg.edit_text(
        f"<b>❖ Effects Applied Successfully ✓ ❖</b>\n\n"
        f"<b>❖ Track Title :</b> {shorten_txt(track['title'])}\n"
        f"<b>❖ Timestamp   :</b> <code>{pos_txt}</code>\n"
        f"<b>❖ Speed Rate  :</b> <code>{spd_txt}</code>\n"
        f"<b>❖ Bass Level  :</b> <code>{bss_txt}</code>",
        parse_mode=p_mode.HTML,
    )


# ❖ auto-apply effects handler (invoked by player.py) ❖

async def maybe_apply_effects(chat_id: int, file_path: str) -> str:
    st_data = _get(chat_id)
    if not st_data.get("enabled", False):
        return file_path
    speed_val = st_data["speed"]
    bass_val  = st_data["bass"]
    if speed_val == 1.0 and bass_val == 0:
        return file_path
    try:
        return await _process_file(file_path, speed_val, bass_val)
    except Exception as err_ex:
        log_mod.warning(f"❖ [effects] automatic application failed for {chat_id}: {err_ex} ❖")
        return file_path


# ══════════════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS SECTION
# ══════════════════════════════════════════════════════════════════════════════

@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/speed(?:@\w+)?\s+(?P<val>[\d.]+)$")
    & g_allow & u_allow
)
async def speed_cmd(_, message: Py_Msg) -> None:
    chat_id = message.chat.id
    try:
        val = round(float(message.matches[0].group("val")), 2)
    except ValueError:
        await message.reply(
            "<b>❖ Incorrect numeric value. ❖</b>\n<b>❖ Example format :</b> <code>/speed 1.5</code>",
            parse_mode=p_mode.HTML,
        )
        return

    if not (0.25 <= val <= 4.0):
        await message.reply(
            "<b>❖ Playback speed must range between</b> <code>0.25</code> <b>and</b> <code>4.0</code>",
            parse_mode=p_mode.HTML,
        )
        return

    set_speed(chat_id, val)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/speedreset(?:@\w+)?$")
    & g_allow & u_allow
)
async def speedreset_cmd(_, message: Py_Msg) -> None:
    chat_id = message.chat.id
    set_speed(chat_id, SPEED_DEFAULT)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/bass(?:@\w+)?\s+(?P<val>\d+)$")
    & g_allow & u_allow
)
async def bass_cmd(_, message: Py_Msg) -> None:
    chat_id = message.chat.id
    try:
        val = int(message.matches[0].group("val"))
    except ValueError:
        await message.reply(
            "<b>❖ Incorrect bass value. ❖</b>\n<b>❖ Example format :</b> <code>/bass 10</code>",
            parse_mode=p_mode.HTML,
        )
        return

    if not (1 <= val <= 20):
        await message.reply(
            "<b>❖ Bass level must range between</b> <code>1</code> <b>and</b> <code>20</code>",
            parse_mode=p_mode.HTML,
        )
        return

    set_bass(chat_id, val)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/bassoff(?:@\w+)?$")
    & g_allow & u_allow
)
async def bassoff_cmd(_, message: Py_Msg) -> None:
    chat_id = message.chat.id
    set_bass(chat_id, BASS_DEFAULT)
    try:
        await message.delete()
    except Exception:
        pass
    await apply_effects_now(chat_id, message)


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/effecton(?:@\w+)?$")
    & g_allow & u_allow
)
async def effecton_cmd(_, message: Py_Msg) -> None:
    chat_id = message.chat.id
    set_enabled(chat_id, True)
    st_data   = _get(chat_id)
    spd_txt   = f"{st_data['speed']}x" if st_data['speed'] != 1.0 else "Normal (1.0x)"
    bss_txt   = f"{st_data['bass']} dB" if st_data['bass'] > 0 else "Off"
    await message.reply(
        "<b>❖ Audio Effects Activated ✓ ❖</b>\n\n"
        "<b>❖ Every track in this group will now playback with filters. ❖</b>\n\n"
        f"<b>❖ Speed Rate :</b> <code>{spd_txt}</code>\n"
        f"<b>❖ Bass Gain  :</b> <code>{bss_txt}</code>\n\n"
        "<i>Type /effectoff to deactivate. Configuration persists across reboots.</i>",
        parse_mode=p_mode.HTML,
    )


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/effectoff(?:@\w+)?$")
    & g_allow & u_allow
)
async def effectoff_cmd(_, message: Py_Msg) -> None:
    set_enabled(message.chat.id, False)
    await message.reply(
        "<b>❖ Audio Effects Deactivated ✓ ❖</b>\n\n"
        "<b>❖ Tracks will now playback in their original state. ❖</b>\n\n"
        "<i>Speed & bass configurations are retained — type /effecton to reactivate.</i>",
        parse_mode=p_mode.HTML,
    )


@tg_bot.on_message(
    py_filters.group
    & py_filters.regex(r"^/effects(?:@\w+)?$")
    & g_allow & u_allow
)
async def effects_status_cmd(_, message: Py_Msg) -> None:
    chat_id   = message.chat.id
    st_data   = _get(chat_id)
    speed_val = st_data["speed"]
    bass_val  = st_data["bass"]
    is_active = st_data["enabled"]

    spd_txt   = f"{speed_val}x" if speed_val != 1.0 else "Normal (1.0x)"
    bss_txt   = f"{bass_val} dB boost" if bass_val > 0 else "Off"
    mode_txt  = "ENABLED — All tracks modified 🟢" if is_active else "DISABLED — Custom per track 🔴"

    track_obj = get_curr_song(chat_id)
    trk_txt   = shorten_txt(track_obj["title"]) if track_obj else "No playback active"

    await message.reply(
        f"<b>❖ Effects Panel Status — {message.chat.title} ❖</b>\n\n"
        f"<b>❖ Active Track :</b> {trk_txt}\n"
        f"<b>❖ Mode State   :</b> <code>{mode_txt}</code>\n"
        f"<b>❖ Speed Multi  :</b> <code>{spd_txt}</code>\n"
        f"<b>❖ Bass Boost   :</b> <code>{bss_txt}</code>\n\n"
        "<b>❖ Commands Reference :</b>\n"
        "<code>/speed 1.5</code>     → update speed (0.25–4.0)\n"
        "<code>/speedreset</code>     → restore standard speed\n"
        "<code>/bass 10</code>        → apply bass level (1–20 dB)\n",
        parse_mode=p_mode.HTML,
    )
