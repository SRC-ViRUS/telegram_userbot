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

client = TelegramClient(StringSession(session_string), api_id, api_hash, system_version="TelegramBot (الصعب) 1.0")
os.makedirs("downloads", exist_ok=True)

# ───── متغيرات عامة ─────
muted_private = set()
muted_groups = {}
taqleed_dict = {}                 # {sender_id: (chat_id, msg_id)}
last_imitated_ids = {}            # {sender_id: last_msg_id_seen}
channel_name_tasks = {}           # {channel_id: dict(task, prev, entity)}
change_name_task = None
previous_name = None
last_commands = {}                # منع سبام
welcome_config = {}               # {chat_id: {enabled, message}}

# ───── دوال مساعدة ─────
def now_baghdad(fmt="%I:%M %p"):
    """توقيت بغداد بصيغة 12 ساعة."""
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

def is_spamming(user_id, cmd, delay=1.5):
    now = datetime.datetime.now().timestamp()
    key = f"{user_id}:{cmd}"
    if now - last_commands.get(key, 0) < delay:
        return True
    last_commands[key] = now
    return False

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def quick_edit(event, text, delay=1):
    await event.edit(text)
    await asyncio.sleep(delay)
    await event.delete()

# ───── الاسم المؤقت للحساب (كل 60 ثانية) ─────
async def loop_name():
    global previous_name
    previous_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=now_baghdad()))
        except Exception:
            pass
        await asyncio.sleep(60)          # تعديل كل دقيقة

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_temp_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await quick_edit(event, "✅ الاسم المؤقت مفعّل سابقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_temp_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
        except Exception:
            pass
    await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت.")

# ───── الاسم المؤقت للقنوات ─────
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def start_channel_title(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except Exception:
        return await quick_edit(event, "❌ رابط غير صالح.")

    if channel.id in channel_name_tasks:
        return await quick_edit(event, "🔄 الاسم المؤقت مفعّل مسبقًا.")

    prev_title = channel.title

    async def updater():
        while True:
            try:
                await client(EditTitleRequest(channel, now_baghdad()))
            except ChatAdminRequiredError:
                break
            except Exception:
                pass
            await asyncio.sleep(60)

    task = asyncio.create_task(updater())
    channel_name_tasks[channel.id] = {"task": task, "prev": prev_title, "entity": channel}
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت للقناة.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_title(event):
    if not await is_owner(event): return
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
        except Exception:
            pass
        await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت للقناة.")
    else:
        await quick_edit(event, "❌ لا يوجد تعديل نشط لهذه القناة.")

# ───── كتم / فك كتم ─────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def cmd_mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await quick_edit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def cmd_unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await quick_edit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def cmd_mute_list(event):
    if not await is_owner(event): return
    out = []
    if muted_private:
        out.append("• خاص:")
        out.extend(f"  - {u}" for u in muted_private)
    for cid, users in muted_groups.items():
        if users:
            out.append(f"\n• جروب {cid}:")
            out.extend(f"  - {u}" for u in users)
    await quick_edit(event, "\n".join(out) if out else "❌ لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def cmd_clear_mutes(event):
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await quick_edit(event, "🗑️ تم مسح جميع المكتومين.")

@client.on(events.NewMessage(incoming=True))
async def auto_delete_mutes(event):
    if event.is_private and event.sender_id in muted_private:
        return await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]:
        return await event.delete()

# ───── التقليد (حفظ & إعادة إرسال كامل) ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def cmd_save_taqleed(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if not reply:
        return await quick_edit(event, "❗ ردّ على رسالة لحفظها.")
    # حفظ (chat_id, msg_id) لسهولة النقل
    taqleed_dict[reply.sender_id] = (reply.chat_id, reply.id)

    if event.is_private:
        await quick_edit(event, "✅ تم حفظ التقليد الكامل (خاص).")
    else:
        await quick_edit(event, "✅ تم حفظ التقليد (نص/ملف مسموع/ملصق) في القروب.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def cmd_stop_taqleed(event):
    if not await is_owner(event): return
    taqleed_dict.clear()
    last_imitated_ids.clear()
    await quick_edit(event, "🛑 تم إيقاف التقليد.")

@client.on(events.NewMessage(incoming=True))
async def auto_taqleed(event):
    """يرسل نفس الرسالة التي حفظناها كلما تكلّم الشخص المستهدف."""
    if event.sender_id not in taqleed_dict:
        return

    src_chat, src_msg_id = taqleed_dict[event.sender_id]

    # منع حلقة تقليد
    if last_imitated_ids.get(event.sender_id) == event.id:
        return
    last_imitated_ids[event.sender_id] = event.id

    try:
        if event.is_private:
            # للخاص نرسل إلى الخاص
            await client.forward_messages(event.sender_id, src_msg_id, src_chat)
        elif event.is_group:
            await client.forward_messages(event.chat_id, src_msg_id, src_chat)
    except Exception:
        pass

# ───── حفظ الوسائط والبصمات الموقّتة تلقائيًا إلى الحافظة ─────
@client.on(events.NewMessage(incoming=True))
async def save_self_destruct_media(event):
    """
    يحفظ أي وسائط ذات مؤقت (TTL) — صور، فيديو، ملفات، بصمات... —
    إلى Saved Messages مع ذكر المرسل.
    """
    if not event.media:
        return
    ttl = getattr(event.media, "ttl_seconds", 0)
    if not ttl:                       # ليست وسائط مؤقّتة
        return

    # اسم/معرّف المرسل
    try:
        sender = await event.get_sender()
        sender_name = f"@{sender.username}" if sender.username else f"ID:{sender.id}"
    except Exception:
        sender_name = f"ID:{event.sender_id}"

    caption = f"📥 وسائط مؤقّتة من: {sender_name}"
    try:
        await client.send_message("me", event.message, caption=caption)
    except Exception as e:
        print(f"[!] خطأ بحفظ الوسائط المؤقتة: {e}")

# ───── الترحيب التلقائي ─────
@client.on(events.ChatAction)
async def welcome_user(event):
    if not (event.user_joined or event.user_added):
        return
    cfg = welcome_config.get(event.chat_id)
    if not (cfg and cfg.get("enabled")):
        return
    user = await event.get_user()
    msg = cfg.get("message", "أهلاً {الاسم} 🌸").replace("{الاسم}", user.first_name)
    await client.send_message(event.chat_id, msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def cmd_enable_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": True, "message": "أهلاً {الاسم} 🌸"}
    await quick_edit(event, "✅ تم تفعيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def cmd_disable_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": False}
    await quick_edit(event, "🛑 تم تعطيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def cmd_set_welcome(event):
    if not await is_owner(event): return
    txt = event.pattern_match.group(1)
    welcome_config[event.chat_id] = {"enabled": True, "message": txt}
    await quick_edit(event, "📨 تم تحديث رسالة الترحيب.")

# ───── كشف معلومات المجموعة ─────
@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def cmd_chat_info(event):
    if not await is_owner(event): return
    if not event.is_group:
        return await quick_edit(event, "❌ هذا الأمر للمجموعات فقط.")
    info = await event.get_chat()
    txt = f"""🏷️ العنوان: {info.title}
🆔 المعرّف: {info.id}
👥 الأعضاء: {getattr(info, 'participants_count', 'غير معروف')}
📛 @: {getattr(info, 'username', 'لا يوجد')}
"""
    await quick_edit(event, txt, delay=10)

# ───── فحص البوت ─────
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def cmd_check(event):
    if not await is_owner(event): return
    await event.edit("⚡ جاري الفحص...")
    await asyncio.sleep(1)
    await event.edit("✅ البوت شغّال ✔️")
    await asyncio.sleep(8)
    await event.delete()

# ───── قائمة الأوامر ─────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmd_show_commands(event):
    if not await is_owner(event): return
    cmds = """
📜 قائمة الأوامر:

👤 الاسم:
  .اسم مؤقت | .ايقاف الاسم

📢 القناة:
  .اسم قناة <رابط> | .ايقاف اسم قناة <رابط>

🔇 الكتم:
  .كتم (بالرد) | .الغاء الكتم (بالرد)
  .قائمة الكتم | .مسح الكتم

🌀 التقليد:
  .تقليد (بالرد) | .ايقاف التقليد

🌸 الترحيب:
  .تفعيل الترحيب | .تعطيل الترحيب
  .وضع ترحيب <رسالة>

🎞️ الحفظ التلقائي:
  يتم حفظ كل الوسائط المؤقّتة إلى الحافظة تلقائيًا.

🕵️ أخرى:
  .كشف | .فحص | .الاوامر
"""
    await quick_edit(event, cmds, delay=12)

# ───── إعلام بالبدء ─────
async def notify_start():
    try:
        me = await client.get_me()
        await client.send_message("me", f"✅ البوت يعمل — @{me.username or me.first_name}")
    except Exception:
        pass

print("✅ Bot Loaded — المطور: الصعب")
client.start()
client.loop.run_until_complete(notify_start())
client.run_until_disconnected()
