import asyncio
import datetime
import os
import tempfile
from telethon import TelegramClient, events, functions, types, utils
from telethon.errors import FileReferenceExpiredError
from functools import lru_cache


@lru_cache(maxsize=1)
async def get_me(client):
    """
    Get the current user's information and cache it.
    """
    return await client.get_me()


async def is_owner(client, event):
    """
    Check if the sender of an event is the owner of the bot.
    """
    me = await get_me(client)
    return event.sender_id == me.id


async def qedit(event, txt, delay=2):
    """
    Edit a message and delete it after a delay.
    """
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()


async def send_media_safe(client, dest, media, caption=None, ttl=None):
    """
    Send media safely, handling FileReferenceExpiredError.
    """
    try:
        await client.send_file(dest, media, caption=caption, ttl=ttl)
    except FileReferenceExpiredError:
        tmp = await client.download_media(media, file=tempfile.mktemp())
        await client.send_file(dest, tmp, caption=caption, ttl=ttl)
        os.remove(tmp)


async def delete_after(msg, seconds):
    """
    Delete a message after a specified number of seconds.
    """
    await asyncio.sleep(seconds)
    try:
        await msg.delete()
    except:
        pass


_dialogs_cache = {"time": None, "counts": (0, 0)}


async def get_dialog_counts(client, refresh=False):
    """Return the number of groups and channels for the current account.

    Results are cached for an hour unless ``refresh`` is True.
    """
    now = datetime.datetime.utcnow()
    if (
        not refresh
        and _dialogs_cache["time"]
        and (now - _dialogs_cache["time"]).total_seconds() < 3600
    ):
        return _dialogs_cache["counts"]

    dialogs = await client.get_dialogs()
    groups = channels = 0
    for d in dialogs:
        if d.is_channel:
            if getattr(d.entity, "broadcast", False):
                channels += 1
            else:
                groups += 1

    _dialogs_cache["time"] = now
    _dialogs_cache["counts"] = (groups, channels)
    return groups, channels


def estimate_creation_date(user_id: int) -> datetime.datetime:
    """Roughly estimate the account creation date based on the ID."""
    base_date = datetime.datetime(2015, 1, 1)
    months = user_id // 50_000_000
    return base_date + datetime.timedelta(days=int(months * 30.44))
