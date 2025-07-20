# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import API_ID, API_HASH, SESSION_STRING, DOWNLOADS_DIR
from modules import (
    bio_rotator,
    command_handler,
    commands,
    forwarding,
    imitate,
    media,
    mentions,
    misc,
    mute,
    reactions,
    sleep,
    welcome,
)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


async def main():
    print("تشغيل البوت…")
    await client.start()
    print("✅ البوت يعمل الآن.")

    # Register all modules
    bio_rotator.register(client)
    commands.register(client)
    forwarding.register(client)
    imitate.register(client)
    media.register(client)
    mentions.register(client)
    misc.register(client)
    mute.register(client)
    reactions.register(client)
    sleep.register(client)
    welcome.register(client)

    # Register the command handler
    command_handler.register(client)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
