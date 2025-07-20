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
