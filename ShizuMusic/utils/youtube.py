import asyncio
import logging
import os
import re
from typing import Union

import aiofiles
import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from ShizuMusic.utils.formatters import sec_to_iso

logger = logging.getLogger(__name__)

# ── API config ────────────────────────────────────────────────────────────────
SHRUTI_API_URL        = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
SHRUTI_API_KEY        = os.environ.get("SHRUTI_API_KEY", "ShrutiBots3VDrKhl4lK6T6ihA1WgL")  # Get from @SHRUTIAPIBOT on Telegram
DOWNLOAD_DIR          = "downloads"
SHRUTI_TOKEN_TIMEOUT  = 10    # seconds — fetch download token
SHRUTI_STREAM_TIMEOUT = 900   # 15 min  — stream long songs

_file_cache: dict[str, str] = {}


# ═════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def _extract_video_id(url: str) -> str:
    """Extract raw video ID from any YouTube URL format."""
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return url


def _cleanup(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def time_to_seconds(time) -> int:
    """Convert M:SS or H:MM:SS string to total seconds."""
    try:
        stringt = str(time)
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))
    except Exception:
        return 0


# ═════════════════════════════════════════════════════════════════════════════
# DOWNLOAD HELPERS (New API — single-step direct stream)
# ═════════════════════════════════════════════════════════════════════════════

async def download_song(link: str) -> str:
    """Download audio via Shruti API. Returns local file path or None on failure."""
    video_id = _extract_video_id(link)
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

    # Disk cache
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SHRUTI_API_URL}/download",
                params={"url": video_id, "type": "audio", "api_key": SHRUTI_API_KEY},
                timeout=aiohttp.ClientTimeout(total=SHRUTI_STREAM_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"[shruti] Audio download failed: HTTP {resp.status}")
                    return None
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        await f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None

    except Exception as e:
        logger.error(f"[shruti] download_song error: {e}")
        _cleanup(file_path)
        return None


async def download_video(link: str) -> str:
    """Download video via Shruti API. Returns local file path or None on failure."""
    video_id = _extract_video_id(link)
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    # Disk cache
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SHRUTI_API_URL}/download",
                params={"url": video_id, "type": "video", "api_key": SHRUTI_API_KEY},
                timeout=aiohttp.ClientTimeout(total=SHRUTI_STREAM_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"[shruti] Video download failed: HTTP {resp.status}")
                    return None
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        await f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None

    except Exception as e:
        logger.error(f"[shruti] download_video error: {e}")
        _cleanup(file_path)
        return None


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC — STREAM RESOLVER (backward-compatible)
# ═════════════════════════════════════════════════════════════════════════════

async def resolve_stream(url: str) -> str:
    """Resolve a YouTube URL or video ID to a local audio file path."""
    if os.path.exists(url) and os.path.isfile(url):
        return url

    if url in _file_cache and os.path.exists(_file_cache[url]):
        logger.info("[shruti] Cache hit")
        return _file_cache[url]

    video_id  = _extract_video_id(url)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        _file_cache[url] = file_path
        return file_path

    logger.info(f"[shruti] Downloading: {video_id}")
    downloaded = await download_song(url)
    if downloaded:
        _file_cache[url] = downloaded
        logger.info(f"[shruti] Done — {os.path.getsize(downloaded) // 1024} KB")
        return downloaded

    raise Exception("Shruti API download failed. Please try again.")


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC — YOUTUBE SEARCH / METADATA (Safe yt-dlp implementation)
# ═════════════════════════════════════════════════════════════════════════════

