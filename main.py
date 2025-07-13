# -*- coding: utf-8 -*-
import asyncio
import os
import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# بيانات الجلسة
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu3cFPR8Mg8e7L_ziTRYf1asEKqvG9LnTCpxCI1tfhIienyV1R6ZsoqRagi05md2RxyIy0RA_ACKFr6qAryc-n66NEW7XihIhFXBBnmlMQ8gC1fSB_14X5DAMgjyte6SY-ssJ7xxVx-A6-eSvosDAJtVZcy0vePv_KCPEp6utel3zg-LzZOHayExqYg4TMAbnLtbna1opvcomXpYTZDaUsw5aHJ5EKBwYoz3EBRYnKQY4L_NC03tef7gGW0eqejpkUPd6_qDH9ivhKl7CBLY7c3F4VYtcOgW6f8GJow_XBi-NUIZAF-BftOTO2h_Tx83UavLtpNjWYwaSjwugBiXo-OY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
imitate_user = None  # معرف المستخدم المُقلَّد فقط

# تغيير الاسم الشخصي كل 60 ثانية
@client.on(events.NewMessage(pattern=r'^\.اسم مؤقت$'))
async def start_name_change(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    async def update_name():
        while True:
            name = datetime.datetime.utcnow().strftime("%I:%M:%S")
            try:
                await client(UpdateProfileRequest(first_name=name))
            except:
                pass
            await asyncio.sleep(60)
    client.loop.create_task(update_name())
    await event.respond("✅ بدأ تغيير الاسم الشخصي كل 60 ثانية.")

# أمر تغيير اسم القناة تلقائيًا
@client.on(events.NewMessage(pattern=r'^\.اسم قناة (.+)$'))
async def start_channel_name_change(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    link = event.pattern_match.group(1)
    try:
        entity = await client.get_entity(link)
        await client(EditTitleRequest(entity, datetime.datetime.utcnow().strftime("%I:%M:%S")))
    except ChatAdminRequiredError:
        return await event.reply("❌ لا أملك صلاحية تغيير اسم القناة.")
    except:
        return await event.reply("❌ تحقق من الرابط.")

    async def update_channel_name():
        while True:
            title = datetime.datetime.utcnow().strftime("%I:%M:%S")
            try:
                await client(EditTitleRequest(entity, title))
            except:
                pass
            await asyncio.sleep(60)

    client.loop.create_task(update_channel_name())
    await event.reply("✅ بدأ تغيير اسم القناة كل 60 ثانية.")

# تقليد مستخدم واحد فقط
@client.on(events.NewMessage(pattern=r'^\.تقليد$', func=lambda e: e.is_reply))
async def imitate_user_command(event):
    global imitate_user
    if not event.sender_id == (await client.get_me()).id:
        return
    reply = await event.get_reply_message()
    imitate_user = reply.sender_id
    await event.respond("✅ سيتم تقليد هذا المستخدم فقط.")

# إلغاء التقليد
@client.on(events.NewMessage(pattern=r'^\.لاتقلده$'))
async def stop_imitate(event):
    global imitate_user
    if not event.sender_id == (await client.get_me()).id:
        return
    imitate_user = None
    await event.respond("🛑 تم إلغاء التقليد.")

# تنفيذ التقليد للمستخدم المحدد فقط
@client.on(events.NewMessage(incoming=True))
async def imitate_handler(event):
    global imitate_user
    if imitate_user and event.sender_id == imitate_user:
        if event.media:
            file = await event.download_media()
            await client.send_file(event.chat_id, file, caption=event.text or "")
            if os.path.exists(file):
                os.remove(file)
        elif event.text:
            await event.respond(event.text)

# أمر حفظ الوسائط
saved_media = {}
@client.on(events.NewMessage(pattern=r'^\.احفظ (.+)$', func=lambda e: e.is_reply))
async def save_fingerprint(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    name = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not reply.media:
        return await event.reply("❌ لا توجد وسائط.")
    path = await reply.download_media(f"downloads/{name}")
    saved_media[name] = path
    await event.reply(f"✅ تم حفظ الوسائط باسم: {name}")

# إرسال بصمة محفوظة
@client.on(events.NewMessage())
async def send_fingerprint(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    if not event.raw_text.startswith(".") or " " in event.raw_text:
        return
    name = event.raw_text[1:]
    path = saved_media.get(name)
    if path and os.path.exists(path):
        await client.send_file(event.chat_id, path)
        await event.delete()

# قائمة البصمات
@client.on(events.NewMessage(pattern=r'^\.قائمة البصمات$'))
async def list_fingerprints(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    if not saved_media:
        return await event.reply("❌ لا توجد بصمات محفوظة.")
    msg = "📋 قائمة الوسائط:\n" + "\n".join([f"🔹 {name}" for name in saved_media])
    await event.reply(msg)

# فحص
@client.on(events.NewMessage(pattern=r'^\.فحص$'))
async def check(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    await event.edit("✅ البوت يعمل.")
    await asyncio.sleep(5)
    await event.delete()

# قائمة الأوامر
@client.on(events.NewMessage(pattern=r'^\.اوامر$'))
async def show_commands(event):
    if not event.sender_id == (await client.get_me()).id:
        return
    await event.reply("""
📜 أوامر البوت:
.فحص – التأكد من عمل البوت
.اسم مؤقت – تغيير الاسم الشخصي كل دقيقة
.اسم قناة <رابط> – تغيير اسم قناة كل دقيقة
.تقليد (بالرد) – تقليد شخص واحد فقط
.لاتقلده – إيقاف التقليد
.احفظ <اسم> (رد على وسائط) – حفظ الوسائط باسم
.<اسم> – إرسال الوسائط المحفوظة
.قائمة البصمات – عرض جميع البصمات
""")
    await event.delete()

# بدء التشغيل
async def main():
    await client.start()
    print("✅ البوت يعمل.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
