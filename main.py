# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل بقوة ومميزات عديدة
المطور: الصعب
حقوق النشر: © 2025 الصعب. كل الحقوق محفوظة.
"""

import os
import asyncio
import datetime
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# ───── بيانات الاتصال ─────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = "ضع_سلسلة_الجلسة_هنا"

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ───── متغيرات عامة ─────
muted_private = set()
muted_groups = {}
taqleed_dict = {}
last_imitated_ids = {}
channel_name_tasks = {}
change_name_task = None
previous_name = None
last_commands = {}
welcome_config = {}

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
    me = await client.get_me()
    return event.sender_id == me.id

async def quick_edit(event, text, delay=1):
    await event.edit(text)
    await asyncio.sleep(delay)
    await event.delete()

# ───── الاسم المؤقت للحساب ─────
async def loop_name():
    global previous_name
    previous_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=now_baghdad()))
        except: pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await quick_edit(event, "✅ الاسم المؤقت مفعّل مسبقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
        except: pass
    await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت.")

# ───── الاسم المؤقت للقنوات ─────
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def start_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except:
        return await quick_edit(event, "❌ رابط غير صالح.")
    if channel.id in channel_name_tasks:
        return await quick_edit(event, "🔄 الاسم المؤقت للقناة مفعّل مسبقًا.")
    prev_title = channel.title

    async def update_loop():
        while True:
            try:
                await client(EditTitleRequest(channel, now_baghdad()))
            except ChatAdminRequiredError:
                break
            except: pass
            await asyncio.sleep(60)

    task = asyncio.create_task(update_loop())
    channel_name_tasks[channel.id] = {"task": task, "prev": prev_title, "entity": channel}
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت للقناة.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_name(event):
    if not await is_owner(event): return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except:
        return await quick_edit(event, "❌ رابط غير صالح.")
    data = channel_name_tasks.pop(channel.id, None)
    if data:
        data["task"].cancel()
        try:
            await client(EditTitleRequest(data["entity"], data["prev"]))
        except: pass
        await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت للقناة.")
    else:
        await quick_edit(event, "❌ لا يوجد تعديل نشط لهذه القناة.")

# ───── كتم / فك كتم ─────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await quick_edit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await quick_edit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
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
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await quick_edit(event, "🗑️ تم مسح جميع المكتومين.")

@client.on(events.NewMessage(incoming=True))
async def auto_delete_muted(event):
    if event.is_private and event.sender_id in muted_private:
        return await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]:
        return await event.delete()

# ───── التقليد (خاص وقروب) ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def cmd_save_taqleed(event):
    if not await is_owner(event): return
    reply = await event.get_reply_message()
    if not reply: return await quick_edit(event, "❗ ردّ على رسالة لتقليدها.")
    taqleed_dict[reply.sender_id] = reply
    await quick_edit(event, "✅ تم حفظ التقليد.")

@client.on(events.NewMessage(incoming=True))
async def auto_taqleed(event):
    if event.sender_id not in taqleed_dict:
        return
    saved_msg = taqleed_dict[event.sender_id]
    if last_imitated_ids.get(event.sender_id) == event.id:
        return
    last_imitated_ids[event.sender_id] = event.id
    try:
        if event.is_private:
            await client.send_message(event.sender_id, saved_msg)
        elif event.is_group:
            if saved_msg.text or saved_msg.voice or saved_msg.sticker:
                await event.reply(saved_msg)
    except: pass

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def stop_taqleed(event):
    if not await is_owner(event): return
    taqleed_dict.clear()
    last_imitated_ids.clear()
    await quick_edit(event, "🛑 تم إيقاف التقليد.")

# ───── حفظ الوسائط المؤقتة تلقائيًا ─────
@client.on(events.NewMessage(incoming=True))
async def save_self_destruct_media(event):
    if not event.media:
        return
    ttl = getattr(event.media, "ttl_seconds", 0)
    if ttl <= 0:
        return
    try:
        sender = await event.get_sender()
        sender_name = f"@{sender.username}" if sender.username else f"ID:{sender.id}"
    except:
        sender_name = f"ID:{event.sender_id}"
    caption = f"📥 وسائط موقّتة من: {sender_name}"
    try:
        await client.send_message("me", event.message, caption=caption)
    except Exception as e:
        print(f"[!] فشل حفظ الوسائط: {e}")

# ───── الترحيب التلقائي ─────
@client.on(events.ChatAction)
async def welcome_new_user(event):
    if not (event.user_joined or event.user_added):
        return
    chat_id = event.chat_id
    config = welcome_config.get(chat_id)
    if config and config.get("enabled", False):
        user = await event.get_user()
        msg = config.get("message", "اهلا {الاسم} 🌸").replace("{الاسم}", user.first_name)
        await client.send_message(chat_id, msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def enable_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": True, "message": "اهلا {الاسم} 🌸"}
    await quick_edit(event, "✅ تم تفعيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def disable_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id] = {"enabled": False}
    await quick_edit(event, "🛑 تم تعطيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def set_welcome(event):
    if not await is_owner(event): return
    txt = event.pattern_match.group(1)
    welcome_config[event.chat_id] = {"enabled": True, "message": txt}
    await quick_edit(event, "📩 تم تحديث رسالة الترحيب.")

# ───── فحص، كشف، أوامر ─────
@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def group_info(event):
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

@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check_status(event):
    if not await is_owner(event): return
    await event.edit("⚡ جاري الفحص...")
    await asyncio.sleep(2)
    await event.edit("✅ البوت شغال تمام 💯")
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def show_commands(event):
    if not await is_owner(event): return
    cmds = """
🎛️ الأوامر:

👤 الاسم:
.اسم مؤقت | .ايقاف الاسم

📢 القناة:
.اسم قناة <رابط> | .ايقاف اسم قناة <رابط>

🔇 الكتم:
.كتم (رد) | .الغاء الكتم (رد)
.قائمة الكتم | .مسح الكتم

🌀 التقليد:
.تقليد (رد) | .ايقاف التقليد

🌸 الترحيب:
.تفعيل الترحيب | .تعطيل الترحيب
.وضع ترحيب <رسالة>

🕵️ أخرى:
.كشف | .فحص | .الاوامر
"""
    await quick_edit(event, cmds, delay=12)

# ───── بدء التشغيل ─────
async def notify_on_start():
    try:
        me = await client.get_me()
        await client.send_message("me", f"✅ البوت شغال استاذ صعب، الحساب: @{me.username or me.first_name}")
    except: pass

print("✅ تم تشغيل البوت بنجاح - المطور: الصعب")
client.start()
client.loop.run_until_complete(notify_on_start())
client.run_until_disconnected()
