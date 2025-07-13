# -*- coding: utf-8 -*-
import asyncio
import os
import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest, EditTitleRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, ChatWriteForbiddenError

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
saved_media = {}  # حفظ الوسائط باسم: {'name': path}
imitate_targets = set()  # الأشخاص الذين فعّلنا عليهم التقليد

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

# تغيير الاسم الشخصي تلقائياً كل 60 ثانية
async def change_name_periodically():
    global previous_name
    me = await client.get_me()
    previous_name = me.first_name
    while True:
        name = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M')
        try:
            await client(UpdateProfileRequest(first_name=name))
        except Exception as e:
            print(f"خطأ في تغيير الاسم: {e}")
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_changing_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await event.reply("🔄 تغيير الاسم التلقائي مفعل مسبقًا.")
    change_name_task = asyncio.create_task(change_name_periodically())
    await event.reply("✅ بدأ تغيير الاسم التلقائي كل دقيقة.")

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

# اسم قناة/كروب مؤقت يتغير كل 60 ثانية (يحذف إشعار تغيير الاسم)
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

    async def updater():
        try:
            while True:
                title = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%I:%M')
                try:
                    await client(EditTitleRequest(channel=cid, title=title))
                    msgs = await client.get_messages(chat, limit=1)
                    if msgs and msgs[0].message is None:
                        await msgs[0].delete()
                except ChatAdminRequiredError:
                    await event.respond("🚫 لا أملك صلاحية تغيير الاسم في القناة/الكروب.")
                    break
                except ChatWriteForbiddenError:
                    await event.respond("🚫 لا أملك صلاحية الكتابة في القناة/الكروب.")
                    break
                except Exception as e:
                    await event.respond(f"❌ خطأ أثناء تغيير الاسم: {e}")
                    break
                await asyncio.sleep(60)
        finally:
            if prev_title:
                try:
                    await client(EditTitleRequest(channel=cid, title=prev_title))
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
            await client(EditTitleRequest(channel=chat.id, title=data['prev']))
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
