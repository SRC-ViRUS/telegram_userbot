# -*- coding: utf-8 -*-
import asyncio, os, datetime
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# ========== بيانات الاتصال ==========
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu0ivnheKrzAuzLihTMiNKMOurFuPNZJnqUpQxByZCzW3pqY9n1L3u2tXJ8oBValiSz8eaK_2M4MBSyLfIetg1SpTm665HNI2vcHWjHaIrWeVGsYYIxIbrnuw8k4vZBOtskw1Lb6lAbBwFfU7ankI3bHNNwZ5jrEhidlP2qi77A53r9m-SoZmoPCcXMNd9TvTLDImAGxslVEtSEQJbfFTnb0LTcGVOfYePGbywRlDQnmFF0uuCRG03iy4eMVjXVQLgW2b_OcfFoWZqLuGDMQIqKxvmWnpL_cpG5hETUGtzbZBjT1Z447_g7FsQQcUeVmEaVpuNY5WLYXqPRbQr-3UUAk=" 

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ========== متغيرات ==========
muted_private = set()
muted_groups = {}
previous_name = None
change_name_task = None
channel_name_tasks = {}

# ========== فحص المالك ==========
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

# ========== توليد جلسة ==========
@client.on(events.NewMessage(pattern=r"\.جلسة"))
async def generate_session(event):
    if not await is_owner(event): return
    await event.respond("🔐 أرسل `api_id` الآن:")
    response = await client.wait_for(events.NewMessage(from_users=event.sender_id))
    api_id_user = int(response.text)

    await event.respond("🔐 أرسل `api_hash` الآن:")
    response = await client.wait_for(events.NewMessage(from_users=event.sender_id))
    api_hash_user = response.text

    await event.respond("📞 أرسل رقم هاتفك (مع +):")
    response = await client.wait_for(events.NewMessage(from_users=event.sender_id))
    phone = response.text

    temp = TelegramClient(StringSession(), api_id_user, api_hash_user)
    await temp.connect()

    try:
        sent = await temp.send_code_request(phone)
        await event.respond("✉️ تم إرسال كود. أرسل الكود الآن:")
        code = (await client.wait_for(events.NewMessage(from_users=event.sender_id))).text

        try:
            await temp.sign_in(phone, code)
        except SessionPasswordNeededError:
            await event.respond("🔒 الحساب فيه تحقق بخطوتين. أرسل كلمة السر:")
            pw = (await client.wait_for(events.NewMessage(from_users=event.sender_id))).text
            await temp.sign_in(password=pw)

        string = temp.session.save()
        await event.respond("✅ تم إنشاء الجلسة بنجاح.")
        await client.send_message("me", f"✨ هذا هو StringSession:\n`{string}`")
        await temp.disconnect()
    except PhoneCodeInvalidError:
        await event.respond("❌ كود التحقق غير صحيح.")
    except Exception as e:
        await event.respond(f"❌ حدث خطأ: {e}")
    await event.delete()

# ========== تغيير الاسم الشخصي حسب الوقت ==========
async def change_name_periodically():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        name = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M')
        try:
            await client(UpdateProfileRequest(first_name=name))
        except: pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"\.اسم مؤقت"))
async def start_changing_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return
    change_name_task = asyncio.create_task(change_name_periodically())
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.ايقاف الاسم"))
async def stop_changing_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try: await client(UpdateProfileRequest(first_name=previous_name))
        except: pass
    await event.delete()

# ========== اسم مؤقت للقنوات والكروبات ==========
@client.on(events.NewMessage(pattern=r"\.اسم قناة (.+)"))
async def temp_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except Exception as e:
        await event.respond(f"❌ الرابط غير صالح: {e}")
        await event.delete()
        return
    cid = chat.id
    if cid in channel_name_tasks:
        await event.respond("🔄 التغيير مفعل مسبقًا.")
        await event.delete()
        return

    prev_title = getattr(chat, "title", None)
    try:
        await client.edit_title(chat, datetime.datetime.now(datetime.timezone.utc).strftime('%I:%M'))
    except:
        await event.respond("🚫 لا أملك صلاحية تغيير الاسم.")
        await event.delete()
        return

    async def updater():
        try:
            while True:
                title = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M')
                await client.edit_title(chat, title)
                msgs = await client.get_messages(chat, limit=1)
                if msgs and msgs[0].message is None:
                    await msgs[0].delete()
                await asyncio.sleep(60)
        finally:
            if prev_title:
                try: await client.edit_title(chat, prev_title)
                except: pass

    task = asyncio.create_task(updater())
    channel_name_tasks[cid] = {'task': task, 'prev': prev_title}
    await event.respond("✅ بدأ التحديث التلقائي.")
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.ايقاف اسم قناة (.+)"))
async def stop_temp_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try: chat = await client.get_entity(link)
    except: await event.respond("❌ الرابط غير صالح."); return
    data = channel_name_tasks.pop(chat.id, None)
    if not data:
        await event.respond("❌ لا يوجد تحديث نشط.")
        return
    data['task'].cancel()
    if data['prev']:
        try: await client.edit_title(chat, data['prev'])
        except: pass
    await event.respond("🛑 تم إيقاف الاسم التلقائي.")

