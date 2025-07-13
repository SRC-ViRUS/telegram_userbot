# -*- coding: utf-8 -*-
import asyncio, os, datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# ---------- بيانات الاتصال ----------
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu3cFPR8Mg8e7L_ziTRYf1asEKqvG9LnTCpxCI1tfhIienyV1R6ZsoqRagi05md2RxyIy0RA_ACKFr6qAryc-n66NEW7XihIhFXBBnmlMQ8gC1fSB_14X5DAMgjyte6SY-ssJ7xxVx-A6-eSvosDAJtVZcy0vePv_KCPEp6utel3zg-LzZOHayExqYg4TMAbnLtbna1opvcomXpYTZDaUsw5aHJ5EKBwYoz3EBRYnKQY4L_NC03tef7gGW0eqejpkUPd6_qDH9ivhKl7CBLY7c3F4VYtcOgW6f8GJow_XBi-NUIZAF-BftOTO2h_Tx83UavLtpNjWYwaSjwugBiXo-OY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ---------- متغيّرات ----------
muted_private, muted_groups = set(), {}
imitate_user = None            # الشخص المقلَّد
change_name_task = None        # مهمة تغيير الاسم الشخصي
channel_name_tasks = {}        # {cid:{task,prev}}
saved_media = {}               # {name:path}
previous_name = None

# ---------- مساعدات ----------
async def is_owner(event):
    return event.sender_id == (await client.get_me()).id

# ---------- تغيير الاسم الشخصي كل 60 ثانية ----------
async def name_loop():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        t = datetime.datetime.utcnow().strftime("%I:%M")
        try:
            await client(UpdateProfileRequest(first_name=t))
        except: pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def name_temp_on(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await event.reply("🔄 مفعل مسبقًا.")
    change_name_task = asyncio.create_task(name_loop())
    await event.reply("✅ تغيير الاسم الشخصي كل 60 ثانية.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def name_temp_off(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task: change_name_task.cancel()
    change_name_task = None
    if previous_name:
        try: await client(UpdateProfileRequest(first_name=previous_name))
        except: pass
    await event.reply("🛑 تم الإيقاف.")

# ---------- تغيير اسم القناة كل 60 ثانية ----------
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def chan_name_on(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try: chat = await client.get_entity(link)
    except: return await event.reply("❌ رابط غير صالح.")
    cid = chat.id
    if cid in channel_name_tasks:
        return await event.reply("🔄 مفعل مسبقًا.")
    prev = getattr(chat, "title", None)
    async def loop():
        try:
            while True:
                title = datetime.datetime.utcnow().strftime("%I:%M")
                try:
                    await client(EditTitleRequest(chat, title))
                    # حذف رسالة النظام (بدون نص)
                    m = await client.get_messages(chat, 1)
                    if m and not m[0].message: await m[0].delete()
                except ChatAdminRequiredError:
                    await client.send_message(event.chat_id, "🚫 لا صلاحية لتغيير الاسم."); break
                await asyncio.sleep(60)
        finally:
            if prev:
                try: await client(EditTitleRequest(chat, prev))
                except: pass
    task = asyncio.create_task(loop())
    channel_name_tasks[cid] = {"task": task, "prev": prev}
    await event.reply("✅ بدأ التحديث.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def chan_name_off(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try: chat = await client.get_entity(link)
    except: return await event.reply("❌ رابط غير صالح.")
    data = channel_name_tasks.pop(chat.id, None)
    if not data: return await event.reply("❌ غير مفعّل.")
    data["task"].cancel()
    if data["prev"]:
        try: await client(EditTitleRequest(chat, data["prev"]))
        except: pass
    await event.reply("🛑 تم الإيقاف.")

# ---------- تقليد شخص واحد ----------
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate_set(event):
    global imitate_user
    if not await is_owner(event): return
    imitate_user = (await event.get_reply_message()).sender_id
    await event.reply("✅ سيتم تقليد هذا المستخدم.")

@client.on(events.NewMessage(pattern=r"^\.لاتقلده$"))
async def imitate_clear(event):
    global imitate_user
    if not await is_owner(event): return
    imitate_user = None
    await event.reply("🛑 تم إلغاء التقليد.")

@client.on(events.NewMessage(incoming=True))
async def imitate_run(event):
    if imitate_user and event.sender_id == imitate_user:
        if event.media:
            f = await event.download_media("downloads/")
            await client.send_file(event.chat_id, f, caption=event.text or "")
            if os.path.exists(f): os.remove(f)
        elif event.text:
            await event.respond(event.text)

# ---------- كتم / فك كتم ----------
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id,set())).add(r.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id,set())).discard(r.sender_id)
    await event.delete()

# ---------- حذف رسائل المكتومين ----------
@client.on(events.NewMessage(incoming=True))
async def del_muted(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()

# ---------- حفظ / إرسال / حذف بصمات ----------
@client.on(events.NewMessage(pattern=r"^\.احفظ (.+)$", func=lambda e: e.is_reply))
async def save_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    r = await event.get_reply_message()
    if not r.media: return await event.reply("❌ لا توجد وسائط.")
    path = await r.download_media(f"downloads/{name}")
    saved_media[name] = path
    await event.reply("✅ تم الحفظ.")

@client.on(events.NewMessage(pattern=r"^\.حذف (.+)$"))
async def del_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    p = saved_media.pop(name, None)
    if p and os.path.exists(p): os.remove(p); await event.reply("🗑️ تم الحذف.")
    else: await event.reply("❌ غير موجود.")

@client.on(events.NewMessage(pattern=r"^\.قائمة البصمات$"))
async def list_media(event):
    if not await is_owner(event): return
    if not saved_media: return await event.reply("⚠️ لا توجد بصمات.")
    await event.reply("📋 البصمات:\n"+"\n".join(f"• {n}" for n in saved_media))

@client.on(events.NewMessage(pattern=r"^\.(\w+)$"))
async def send_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1)
    p = saved_media.get(name)
    if p and os.path.exists(p):
        await client.send_file(event.chat_id, p); await event.delete()

# ---------- فحص ----------
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def ping(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    msg = await event.edit("⌛")
    end = datetime.datetime.now()
    await msg.edit(f"✅ { (end-start).microseconds//1000 }ms")
    await asyncio.sleep(3)
    await msg.delete()

# ---------- قائمة الأوامر ----------
@client.on(events.NewMessage(pattern=r"^\.اوامر$"))
async def cmds(event):
    if not await is_owner(event): return
    await event.respond("""
📜 أوامر البوت:
.اسم مؤقت             – تفعيل تغيير الاسم كل دقيقة
.ايقاف الاسم           – إيقاف تغيير الاسم
.اسم قناة <رابط>       – تفعيل تغيير اسم القناة كل دقيقة
.ايقاف اسم قناة <رابط> – إيقاف تغيير اسم القناة
.تقليد (بالرد)         – تقليد شخص واحد
.لاتقلده               – إلغاء التقليد
.كتم / .الغاء الكتم (رد) – كتم/فك كتم عضو
.احفظ <اسم> (رد على وسائط) – حفظ وسائط
.<اسم>                 – إرسال الوسائط المحفوظة
.حذف <اسم>            – حذف بصمة
.قائمة البصمات         – عرض البصمات
""")
    await event.delete()

# ---------- تشغيل البوت ----------
async def main():
    await client.start()
    print("✅ Bot is running.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
