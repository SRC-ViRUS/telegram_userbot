from telethon import events
from utils import is_owner, qedit, send_media_safe

imitate_targets, last_imitated = set(), {}


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
    async def cmd_imitate_on(event):
        if not await is_owner(client, event):
            return
        r = await event.get_reply_message()
        imitate_targets.add(r.sender_id)
        last_imitated.pop(r.sender_id, None)
        await qedit(event, f"✅ تفعيل التقليد لـ {r.sender_id}")

    @client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
    async def cmd_imitate_off(event):
        if not await is_owner(client, event):
            return
        imitate_targets.clear()
        last_imitated.clear()
        await qedit(event, "🛑 تم إيقاف التقليد.")

    @client.on(events.NewMessage(incoming=True))
    async def imitate(event):
        uid = event.sender_id
        if uid not in imitate_targets or last_imitated.get(uid) == event.id:
            return
        last_imitated[uid] = event.id
        if event.is_group:
            me = await client.get_me()
            if not (
                (
                    event.is_reply
                    and (await event.get_reply_message()).sender_id == me.id
                )
                or f"@{me.username}" in (event.raw_text or "")
            ):
                return
        try:
            if event.text:
                await client.send_message(
                    event.chat_id if event.is_group else uid, event.text
                )
            if event.media:
                ttl = getattr(event.media, "ttl_seconds", None)
                await send_media_safe(
                    client,
                    event.chat_id if event.is_group else uid,
                    event.media,
                    event.text or None,
                    ttl=ttl,
                )
        except Exception as e:
            print("خطأ تقليد:", e)
