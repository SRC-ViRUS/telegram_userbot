# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل بقوة ومميزات عديدة
المطور: الصعب
حقوق النشر: © 2025 الصعب. كل الحقوق محفوظة.
"""

import os
import asyncio
import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# ───── بيانات الاتصال ─────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = (
    "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2"
    "kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHP"
    "HEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu"
    "3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgK"
    "Vts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEg"
    "hyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="
)

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ───── متغيرات عامة ─────
muted_private = set()
muted_groups = {}
imitate_user_ids = set()  # دعم تقليد أكثر من شخص
last_imitated_message_ids = {}  # لتتبع آخر رسالة مقلدة لكل مستخدم
channel_name_tasks = {}
change_name_task = None
previous_name = None
last_commands = {}
welcome_config = {}  # {chat_id: {"enabled": bool, "message": str}}

me = None  # لحفظ معلومات المستخدم صاحب الجلسة

# ───── دوال مساعدة ─────
def is_spamming(user_id, command, delay=1.5):
    now = datetime.datetime.now().timestamp()
    key = f"{user_id}:{command}"
    if now - last_commands.get(key, 0) < delay:
        return True
    last_commands[key] = now
    return False

def now_baghdad(fmt="%I:%M %p"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    global me
    if me is None:
        me = await client.get_me()
    return event.sender_id == me.id

async def quick_edit(event, text, delay=3):
    await event.edit(text)
    await asyncio.sleep(delay)
    # لحين التأكد من عمل الأوامر، علق السطر التالي
    await event.delete()

# ───── الاسم المؤقت للحساب ─────
async def loop_name():
    global previous_name
    previous_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=now_baghdad()))
        except Exception as e:
            print(f"خطأ بتحديث الاسم: {e}")
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_name(event):
    print("تم استدعاء أمر .اسم مؤقت")
    if not await is_owner(event) or is_spamming(event.sender_id, ".اسم مؤقت"):
        return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await quick_edit(event, "✅ الاسم المؤقت مفعّل مسبقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_name(event):
    print("تم استدعاء أمر .ايقاف الاسم")
    if not await is_owner(event) or is_spamming(event.sender_id, ".ايقاف الاسم"):
        return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
        except Exception as e:
            print(f"خطأ بإرجاع الاسم السابق: {e}")
    await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت.")

# ───── الاسم المؤقت للقنوات ─────
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def start_channel_name(event):
    print("تم استدعاء أمر .اسم قناة")
    if not await is_owner(event) or is_spamming(event.sender_id, ".اسم قناة"):
        return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except Exception:
        return await quick_edit(event, "❌ رابط غير صالح.")
    if channel.id in channel_name_tasks:
        return await quick_edit(event, "🔄 الاسم المؤقت للقناة مفعّل مسبقًا.")
    prev_title = channel.title

    async def update_loop():
        while True:
            try:
                await client(EditTitleRequest(channel, now_baghdad()))
            except ChatAdminRequiredError:
                print("لا توجد صلاحيات تعديل اسم القناة")
                break
            except Exception as e:
                print(f"خطأ أثناء تعديل اسم القناة: {e}")
            await asyncio.sleep(60)

    task = asyncio.create_task(update_loop())
    channel_name_tasks[channel.id] = {"task": task, "prev": prev_title, "entity": channel}
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت للقناة.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_name(event):
    print("تم استدعاء أمر .ايقاف اسم قناة")
    if not await is_owner(event) or is_spamming(event.sender_id, ".ايقاف اسم قناة"):
        return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except Exception:
        return await quick_edit(event, "❌ رابط غير صالح.")
    data = channel_name_tasks.pop(channel.id, None)
    if data:
        data["task"].cancel()
        try:
            await client(EditTitleRequest(data["entity"], data["prev"]))
        except Exception as e:
            print(f"خطأ بإرجاع اسم القناة السابق: {e}")
        await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت للقناة.")
    else:
        await quick_edit(event, "❌ لا يوجد تعديل نشط لهذه القناة.")

# ───── كتم / فك كتم ─────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    print("تم استدعاء أمر .كتم")
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await quick_edit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    print("تم استدعاء أمر .الغاء الكتم")
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await quick_edit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    print("تم استدعاء أمر .قائمة الكتم")
    if not await is_owner(event): return
    lines = []
    if muted_private:
        lines.append("• خاص:")
        lines.extend(f"  - {u}" for u in muted_private)
    for cid, users in muted_groups.items():
        if users:
            lines.append(f"\n• جروب {cid}:")
            lines.extend(f"  - {u}" for u in users)
    await quick_edit(event, "\n".join(lines) if lines else "❌ لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def mute_clear(event):
    print("تم استدعاء أمر .مسح الكتم")
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await quick_edit(event, "🗑️ تم مسح جميع المكتومين.")

@client.on(events.NewMessage(incoming=True))
async def auto_delete_muted(event):
    if event.is_private and event.sender_id in muted_private:
        await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]:
        await event.delete()

# ───── التقليد الذكي (يدعم تقليد أكثر من شخص بكل الوسائط) ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate(event):
    print("تم استدعاء أمر .تقليد")
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    imitate_user_ids.add(reply.sender_id)
    await quick_edit(event, f"🔁 جاري تقليد المستخدم {reply.sender_id} (عدد المقلدين: {len(imitate_user_ids)})")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def stop_imitate(event):
    print("تم استدعاء أمر .ايقاف التقليد")
    if not await is_owner(event): return
    imitate_user_ids.clear()
    await quick_edit(event, "🛑 تم إيقاف التقليد لجميع المستخدمين.")

@client.on(events.NewMessage(incoming=True))
async def imitate_user(event):
    if event.sender_id not in imitate_user_ids:
        return
    last_id = last_imitated_message_ids.get(event.sender_id)
    if event.id == last_id:
        return
    last_imitated_message_ids[event.sender_id] = event.id
    try:
        if event.media:
            await event.reply(file=event.media, message=event.raw_text or None)
        else:
            await event.reply(event.raw_text or "")
    except Exception as e:
        print(f"خطأ بالتقليد: {e}")

# ───── ترحيب تلقائي ─────
@client.on(events.ChatAction)
async def welcome_new_user(event):
    if not event.user_joined and not event.user_added:
        return
    chat_id = event.chat_id
    config = welcome_config.get(chat_id)
    if config and config.get("enabled", False):
        user = await event.get_user()
        msg = config.get("message", "اهلا {الاسم} 🌸").replace("{الاسم}", user.first_name)
        await client.send_message(chat_id, msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def enable_welcome(event):
    print("تم استدعاء أمر .تفعيل الترحيب")
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": True, "message": "اهلا {الاسم} 🌸"}
    await quick_edit(event, "✅ تم تفعيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def disable_welcome(event):
    print("تم استدعاء أمر .تعطيل الترحيب")
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": False}
    await quick_edit(event, "🛑 تم تعطيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def set_welcome(event):
    print("تم استدعاء أمر .وضع ترحيب")
    if not await is_owner(event): return
    txt = event.pattern_match.group(1)
    welcome_config[event.chat_id] = {"enabled": True, "message": txt}
    await quick_edit(event, "📩 تم تحديث رسالة الترحيب.")

# ───── حفظ الوسائط المؤقتة من الخاص (شامل كل الوسائط والبصمات) ─────
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.media))
async def save_media(event):
    name = os.path.join("downloads", f"{event.id}")
    try:
        path = await event.download_media(file=name)
        print(f"📥 تم حفظ الوسائط: {path}")
    except Exception as e:
        print(f"❌ خطأ بحفظ الوسائط: {e}")

# ───── كشف معلومات المجموعة ─────
@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def group_info(event):
    print("تم استدعاء أمر .كشف")
    if not await is_owner(event): return
    if not event.is_group:
        return await quick_edit(event, "❌ هذا الأمر فقط للمجموعات.")
    info = await event.get_chat()
    msg = f"""
