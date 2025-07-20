from telethon import events
from utils import is_owner, qedit

muted_private, muted_groups = set(), {}


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
    async def cmd_mute(event):
        if not await is_owner(client, event):
            return
        r = await event.get_reply_message()
        (
            muted_private
            if event.is_private
            else muted_groups.setdefault(event.chat_id, set())
        ).add(r.sender_id)
        await qedit(event, "🔇 تم كتمه.")

    @client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
    async def cmd_unmute(event):
        if not await is_owner(client, event):
            return
        r = await event.get_reply_message()
        (
            muted_private
            if event.is_private
            else muted_groups.get(event.chat_id, set())
        ).discard(r.sender_id)
        await qedit(event, "🔊 تم فك الكتم.")

    @client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
    async def cmd_mlist(event):
        if not await is_owner(client, event):
            return
        lines = []
        if muted_private:
            lines += ["• خاص:"] + [f"  - {u}" for u in muted_private]
        for cid, users in muted_groups.items():
            if users:
                lines += [f"\n• جروب {cid}:"] + [f"  - {u}" for u in users]
        await qedit(event, "\n".join(lines) if lines else "لا يوجد مكتومين.")

    @client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
    async def cmd_mclear(event):
        if not await is_owner(client, event):
            return
        muted_private.clear()
        muted_groups.clear()
        await qedit(event, "🗑️ تم المسح.")

    @client.on(events.NewMessage(incoming=True))
    async def auto_del(event):
        if (event.is_private and event.sender_id in muted_private) or (
            event.chat_id in muted_groups
            and event.sender_id in muted_groups[event.chat_id]
        ):
            return await event.delete()
