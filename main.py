import asyncio
import os
import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest

# بيانات الاتصال
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu3LbcZl_ZaB1NarDuo3EmApdJbr4sseU-..."  # اختصرته للعرض

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# المتغيرات
muted_private = set()
muted_groups = {}
welcome_enabled = {}
welcome_message = {}
clone_list = set()
auto_name = True

# --------- تغيير الاسم الوقتي ---------
async def update_name_loop():
    while True:
        if auto_name:
            now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
            name = now.strftime('%I:%M')
            try:
                await client(UpdateProfileRequest(first_name=name))
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                pass
        await asyncio.sleep(60)

# --------- أوامر الاسم ---------
@client.on(events.NewMessage(pattern=r"\.تشغيل الاسم"))
async def start_auto_name(event):
    global auto_name
    auto_name = True
    msg = await event.edit("✅ تم تشغيل الاسم الوقتي.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"\.ايقاف الاسم"))
async def stop_auto_name(event):
    global auto_name
    auto_name = False
    msg = await event.edit("🛑 تم إيقاف الاسم الوقتي.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- أمر فحص ---------
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def ping(event):
    try:
        msg = await event.edit("✅ البوت شغال وبأفضل حال!")
        await client.send_message("me", "✨ حياتي الصعب، البوت شغال.")
        await asyncio.sleep(10)
        await msg.delete()
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)

# --------- كشف معلومات القروب أو القناة ---------
@client.on(events.NewMessage(pattern=r"\.كشف"))
async def cmd_kashf(event):
    chat = await event.get_chat()
    try:
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            full = await client(GetFullChannelRequest(chat))
            title = full.chats[0].title
            id_ = full.chats[0].id
            members_count = full.full_chat.participants_count
            about = full.full_chat.about or "لا يوجد وصف"
        else:
            full = await client(GetFullChatRequest(chat))
            title = full.chats[0].title
            id_ = full.chats[0].id
            members_count = len(full.full_chat.participants)
            about = full.full_chat.about or "لا يوجد وصف"
    except Exception:
        title = getattr(chat, 'title', '❌')
        id_ = getattr(chat, 'id', '❌')
        members_count = "❌"
        about = "❌"
    text = (f"📊 معلومات:\n"
            f"🔹 الاسم: {title}\n"
            f"🔹 الايدي: `{id_}`\n"
            f"🔹 عدد الأعضاء: {members_count}\n"
            f"🔹 الوصف:\n{about}")
    await event.reply(text)

# --------- قائمة الأوامر ---------
@client.on(events.NewMessage(pattern=r"\.اوامر"))
async def list_commands(event):
    await event.respond("🧠 أوامر البوت:\n.فحص\n.كشف\n.كتم\n.الغاء الكتم\n.تشغيل الاسم\n.ايقاف الاسم\n.قائمة الكتم\n.مسح الكتم")

# --------- كتم / فك / عرض الكتم ---------
@client.on(events.NewMessage(pattern=r"\.كتم$", func=lambda e: e.is_reply))
async def mute_user(event):
    reply = await event.get_reply_message()
    if reply:
        uid, cid = reply.sender_id, event.chat_id
        (muted_private if event.is_private else muted_groups.setdefault(cid, set())).add(uid)
        msg = await event.edit("🔇 تم الكتم.")
        await asyncio.sleep(1)
        await msg.delete()

@client.on(events.NewMessage(pattern=r"\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute_user(event):
    reply = await event.get_reply_message()
    if reply:
        uid, cid = reply.sender_id, event.chat_id
        (muted_private if event.is_private else muted_groups.get(cid, set())).discard(uid)
        msg = await event.edit("🔊 تم فك الكتم.")
        await asyncio.sleep(1)
        await msg.delete()

@client.on(events.NewMessage(pattern=r"\.قائمة الكتم$"))
async def list_muted(event):
    text = "📋 المكتومين:\n"
    for uid in muted_private:
        try:
            user = await client.get_entity(uid)
            text += f"🔸 خاص: {user.first_name}\n"
        except:
            continue
    for cid, users in muted_groups.items():
        if users:
            try:
                chat = await client.get_entity(cid)
                text += f"\n🔹 {chat.title}:\n"
                for uid in users:
                    try:
                        user = await client.get_entity(uid)
                        text += f" - {user.first_name}\n"
                    except:
                        continue
            except:
                continue
    await event.respond(text or "لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"\.مسح الكتم$"))
async def clear_mutes(event):
    muted_private.clear()
    muted_groups.clear()
    msg = await event.edit("🗑️ تم مسح المكتومين.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- حذف رسائل المكتومين + حفظ الوسائط المؤقتة ---------
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()
    if event.is_private and event.media and getattr(event.media, 'ttl_seconds', None):
        try:
            path = await event.download_media("downloads/")
            await client.send_file("me", path, caption="📸 تم حفظ البصمة.")
            os.remove(path)
        except:
            pass

# --------- تشغيل البوت ---------
async def main():
    await client.start()
    asyncio.create_task(update_name_loop())
    print("✅ البوت يعمل الآن.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
