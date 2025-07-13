# -*- coding: utf-8 -*-
import asyncio
import os
import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest, EditTitleRequest
from telethon.tl.functions.messages import GetFullChatRequest

# بيانات الاتصال
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu3cFPR8Mg8e7L_ziTRYf1asEKqvG9LnTCpxCI1tfhIienyV1R6ZsoqRagi05md2RxyIy0RA_ACKFr6qAryc-n66NEW7XihIhFXBBnmlMQ8gC1fSB_14X5DAMgjyte6SY-ssJ7xxVx-A6-eSvosDAJtVZcy0vePv_KCPEp6utel3zg-LzZOHayExqYg4TMAbnLtbna1opvcomXpYTZDaUsw5aHJ5EKBwYoz3EBRYnKQY4L_NC03tef7gGW0eqejpkUPd6_qDH9ivhKl7CBLY7c3F4VYtcOgW6f8GJow_XBi-NUIZAF-BftOTO2h_Tx83UavLtpNjWYwaSjwugBiXo-OY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# متغيرات
muted_private = set()
muted_groups = {}
previous_name = None
change_name_task = None
channel_name_tasks = {}
imitate_enabled = False  # حالة التقليد التلقائي
saved_media = {}  # حفظ الوسائط باسم: {'name': path}

# التحقق من المالك فقط
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

# تنظيف كامل قبل التشغيل
async def cleanup():
    global change_name_task, channel_name_tasks, muted_private, muted_groups, saved_media

    # إلغاء مهمة تغيير الاسم المؤقت لو كانت شغالة
    if change_name_task and not change_name_task.done():
        change_name_task.cancel()

    # إلغاء مهام تغيير اسم القنوات وإرجاع الاسم الأصلي
    for cid, data in channel_name_tasks.items():
        data['task'].cancel()
        prev = data.get('prev')
        if prev:
            try:
                await client(EditTitleRequest(channel=cid, title=prev))
            except:
                pass
    channel_name_tasks.clear()

    # مسح المكتومين
    muted_private.clear()
    muted_groups.clear()

    # مسح الوسائط المحفوظة من مجلد التنزيل ومسح القاموس
    for path in saved_media.values():
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    saved_media.clear()

    # مسح مجلد التنزيل بالكامل
    folder = "downloads"
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except:
                pass

# تغيير الاسم الشخصي تلقائياً كل 20 ثانية
async def change_name_periodically():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        name = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M:%S')
        try:
            await client(UpdateProfileRequest(first_name=name))
        except:
            pass
        await asyncio.sleep(20)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_changing_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await event.reply("🔄 تغيير الاسم التلقائي مفعل مسبقًا.")
    change_name_task = asyncio.create_task(change_name_periodically())
    await event.reply("✅ بدأ تغيير الاسم التلقائي كل 20 ثانية.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_changing_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
            await event.reply("🛑 تم إيقاف تغيير الاسم وإرجاع الاسم السابق.")
        except Exception as e:
            await event.reply(f"❌ خطأ: {e}")
    else:
        await event.reply("❌ لا يوجد اسم سابق محفوظ.")

# اسم قناة/كروب مؤقت يتغير كل 20 ثانية (يحذف إشعار تغيير الاسم)
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def temp_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except Exception as e:
        await event.respond(f"❌ الرابط غير صالح: {e}")
        return

    cid = chat.id
    if cid in channel_name_tasks:
        return await event.respond("🔄 التغيير مفعل مسبقًا.")

    prev_title = getattr(chat, "title", None)
    try:
        await client.edit_title(chat, (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M:%S'))
    except:
        return await event.respond("🚫 لا أملك صلاحية تغيير الاسم.")

    async def updater():
        try:
            while True:
                title = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M:%S')
                await client.edit_title(chat, title)
                msgs = await client.get_messages(chat, limit=1)
                if msgs and msgs[0].message is None:
                    await msgs[0].delete()
                await asyncio.sleep(20)
        finally:
            if prev_title:
                try:
                    await client.edit_title(chat, prev_title)
                except:
                    pass

    task = asyncio.create_task(updater())
    channel_name_tasks[cid] = {'task': task, 'prev': prev_title}
    await event.respond("✅ بدأ التحديث التلقائي لاسم القناة/الكروب.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_temp_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        return await event.respond("❌ الرابط غير صالح.")
    data = channel_name_tasks.pop(chat.id, None)
    if not data:
        return await event.respond("❌ لا يوجد تحديث نشط لاسم القناة/الكروب.")
    data['task'].cancel()
    if data['prev']:
        try:
            await client.edit_title(chat, data['prev'])
        except:
            pass
    await event.respond("🛑 تم إيقاف التحديث التلقائي لاسم القناة/الكروب.")

# فحص حالة البوت
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    msg = await event.edit("⌛ جاري الفحص...")
    end = datetime.datetime.now()
    await msg.edit(f"✅ البوت شغال\n📶 `{(end-start).microseconds//1000}ms`")
    await asyncio.sleep(10)
    await msg.delete()

# كشف معلومات القروب/القناة
@client.on(events.NewMessage(pattern=r"^\.كشف$"))
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

# كتم / فك كتم (خاص وعام)
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event): return
    text = "📋 المكتومين:\n"
    for uid in muted_private:
        try:
            user = await client.get_entity(uid)
            text += f"🔸 خاص: {user.first_name}\n"
        except:
            continue
    for cid, uids in muted_groups.items():
        try:
            chat = await client.get_entity(cid)
            text += f"\n🔹 {chat.title}:\n"
            for uid in uids:
                try:
                    user = await client.get_entity(uid)
                    text += f" - {user.first_name}\n"
                except:
                    continue
        except:
            continue
    await event.respond(text or "لا يوجد مكتومين.")
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def clear_mute(event):
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await event.delete()

# التقليد التلقائي (تشغيل/إيقاف)
@client.on(events.NewMessage(pattern=r"^\.تقليد$"))
async def start_imitate(event):
    if not await is_owner(event): return
    global imitate_enabled
    if imitate_enabled:
        return await event.reply("🔄 التقليد التلقائي مفعل مسبقًا.")
    imitate_enabled = True
    await event.reply("✅ تم تفعيل التقليد التلقائي لكل الرسائل.")

@client.on(events.NewMessage(pattern=r"^\.لاتقلده$"))
async def stop_imitate(event):
    if not await is_owner(event): return
    global imitate_enabled
    if not imitate_enabled:
        return await event.reply("ℹ️ التقليد التلقائي معطل مسبقًا.")
    imitate_enabled = False
    await event.reply("🛑 تم تعطيل التقليد التلقائي.")

# تقليد رسالة واحدة (بالرد)
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate_one(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if reply.media:
        ttl = getattr(reply.media, 'ttl_seconds', None)
        path = await reply.download_media("downloads/")
        try:
            await client.send_file(event.chat_id, path, caption=reply.text or "", ttl_seconds=ttl)
        finally:
            if os.path.exists(path):
                os.remove(path)
    elif reply.text:
        await event.respond(reply.text)
    await event.delete()

# تطبيق التقليد التلقائي لكل الرسائل الواردة
@client.on(events.NewMessage(incoming=True))
async def imitate_handler(event):
    global imitate_enabled
    if imitate_enabled:
        me = await client.get_me()
        if event.sender_id == me.id:
            return
        if event.media:
            ttl = getattr(event.media, 'ttl_seconds', None)
            path = await event.download_media("downloads/")
            try:
                await client.send_file(event.chat_id, path, caption=event.text or "", ttl_seconds=ttl)
            finally:
                if os.path.exists(path):
                    os.remove(path)
        elif event.text:
            await event.respond(event.text)

# حذف رسائل المكتومين وحفظ الوسائط المؤقتة
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()
    if event.media and getattr(event.media, 'ttl_seconds', None):
        path = await event.download_media("downloads/")
        await client.send_file("me", path, caption="📸 تم الحفظ", ttl_seconds=event.media.ttl_seconds)
        if os.path.exists(path):
            os.remove(path)

# حفظ الوسائط باسم معين
@client.on(events.NewMessage(pattern=r"^\.احفظ (.+)$", func=lambda e: e.is_reply))
async def save_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.reply("❌ الرجاء الرد على رسالة تحتوي على وسائط.")
    path = await reply.download_media(f"downloads/{name}")
    saved_media[name] = path
    await event.reply(f"✅ تم حفظ الوسائط باسم: {name}")

# ارسال الوسائط المحفوظة
@client.on(events.NewMessage(pattern=r"^\.(.+)$"))
async def send_saved_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    path = saved_media.get(name)
    if not path or not os.path.exists(path):
        return await event.reply("❌ لا توجد وسائط محفوظة بهذا الاسم.")
    await client.send_file(event.chat_id, path)
    await event.delete()

# حذف الوسائط المحفوظة
@client.on(events.NewMessage(pattern=r"^\.حذف (.+)$"))
async def delete_saved_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    path = saved_media.pop(name, None)
    if path and os.path.exists(path):
        os.remove(path)
        await event.reply(f"✅ تم حذف الوسائط باسم: {name}")
    else:
        await event.reply("❌ لا توجد وسائط محفوظة بهذا الاسم.")

# عرض قائمة الوسائط المحفوظة (البصمات)
@client.on(events.NewMessage(pattern=r"^\.قائمة البصمات$"))
async def list_saved_media(event):
    if not await is_owner(event): return
    if not saved_media:
        return await event.reply("❌ لا توجد وسائط محفوظة.")
    text = "📋 قائمة البصمات المحفوظة:\n"
    for name in saved_media.keys():
        text += f"🔹 {name}\n"
    await event.reply(text)

# قائمة الأوامر
@client.on(events.NewMessage(pattern=r"^\.اوامر$"))
async def cmds(event):
    if not await is_owner(event): return
    await event.respond(
        "🧠 قائمة أوامر البوت:\n\n"
        ".فحص - اختبار عمل البوت\n"
        ".كشف - كشف معلومات القروب/القناة\n"
        ".كتم (بالرد) - كتم عضو\n"
        ".الغاء الكتم (بالرد) - فك كتم عضو\n"
        ".قائمة الكتم - عرض المكتومين\n"
        ".مسح الكتم - حذف جميع الكتم\n"
        ".اسم مؤقت - تفعيل تغيير الاسم الشخصي تلقائياً\n"
        ".ايقاف الاسم - إيقاف تغيير الاسم الشخصي\n"
        ".اسم قناة <رابط> - تفعيل تغيير اسم القناة/الكروب تلقائياً\n"
        ".ايقاف اسم قناة <رابط> - إيقاف تغيير اسم القناة/الكروب\n"
        ".تقليد (بالرد) - تقليد رسالة واحدة\n"
        ".تقليد - تفعيل التقليد التلقائي لكل الرسائل\n"
        ".لاتقلده - تعطيل التقليد التلقائي\n"
        ".احفظ <اسم> (بالرد على وسائط) - حفظ الوسائط باسم معين\n"
        ".<اسم> - إرسال الوسائط المحفوظة\n"
        ".حذف <اسم> - حذف الوسائط المحفوظة\n"
        ".قائمة البصمات - عرض جميع الوسائط المحفوظة\n"
    )
    await event.delete()

# تشغيل البوت
async def main():
    await client.start()
    await cleanup()  # تنظيف قبل التشغيل
    print("✅ البوت يعمل.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