# ========== فحص ==========
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def check(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    msg = await event.edit("⌛")
    end = datetime.datetime.now()
    await msg.edit(f"✅ البوت شغال\n📶 `{(end-start).microseconds//1000}ms`")
    await asyncio.sleep(10)
    await msg.delete()

# ========== كشف معلومات ==========
@client.on(events.NewMessage(pattern=r"\.كشف"))
async def get_info(event):
    if not await is_owner(event): return
    chat = await event.get_chat()
    try:
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            full = await client(GetFullChannelRequest(chat))
            title = full.chats[0].title
            id_ = full.chats[0].id
            members = full.full_chat.participants_count
            about = full.full_chat.about or "لا يوجد وصف"
        else:
            full = await client(GetFullChatRequest(chat))
            title = full.chats[0].title
            id_ = full.chats[0].id
            members = len(full.full_chat.participants)
            about = full.full_chat.about or "لا يوجد وصف"
    except:
        title, id_, members, about = "❌", "❌", "❌", "❌"
    await event.respond(f"📊 معلومات:\n🔹 الاسم: {title}\n🔹 الايدي: `{id_}`\n🔹 عدد الأعضاء: {members}\n🔹 الوصف:\n{about}")
    await event.delete()

# ========== كتم / فك كتم ==========
@client.on(events.NewMessage(pattern=r"\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event): return
    text = "📋 المكتومين:\n"
    for uid in muted_private:
        try: user = await client.get_entity(uid)
        except: continue
        text += f"🔸 خاص: {user.first_name}\n"
    for cid, uids in muted_groups.items():
        try: chat = await client.get_entity(cid)
        except: continue
        text += f"\n🔹 {chat.title}:\n"
        for uid in uids:
            try: user = await client.get_entity(uid)
            except: continue
            text += f" - {user.first_name}\n"
    await event.respond(text or "لا يوجد مكتومين.")
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.مسح الكتم$"))
async def clear_mute(event):
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await event.delete()

# ========== تقليد متطور ==========
@client.on(events.NewMessage(pattern=r"\.تقليد$", func=lambda e: e.is_reply))
async def imitate_all(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if reply.media:
        ttl = getattr(reply.media, 'ttl_seconds', None)
        path = await reply.download_media("downloads/")
        try:
            await client.send_file(event.chat_id, path, caption=reply.text or "", ttl_seconds=ttl)
        finally:
            if os.path.exists(path): os.remove(path)
    elif reply.text:
        await event.respond(reply.text)
    await event.delete()

# ========== حفظ الوسائط المؤقتة ==========
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()
    if event.media and getattr(event.media, 'ttl_seconds', None):
        path = await event.download_media("downloads/")
        await client.send_file("me", path, caption="📸 تم الحفظ", ttl_seconds=event.media.ttl_seconds)
        if os.path.exists(path): os.remove(path)

# ========== قائمة الأوامر ==========
@client.on(events.NewMessage(pattern=r"\.اوامر"))
async def cmds(event):
    if not await is_owner(event): return
    await event.respond(
        "🧠 أوامر البوت:\n\n"
        ".جلسة - توليد جلسة تليثون\n"
        ".فحص - اختبار عمل البوت\n"
        ".كشف - كشف معلومات الكروب/القناة\n"
        ".كتم / .الغاء الكتم (بالرد)\n"
        ".قائمة الكتم / .مسح الكتم\n"
        ".اسم مؤقت / .ايقاف الاسم\n"
        ".اسم قناة <رابط> / .ايقاف اسم قناة <رابط>\n"
        ".تقليد (بالرد)\n"
    )
    await event.delete()

# ========== تشغيل البوت ==========
async def main():
    await client.start()
    print("✅ البوت يعمل.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