async def search_yt(query: str):
    """Search YouTube for a video or playlist using yt-dlp."""
    loop = asyncio.get_event_loop()

    def _extract():
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if "playlist?list=" in query or "&list=" in query:
                return ydl.extract_info(query, download=False), "playlist"
            else:
                ydl_opts['default_search'] = 'ytsearch1'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_search:
                    return ydl_search.extract_info(query, download=False), "single"

    try:
        data, type_res = await loop.run_in_executor(None, _extract)
        
        if type_res == "playlist":
            vids = data.get("entries") or []
            if not vids:
                raise Exception("ᴩʟᴀʏʟɪsᴛ ɪs ᴇᴍᴩᴛʏ")
            items = []
            for v in vids:
                secs = v.get("duration", 0) or 0
                items.append({
                    "link": f"https://www.youtube.com/watch?v={v.get('id')}",
                    "title": v.get("title", "Unknown"),
                    "duration": sec_to_iso(int(secs)),
                    "thumbnail": v.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
                })
            return {"playlist": items}
        
        else:
            if 'entries' in data:
                data = data['entries'][0]
            
            url = data.get("webpage_url") or f"https://www.youtube.com/watch?v={data.get('id')}"
            title = data.get("title", "Unknown")
            secs = data.get("duration", 0) or 0
            thumb = data.get("thumbnail", "")
            if not thumb and 'thumbnails' in data and data['thumbnails']:
                thumb = data['thumbnails'][-1].get('url', '')

            return (url, title, sec_to_iso(int(secs)), thumb.split("?")[0])

    except Exception as e:
        logger.error(f"[yt-dlp search error]: {e}")
        raise Exception("ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ")


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC — YouTubeAPI CLASS (Full featured with original methods preserved)
# ═════════════════════════════════════════════════════════════════════════════

class YouTubeAPI:
    def __init__(self):
        self.base      = "https://www.youtube.com/watch?v="
        self.regex     = r"(?:youtube\.com|youtu\.be)"
        self.status    = "https://www.youtube.com/oembed?url="
        self.listbase  = "https://youtube.com/playlist?list="
        self.reg       = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_link(self, link: str, videoid) -> str:
        return (self.base + link) if videoid else link

    def _strip_extra(self, link: str) -> str:
        return link.split("&")[0] if "&" in link else link

    # ── Public methods ────────────────────────────────────────────────────────

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        link = self._strip_extra(self._build_link(link, videoid))
        res = await search_yt(link)
        if isinstance(res, tuple):
            url, title, duration_min, thumbnail = res
            vidid = _extract_video_id(url)
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        raise Exception("Details failed")

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        res = await self.details(link, videoid)
        return res[0]

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        res = await self.details(link, videoid)
        return res[1]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        res = await self.details(link, videoid)
        return res[3]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        link = self._strip_extra(self._build_link(link, videoid))
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(
        self, link: str, limit: int, user_id, videoid: Union[bool, str] = None
    ) -> list:
        if videoid:
            link = self.listbase + link
        link = self._strip_extra(link)
        loop = asyncio.get_event_loop()
        
        def _get_pl():
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(link, download=False)

        try:
            plist = await loop.run_in_executor(None, _get_pl)
            videos = plist.get("entries") or []
            ids = []
            for data in videos[:limit]:
                if not data:
                    continue
                vid = data.get("id")
                if not vid:
                    continue
                ids.append(vid)
            return ids
        except Exception:
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        link = self._strip_extra(self._build_link(link, videoid))
        title, duration_min, duration_sec, thumbnail, vidid = await self.details(link)
        yturl = f"https://www.youtube.com/watch?v={vidid}"
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        link = self._strip_extra(self._build_link(link, videoid))
        loop = asyncio.get_event_loop()
        def _get_fmt():
            ytdl_opts = {"quiet": True}
            ydl = yt_dlp.YoutubeDL(ytdl_opts)
            with ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for fmt in r.get("formats", []):
                    try:
                        if "dash" not in str(fmt.get("format", "")).lower():
                            formats_available.append(
                                {
                                    "format": fmt.get("format"),
                                    "filesize": fmt.get("filesize"),
                                    "format_id": fmt.get("format_id"),
                                    "ext": fmt.get("ext"),
                                    "format_note": fmt.get("format_note"),
                                    "yturl": link,
                                }
                            )
                    except Exception:
                        continue
                return formats_available, link
        return await loop.run_in_executor(None, _get_fmt)

    async def slider(
        self, link: str, query_type: int, videoid: Union[bool, str] = None
    ):
        link = self._strip_extra(self._build_link(link, videoid))
        loop = asyncio.get_event_loop()
        def _get_slider():
            ydl_opts = {'default_search': f'ytsearch{query_type + 1}', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                r = ydl.extract_info(link, download=False)
                entries = r.get('entries', [])
                if len(entries) > query_type:
                    item = entries[query_type]
                    return (
                        item.get("title"),
                        sec_to_iso(int(item.get("duration", 0))),
                        item.get("thumbnail", "").split("?")[0],
                        item.get("id")
                    )
                raise Exception("Slider out of range")
        return await loop.run_in_executor(None, _get_slider)

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file:
                return downloaded_file, True
            return None, False
        except Exception:
            return None, False
