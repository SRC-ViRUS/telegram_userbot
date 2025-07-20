import os
from telethon import events
from utils import send_media_safe
from modules.mute import muted_private, muted_groups


def register(client):
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming(event):
        if (event.is_private and event.sender_id in muted_private) or (
            event.chat_id in muted_groups
            and event.sender_id in muted_groups[event.chat_id]
        ):
            return await event.delete()
        if (
            event.is_private
            and event.media
            and getattr(event.media, "ttl_seconds", None)
        ):
            try:
                p = await event.download_media("downloads/")
                await send_media_safe(client, "me", p, caption="📸 تم حفظ البصمة.")
                os.remove(p)
            except Exception:
                pass
