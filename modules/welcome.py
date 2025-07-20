from telethon import events
from utils import is_owner, qedit

welcome_cfg = {}


def register(client):
    @client.on(events.ChatAction)
    async def welcome(event):
        if not (event.user_joined or event.user_added):
            return
        cfg = welcome_cfg.get(event.chat_id)
        if not (cfg and cfg["enabled"]):
            return
        user, chat = await event.get_user(), await event.get_chat()
        msg = cfg["msg"].format(
            الاسم=user.first_name, الايدي=user.id, القروب=chat.title
        )
        await client.send_message(event.chat_id, msg)

    @client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
    async def w_on(event):
        if not await is_owner(client, event):
            return
        welcome_cfg[event.chat_id] = {"enabled": True, "msg": "اهلا {الاسم} 🌸"}
        await qedit(event, "✅ تم التفعيل.")

    @client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
    async def w_off(event):
        if not await is_owner(client, event):
            return
        welcome_cfg[event.chat_id] = {"enabled": False, "msg": " "}
        await qedit(event, "🛑 تم التعطيل.")

    @client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
    async def w_set(event):
        if not await is_owner(client, event):
            return
        txt = event.pattern_match.group(1)
        welcome_cfg[event.chat_id] = {"enabled": True, "msg": txt}
        await qedit(event, "📩 تم تحديث الترحيب.")
