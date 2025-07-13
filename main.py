# -*- coding: utf-8 -*-
import os, asyncio, datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# ───── بيانات الاتصال ─────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = ("1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2"
                  "kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHP"
                  "HEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu"
                  "3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgK"
                  "Vts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEg"
                  "hyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY=")

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ───── متغيرات عامة ─────
muted_private = set()
muted_groups = {}
imitate_user_id, last_imitated_message_id = None, None
channel_name_tasks, change_name_task, previous_name = {}, None, None
welcome_config, last_commands = {}, {}

# ───── دوال مساعدة ─────
def is_spamming(user_id, command, delay=1.5):
    now = datetime.datetime.now().timestamp()
    key = f"{user_id}:{command}"
    if now - last_commands.get(key, 0) < delay:
        return True
    last_commands[key] = now
    return False

def now_baghdad(fmt="%I:%M"):
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
        except Exception:
            pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_name(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".اسم مؤقت"):
        return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await quick_edit(event, "✅ مفعّل مسبقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_name(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".ايقاف الاسم"):
        return
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
async def start_channel_name(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".اسم قناة"):
        return
    link = event.pattern_match.group(1).strip()
    try:
        channel = await client.get_entity(link)
    except Exception:
        return await quick_edit(event, "❌ رابط غير صالح.")
    if channel.id in channel_name_tasks:
        return await quick_edit(event, "🔄 مفعّل مسبقًا.")
    prev_title = channel.title

    async def update_loop():
        while True:
            try:
                await client(EditTitleRequest(channel, now_baghdad()))
            except ChatAdminRequiredError:
                break
            except Exception:
                pass
            await asyncio.sleep(60)

    task = asyncio.create_task(update_loop())
    channel_name_tasks[channel.id] = {"task": task, "prev": prev_title, "entity": channel}
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت للقناة.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم قناة (.+)$"))
async def stop_channel_name(event):
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
        except Exception:
            pass
        await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت للقناة.")
    else:
        await quick_edit(event, "❌ لا يوجد تعديل نشط لهذه القناة.")

# ───── كتم / فك كتم ─────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def mute(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".كتم"):
        return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await quick_edit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".الغاء الكتم"):
        return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await quick_edit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".قائمة الكتم"):
        return
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
    if not await is_owner(event) or is_spamming(event.sender_id, ".مسح الكتم"):
        return
    muted_private.clear()
    muted_groups.clear()
    await quick_edit(event, "🗑️ تم مسح جميع المكتومين.")

@client.on(events.NewMessage(incoming=True))
async def auto_delete_muted(event):
    if event.is_private and event.sender_id in muted_private:
        return await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]:
        return await event.delete()

# ───── تقليد ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".تقليد"):
        return
    global imitate_user_id, last_imitated_message_id
    r = await event.get_reply_message()
    imitate_user_id, last_imitated_message_id = r.sender_id, None
    await quick_edit(event, "✅ تم تفعيل التقليد.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def stop_imitate(event):
    if not await is_owner(event):
        return
    global imitate_user_id, last_imitated_message_id
    imitate_user_id, last_imitated_message_id = None, None
    await quick_edit(event, "🛑 تم إيقاف التقليد.")

@client.on(events.NewMessage(incoming=True))
async def do_imitate(event):
    global imitate_user_id, last_imitated_message_id
    if (imitate_user_id is None or event.sender_id != imitate_user_id
            or event.id == last_imitated_message_id or event.out or event.via_bot_id):
        return
    try:
        await event.reply(event.raw_text)
        last_imitated_message_id = event.id
    except Exception:
        pass

# ───── أمر فحص السّرعة ─────
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def ping_handler(event):
    if not await is_owner(event) or is_spamming(event.sender_id, ".فحص"):
        return
    start = datetime.datetime.now()
    await event.edit("⏱️ جاري الفحص ...")
    duration = (datetime.datetime.now() - start).total_seconds()
    await event.edit(f"✅ البوت يعمل خلال `{duration:.2f}` ثانية.")
    await asyncio.sleep(10)
    await event.delete()

# ───── تشغيل البوت ─────
print("✅ تم تشغيل البوت بنجاح.")
client.start()
client.run_until_disconnected()
