import asyncio

from pyrogram.enums import ParseMode
from pytgcalls import filters as fl
from ntgcalls import TelegramServerError
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import (
    ChatUpdate,
    StreamEnded,
)

from ShizuMusic import LOGGER, bot, call_py
from ShizuMusic.core.queue import clear_queue, peek_current, pop_current, queue_size
from ShizuMusic.utils.helpers import delete_file


async def leave_vc(chat_id: int) -> None:
    """
    Leave voice chat and clean queue + autoplay state.
    """

    # Stop autoplay when leaving VC
    try:
        from ShizuMusic.core.autoplay import stop_autoplay
        stop_autoplay(chat_id)
    except Exception:
        pass

    # Delete queued files
    for song in clear_queue(chat_id):
        try:
            delete_file(song.get("file_path", ""))
        except Exception:
            pass

    try:
        await call_py.leave_call(chat_id)

    except NoActiveGroupCall:
        pass

    except TelegramServerError as e:
        LOGGER.error(f"Leave VC TelegramServerError: {e}")

    except Exception as e:
        LOGGER.error(f"Leave VC Error: {e}")


@call_py.on_update(fl.stream_end())
async def on_stream_end(_: object, update: StreamEnded) -> None:
    """
    Automatically play the next song when the current stream ends.
    AutoPlay mode also refetches songs when queue becomes low.
    """

    chat_id = update.chat_id

    # Remove finished song safely
    done = pop_current(chat_id)

    if done:
        await asyncio.sleep(1)

        try:
            delete_file(done.get("file_path", ""))

        except Exception:
            pass

    # ── AutoPlay Refetch Check ────────────────────────────────────────────────
    try:
        from ShizuMusic.core.autoplay import is_autoplay, maybe_refetch

        if is_autoplay(chat_id):
            # Sirf tabhi fetch karein jab queue mein actually gaane bache hon ya threshold cross ho
            if queue_size(chat_id) <= 2:
                asyncio.create_task(
                    maybe_refetch(chat_id, "Aᴜᴛᴏᴘʟᴀʏ 🔁", 0)
                )

    except Exception as ap_err:
        LOGGER.warning(f"[AutoPlay] Refetch Check Error: {ap_err}")

    # ── Next Song ─────────────────────────────────────────────────────────────
    # Wait a little so autoplay fetch can complete
    await asyncio.sleep(2)

    nxt = peek_current(chat_id)

    # Play next song
    if nxt:

        from ShizuMusic.core.player import play_song

        try:
            msg = await bot.send_message(
                chat_id,
                f"<b>❖ Nᴇxᴛ Tʀᴀᴄᴋ :</b>\n"
                f"<b>❖ Tɪᴛʟᴇ :</b> <code>{nxt['title']}</code>",
                parse_mode=ParseMode.HTML,
            )

            await play_song(chat_id, msg, nxt)

        except (NoActiveGroupCall, TelegramServerError) as e:
            LOGGER.error(f"Next Song VC Error: {e}")

        except Exception as e:
            LOGGER.error(f"Next Song Error: {e}")

            try:
                await bot.send_message(
                    chat_id,
                    f"<b>❖ Eʀʀᴏʀ :</b> <code>{e}</code>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

    else:

        # Queue finished but autoplay may still fetch songs
        try:
            from ShizuMusic.core.autoplay import (
                is_autoplay,
                _autoplay_fetching,
            )

            if is_autoplay(chat_id):

                # Wait if background fetching is running (up to 10 seconds max to avoid infinite locks)
                for _ in range(10):
                    if _autoplay_fetching.get(chat_id):
                        await asyncio.sleep(1)
                    else:
                        break

                # Give one more second after fetching finishes
                await asyncio.sleep(1)

                nxt2 = peek_current(chat_id)

                # Play fetched song
                if nxt2:

                    from ShizuMusic.core.player import play_song

                    msg2 = await bot.send_message(
                        chat_id,
                        f"<b>❖ Nᴇxᴛ Tʀᴀᴄᴋ :</b> "
                        f"<code>{nxt2['title']}</code>",
                        parse_mode=ParseMode.HTML,
                    )

                    await play_song(chat_id, msg2, nxt2)
                    return

        except Exception:
            pass

        # Check if queue is really empty before leaving VC
        if queue_size(chat_id) == 0:
            # Queue completely finished
            await leave_vc(chat_id)

            try:
                await bot.send_message(
                    chat_id,
                    "<b>❖ Tʜᴇ ǫᴜᴇᴜᴇ ʜᴀs ᴇɴᴅᴇᴅ</b>\n"
                    "<b>❖ Assɪsᴛᴀɴᴛ ʟᴇғᴛ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀT.</b>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass
