# -*- coding: utf-8 -*-
import asyncio, os, datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest

api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBu0ivnheKrzAuzLihTMiNKMOurFuPNZJnqUpQxByZCzW3pqY9n1L3u2tXJ8oBValiSz8eaK_2M4MBSyLfIetg1SpTm665HNI2vcHWjHaIrWeVGsYYIxIbrnuw8k4vZBOtskw1Lb6lAbBwFfU7ankI3bHNNwZ5jrEhidlP2qi77A53r9m-SoZmoPCcXMNd9TvTLDImAGxslVEtSEQJbfFTnb0LTcGVOfYePGbywRlDQnmFF0uuCRG03iy4eMVjXVQLgW2b_OcfFoWZqLuGDMQIqKxvmWnpL_cpG5hETUGtzbZBjT1Z447_g7FsQQcUeVmEaVpuNY5WLYXqPRbQr-3UUAk="
client = TelegramClient(StringSession(session_string), api_id, api_hash)

os.makedirs("downloads", exist_ok=True)
os.makedirs("saved_media", exist_ok=True)

# ======== متغيرات =========
muted_private = set()
muted_groups = {}
previous_name = None
change_name_task = None
channel_name_tasks = {}
saved_media = {}  # الاسم : مسار الملف
imitate_active = False

# ======== فحص المالك ========
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

# ======== تغيير الاسم الشخصي تلقائي ========
async def change_name_periodically():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
        name = now.strftime('%I:%M %p')
        try:
            await client(UpdateProfileRequest(first_name=name))
        except:
            pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"\.اسم مؤقت"))
async def start_changing_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        await event.reply("🔄 تغيير الاسم التلقائي مفعل مسبقاً.")
        return
    change_name_task = asyncio.create_task(change_name_periodically())
    await event.reply("✅ بدأ تغيير الاسم التلقائي كل دقيقة.")

@client.on(events.NewMessage(pattern=r"\.ايقاف الاسم"))
async def stop_changing_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
        except:
            pass
    await event.reply("🛑 أوقفت تغيير الاسم وأرجعت الاسم السابق.")

# ======== تغيير اسم القناة/الكروب تلقائي حسب الوقت ========
async def update_chat_title(chat, prev_title):
    try:
        while True:
            now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
            title = now.strftime('%I:%M %p')
            await client.edit_title(chat, title)
            # حذف إشعارات تغيير الاسم (آخر رسالة فارغة)
            msgs = await client.get_messages(chat, limit=1)
            if msgs and msgs[0].message is None:
                await msgs[0].delete()
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        # إرجاع الاسم القديم عند الإيقاف
        if prev_title:
            try:
                await client.edit_title(chat, prev_title)
            except:
                pass

@client.on(events.NewMessage(pattern=r"\.اسم قناة (.+)"))
async def start_temp_chat_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except Exception as e:
        await event.reply(f"❌ الرابط غير صالح: {e}")
        return
    if chat.id in channel_name_tasks:
        await event.reply("🔄 التغيير مفعل مسبقًا.")
        return
    prev_title = getattr(chat, "title", None)
    try:
        await client.edit_title(chat, datetime.datetime.now(datetime.timezone.utc).strftime('%I:%M %p'))
    except:
        await event.reply("🚫 لا أملك صلاحية تغيير الاسم في القناة/الكروب.")
        return
    task = asyncio.create_task(update_chat_title(chat, prev_title))
    channel_name_tasks[chat.id] = {'task': task, 'prev': prev_title}
    await event.reply("✅ بدأ تحديث اسم القناة/الكروب تلقائياً كل دقيقة.")

@client.on(events.NewMessage(pattern=r"\.ايقاف اسم قناة (.+)"))
async def stop_temp_chat_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        await event.reply("❌ الرابط غير صالح.")
        return
    data = channel_name_tasks.pop(chat.id, None)
    if not data:
        await event.reply("❌ لا يوجد تحديث اسم مفعل على هذا القناة/الكروب.")
        return
    data['task'].cancel()
    await event.reply("🛑 تم إيقاف تحديث الاسم تلقائي.")

