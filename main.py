# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest

# بيانات البوت
api_id = 20507759   # <-- غيّر إلى الخاص بك
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHPHEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgKVts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEghyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)

muted_users = set()
imitate_users = set()
channel_title_tasks = {}
change_name_task = None
previous_name = None

saved_media = {}

# التحقق من المالك فقط
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

# تغيير الاسم الشخصي كل دقيقة بتوقيت بغداد
async def name_loop():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        t = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%I:%M")
        try:
            await client(UpdateProfileRequest(first_name=t))
        except: pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_temp_name(event):
    global change_name_task
    if not await is_owner(event): return
    if change_name_task: return await event.reply("مفعل مسبقاً")
    change_name_task = asyncio.create_task(name_loop())
    await event.reply("✅ تم تفعيل تغيير الاسم كل دقيقة")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_temp_name(event):
    global change_name_task, previous_name
    if not await is_owner(event): return
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
        try:
            if previous_name:
                await client(UpdateProfileRequest(first_name=previous_name))
        except: pass
    await event.reply("🛑 تم إيقاف الاسم المؤقت")

# تغيير اسم القناة كل دقيقة
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def start_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        return await event.reply("❌ فشل في الوصول للقناة")
    cid = chat.id
    if cid in channel_title_tasks:
        return await event.reply("🔄 مفعّل مسبقاً")
    old_title = chat.title
    async def update_title():
        try:
            while True:
                title = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%I:%M")
                await client(EditTitleRequest(chat, title))
                await asyncio.sleep(60)
        except: pass
    task = asyncio.create_task(update_title())
    channel_title_tasks[cid] = (task, old_title)
    await event.reply("✅ تم تفعيل تغيير اسم القناة")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        return await event.reply("❌ فشل في الوصول")
    cid = chat.id
    if cid in channel_title_tasks:
        task, old = channel_title_tasks.pop(cid)
        task.cancel()
        try:
            await client(EditTitleRequest(chat, old))
        except: pass
        await event.reply("🛑 تم الإيقاف")
    else:
        await event.reply("❌ لا يوجد تحديث مفعّل")

# كتم و فك كتم
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    muted_users.add(reply.sender_id)
    await event.reply("تم كتم الشخص")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    muted_users.discard(reply.sender_id)
    await event.reply("تم فك الكتم")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event): return
    if not muted_users:
        return await event.reply("لا يوجد مكتومين")
    text = "📋 قائمة المكتومين:\n"
    for user_id in muted_users:
        try:
            user = await client.get_entity(user_id)
            text += f"• {user.first_name}\n"
        except: continue
    await event.reply(text)

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def clear_mute(event):
    if not await is_owner(event): return
    muted_users.clear()
    await event.reply("✅ تم مسح القائمة")

# تقليد شخص معين فقط
@client.on(events.NewMessage(pattern=r"^\.قلده$", func=lambda e: e.is_reply))
async def imitate_user(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    imitate_users.add(reply.sender_id)
    await event.reply("✅ سيبدأ تقليد هذا الشخص فقط")

@client.on(events.NewMessage(pattern=r"^\.لاتقلده$", func=lambda e: e.is_reply))
async def stop_imitate_user(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    imitate_users.discard(reply.sender_id)
    await event.reply("🛑 تم إيقاف تقليده")

# تقليد رسائل الشخص المضاف فقط
@client.on(events.NewMessage(incoming=True))
async def imitate_incoming(event):
    if event.sender_id in imitate_users:
        if event.media:
            file = await event.download_media("temp/")
            await client.send_file(event.chat_id, file, caption=event.text or "")
            os.remove(file)
        elif event.text:
            await event.respond(event.text)

    if event.sender_id in muted_users:
        await event.delete()

# حفظ بصمة
@client.on(events.NewMessage(pattern=r"^\.احفظ (.+)$", func=lambda e: e.is_reply))
async def save(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if reply.media:
        path = await reply.download_media(f"downloads/{name}")
        saved_media[name] = path
        await event.reply(f"✅ تم الحفظ باسم: {name}")
    else:
        await event.reply("❌ لا يوجد وسائط")

# إرسال بصمة محفوظة
@client.on(events.NewMessage())
async def send_saved(event):
    if not await is_owner(event): return
    name = event.raw_text.strip()
    path = saved_media.get(name)
    if path and os.path.exists(path):
        await client.send_file(event.chat_id, path)
        await event.delete()

# أمر الوقت حسب بغداد
@client.on(events.NewMessage(pattern=r"^\.الوقت$"))
async def time_now(event):
    if not await is_owner(event): return
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%I:%M %p")
    await event.reply(f"🕒 الوقت الآن في بغداد:\n`{now}`")

# تشغيل البوت
async def main():
    await client.start()
    print("✅ البوت يعمل")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