🏷️ العنوان: {info.title}
🆔 المعرف: {info.id}
👥 الأعضاء: {getattr(info, 'participants_count', 'غير معروف')}
📛 اسم المستخدم: @{getattr(info, 'username', 'لا يوجد')}
"""
    await quick_edit(event, msg.strip(), delay=10)

# ───── أمر فحص ─────
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check_status(event):
    print("تم استدعاء أمر .فحص")
    if not await is_owner(event): return
    await event.edit("⚡ جاري الفحص...")
    await asyncio.sleep(2)
    await event.edit("✅ البوت شغال تمام 💯")
    await asyncio.sleep(10)
    await event.delete()

# ───── قائمة الأوامر (مطوّرة - خرافية وجذابة) ─────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def show_commands(event):
    print("تم استدعاء أمر .الاوامر")
    if not await is_owner(event): return
    cmds = """
╔══════════════════════╗
║ 🛸 𝗔𝗹𝘀𝗮𝗯𝗮𝗯 𝗕𝗼𝘁 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 🛸 ║
╚══════════════════════╝

👤 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 Commands:
  • .اسم مؤقت      ➤ تفعيل تغيير الاسم المؤقت كل دقيقة
  • .ايقاف الاسم    ➤ إيقاف تغيير الاسم المؤقت

📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 Commands:
  • .اسم قناة <رابط>