# ======== فحص حالة البوت ========
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def check_bot(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    msg = await event.edit("⌛ جارٍ الفحص...")
    end = datetime.datetime.now()
    await msg.edit(f"✅ البوت يعمل\nالزمن: {(end - start).microseconds // 1000}ms")
    await asyncio.sleep(10)
    await msg.delete()

# ======== كشف معلومات القروب/القناة ========
@client.on(events.NewMessage(pattern=r"\.كشف"))
async def show_info(event):
    if not await is_owner(event): return
    chat = await event.get_chat()
    try:
        if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
            full = await client(GetFullChannelRequest(chat))
            title = full.chats[0].title
            chat_id = full.chats[0].id
            members = full.full_chat.participants_count
            about = full.full_chat.about or "لا يوجد وصف"
        else:
            full = await client(GetFullChatRequest(chat))
            title = full.chats[0].title
            chat_id = full.chats[0].id
            members = len(full.full_chat.participants)
            about = full.full_chat.about or "لا يوجد وصف"
    except:
        title, chat_id, members, about = "❌", "❌", "❌", "❌"
    await event.reply(f"📊 معلومات:\n"
                      f"🔹 الاسم: {title}\n"
                      f"🔹 الايدي: `{chat_id}`\n"
                      f"🔹 عدد الأعضاء: {members}\n"
                      f"🔹 الوصف:\n{about}")

# ======== كتم وفك كتم وقائمة ومسح الكتم ========
@client.on(events.NewMessage(pattern=r"\.كتم$", func=lambda e: e.is_reply))
async def mute_user(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if event.is_private:
        muted_private.add(reply.sender_id)
    else:
        muted_groups.setdefault(event.chat_id, set()).add(reply.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute_user(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if event.is_private:
        muted_private.discard(reply.sender_id)
    else:
        muted_groups.get(event.chat_id, set()).discard(reply.sender_id)
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.قائمة الكتم$"))
async def show_muted(event):
    if not await is_owner(event): return
    text = "📋 قائمة المكتومين:\n"
    for uid in muted_private:
        try:
            user = await client.get_entity(uid)
            text += f"🔸 خاص: {user.first_name}\n"
        except:
            continue
    for chat_id, users in muted_groups.items():
        try:
            chat = await client.get_entity(chat_id)
            text += f"\n🔹 {chat.title}:\n"
            for uid in users:
                try:
                    user = await client.get_entity(uid)
                    text += f" - {user.first_name}\n"
                except:
                    continue
        except:
            continue
    await event.reply(text or "❌ لا يوجد مكتومين.")
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.مسح الكتم$"))
async def clear_muted(event):
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await event.delete()

# ======== حفظ الوسائط المؤقتة تلقائي ========
@client.on(events.NewMessage(incoming=True))
async def auto_save_temp_media(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()

    if event.media and getattr(event.media, 'ttl_seconds', None):
        path = await event.download_media("downloads/")
        await client.send_file("me", path, caption="📸 تم الحفظ مؤقتًا", ttl_seconds=event.media.ttl_seconds)
        if os.path.exists(path):
            os.remove(path)

    # تقليد تلقائي
    if imitate_active and not event.out and not event.sender.bot:
        if event.media:
            ttl = getattr(event.media, 'ttl_seconds', None)
            path = await event.download_media("downloads/")
            try:
                await client.send_file(event.chat_id, path, caption=event.text or "", ttl_seconds=ttl)
            finally:
                if os.path.exists(path): os.remove(path)
        elif event.text:
            await event.respond(event.text)

# ======== تقليد بالرد ========
@client.on(events.NewMessage(pattern=r"\.تقليد$", func=lambda e: e.is_reply))
async def imitate_once(event):
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

# ======== تفعيل / تعطيل التقليد التلقائي ========
@client.on(events.NewMessage(pattern=r"\.تقليد$"))
async def enable_imitation(event):
    global imitate_active
    if not await is_owner(event): return
    imitate_active = True
    await event.reply("✅ تم تفعيل التقليد التلقائي.")

@client.on(events.NewMessage(pattern=r"\.لاتقلده$"))
async def disable_imitation(event):
    global imitate_active
    if not await is_owner(event): return
    imitate_active = False
    await event.reply("🛑 تم إيقاف التقليد التلقائي.")

# ======== حفظ الوسائط بأسماء وإرسالها ========
@client.on(events.NewMessage(pattern=r"\.احفظ (.+)$", func=lambda e: e.is_reply))
async def save_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.reply("❌ الرجاء الرد على رسالة تحتوي على وسائط للحفظ.")
    path = await reply.download_media(f"saved_media/{name}")
    saved_media[name] = path
    await event.reply(f"✅ تم حفظ الوسائط باسم `{name}`.")

@client.on(events.NewMessage(pattern=r"\.(.+)$"))
async def send_saved_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    # تجاهل الأوامر المعروفة حتى لا تتعارض
    cmds = ['فحص','كشف','كتم','الغاء الكتم','قائمة الكتم','مسح الكتم','اسم مؤقت','ايقاف الاسم',
            'اسم قناة','ايقاف اسم قناة','تقليد','لاتقلده','احفظ','حذف','قائمة البصمات']
    if any(name.startswith(c) for c in cmds):
        return
    if name in saved_media:
        path = saved_media[name]
        if os.path.exists(path):
            await client.send_file(event.chat_id, path)
        else:
            await event.reply("❌ الملف المحفوظ غير موجود.")
    else:
        await event.reply("❌ لا يوجد وسائط محفوظة بهذا الاسم.")

@client.on(events.NewMessage(pattern=r"\.حذف (.+)$"))
async def delete_saved_media(event):
    if not await is_owner(event): return
    name = event.pattern_match.group(1).strip()
    if name in saved_media:
        path = saved_media.pop(name)
        if os.path.exists(path):
            os.remove(path)
        await event.reply(f"🗑️ تم حذف الوسائط المحفوظة باسم `{name}`.")
    else:
        await event.reply("❌ لا يوجد وسائط محفوظة بهذا الاسم.")

@client.on(events.NewMessage(pattern=r"\.قائمة البصمات$"))
async def list_saved_media(event):
    if not await is_owner(event): return
    if saved_media:
        text = "📋 قائمة البصمات المحفوظة:\n"
        for name in saved_media.keys():
            text += f" - {name}\n"
    else:
        text = "❌ لا توجد بصمات محفوظة."
    await event.reply(text)

# ======== قائمة الأوامر ========
@client.on(events.NewMessage(pattern=r"\.اوامر$"))
async def commands_list(event):
    if not await is_owner(event): return
    await event.respond(
        "🧠 أوامر البوت:\n\n"
        ".فحص - اختبار عمل البوت\n"
        ".كشف - كشف معلومات الكروب/القناة\n"
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
        ".<اسم> - إرسال الوسائط المحفوظة بالاسم\n"
        ".حذف <اسم> - حذف الوسائط المحفوظة باسم معين\n"
        ".قائمة البصمات - عرض جميع الوسائط المحفوظة\n"
    )

# ======== تشغيل البوت ========
async def main():
    await client.start()
    print("✅ البوت شغال وجاهز.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
