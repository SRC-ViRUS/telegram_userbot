# -*- coding: utf-8 -*-
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
session_string = "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHPHEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgKVts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEghyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ───── متغيرات عامة ─────
muted_private = set()
muted_groups = {}
saved_media = {}
imitate_user_id = None
last_imitated_message_id = None
channel_name_tasks = {}
change_name_task = None
previous_name = None
welcome_config = {}  # {chat_id: {"enabled": bool, "text": str}}

# ───── لمنع تكرار تنفيذ نفس الأمر بنفس المستخدم ─────
last_commands = {}

def is_spamming(user_id, command, delay=1.5):
    now = datetime.datetime.now().timestamp()
    key = f"{user_id}:{command}"
    last = last_commands.get(key, 0)
    if now - last < delay:
        return True
    last_commands[key] = now
    return False

# ───── توقيت بغداد ─────
def now_baghdad(fmt="%I:%M"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

# ───── تحقق من المالك ─────
async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

# ───── تنظيف الجلسة ─────
async def cleanup():
    global change_name_task, channel_name_tasks, saved_media
    if change_name_task and not change_name_task.done():
        change_name_task.cancel()
    for cid, task in list(channel_name_tasks.items()):
        task["task"].cancel()
        if task.get("prev"):
            try:
                await client(EditTitleRequest(cid, task["prev"]))
            except:
                pass
    channel_name_tasks.clear()
    for path in saved_media.values():
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    saved_media.clear()
    for f in os.listdir("downloads"):
        try:
            os.remove(os.path.join("downloads", f))
        except:
            pass

# ───── الاسم المؤقت للحساب ─────
async def loop_name():
    global previous_name
    previous_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=now_baghdad()))
        except:
            pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_name(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".اسم مؤقت"):
        return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await event.reply("✅ مفعل مسبقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await event.reply("🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_name(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".ايقاف الاسم"):
        return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try:
            await client(UpdateProfileRequest(first_name=previous_name))
        except:
            pass
    await event.reply("🛑 تم إيقاف الاسم المؤقت.")

# ───── اسم قناة مؤقت ─────
@client.on(events.NewMessage(pattern=r"^\.اسم قناة (.+)$"))
async def start_channel_name(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".اسم قناة"):
        return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        return await event.reply("❌ رابط غير صالح.")
    cid = chat.id
    if cid in channel_name_tasks:
        return await event.reply("🔄 مفعل مسبقًا.")
    prev = chat.title

    async def update_loop():
        while True:
            try:
                await client(EditTitleRequest(cid, now_baghdad()))
                msgs = await client.get_messages(cid, limit=1)
                if msgs and not msgs[0].message:
                    await msgs[0].delete()
            except ChatAdminRequiredError:
                break
            except:
                pass
            await asyncio.sleep(60)

    task = asyncio.create_task(update_loop())
    channel_name_tasks[cid] = {"task": task, "prev": prev}
    await event.reply("🕒 تم تفعيل الاسم المؤقت للقناة.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_name(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".ايقاف اسم قناة"):
        return
    link = event.pattern_match.group(1).strip()
    try:
        chat = await client.get_entity(link)
    except:
        return await event.reply("❌ رابط غير صالح.")
    data = channel_name_tasks.pop(chat.id, None)
    if data:
        data["task"].cancel()
        if data["prev"]:
            try:
                await client(EditTitleRequest(chat.id, data["prev"]))
            except:
                pass
        await event.reply("🛑 تم إيقاف الاسم المؤقت للقناة.")
    else:
        await event.reply("❌ لا يوجد تعديل نشط.")

# ───── كتم / فك كتم ─────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".كتم"):
        return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await event.reply("🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".الغاء الكتم"):
        return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await event.reply("🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".قائمة الكتم"):
        return
    txt = "📋 المكتومون:\n"
    for u in muted_private:
        txt += f"• خاص: {u}\n"
    for cid, users in muted_groups.items():
        txt += f"\n• جروب {cid}:\n" + "\n".join(f"  - {u}" for u in users)
    await event.reply(txt or "❌ لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def mute_clear(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".مسح الكتم"):
        return
    muted_private.clear()
    muted_groups.clear()
    await event.reply("🗑️ تم المسح.")

# ───── تقليد ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate(event):
    if not await is_owner(event):
        return
    if is_spamming(event.sender_id, ".تقليد"):
        return
    global imitate_user_id, last_imitated_message_id
    r = await event.get_reply_message()
    imitate_user_id = r.sender_id
    last_imitated_message_id = None
    msg = await event.edit("
