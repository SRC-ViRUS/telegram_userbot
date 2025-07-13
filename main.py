# -*- coding: utf-8 -*-
import os, asyncio, datetime, time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import EditTitleRequest
from telethon.errors import ChatAdminRequiredError

# ───── بيانات الاتصال ─────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = (
    "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2kyID0DGo-ZZV"
    "tB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHPHEBiWrEDiHqO01g1zY4t_Kf7dA"
    "-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8w"
    "xoMdQlr8tAGBySMM_EPkUXSgKVts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mU"
    "ypaJ5OnO-aEghyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="
)

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

# ───── توقيت بغداد ─────
def now_baghdad(fmt="%I:%M"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

# ───── حماية صارمة: تحقق من المالك مع Debounce لمنع السبام ─────
_owner_id = None
_last_command_time = {}

async def get_owner_id():
    global _owner_id
    if _owner_id is None:
        me = await client.get_me()
        _owner_id = me.id
    return _owner_id

async def is_owner(event):
    owner_id = await get_owner_id()
    if event.sender_id != owner_id:
        return False
    # حماية Debounce: عدم قبول نفس الأمر خلال 1 ثانية لكل مستخدم
    cmd = event.pattern.pattern if hasattr(event.pattern, 'pattern') else str(event.raw_text)
    now = time.time()
    key = (event.sender_id, cmd)
    last = _last_command_time.get(key, 0)
    if now - last < 1:  # تأخير 1 ثانية
        return False
    _last_command_time[key] = now
    return True

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
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await event.reply("✅ مفعل مسبقًا.")
    change_name_task = asyncio.create_task(loop_name())
    await event.reply("🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_name(event):
    if not await is_owner(event):
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
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(
        r.sender_id
    )
    await event.reply("🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute(event):
    if not await is_owner(event):
        return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(
        r.sender_id
    )
    await event.reply("🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def mute_list(event):
    if not await is_owner(event):
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
    muted_private.clear()
    muted_groups.clear()
    await event.reply("🗑️ تم المسح.")

# ───── تفعيل التقليد ─────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e: e.is_reply))
async def imitate(event):
    if not await is_owner(event):
        return
    global imitate_user_id, last_imitated_message_id
    r = await event.get_reply_message()
    imitate_user_id = r.sender_id
    last_imitated_message_id = None
    msg = await event.edit("✅ تم تفعيل التقليد")
    await asyncio.sleep(1)
    await msg.delete()

# ───── إيقاف التقليد ─────
@client.on(events.NewMessage(pattern=r"^\.لاتقلده$"))
async def stop_imitate(event):
    if not await is_owner(event):
        return
    global imitate_user_id
    imitate_user_id = None
    msg = await event.edit("🛑 تم إيقاف التقليد")
    await asyncio.sleep(1)
    await msg.delete()

# ───── تقليد الرسائل ─────
@client.on(events.NewMessage(incoming=True))
async def imitate_user(event):
    global imitate_user_id, last_imitated_message_id

    # حذف رسائل المكتومين
    if (event.is_private and event.sender_id in muted_private) or (
        event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]
    ):
        try:
            await event.delete()
        except:
            pass
        return

    # تحقق من الشخص المقلَّد
    if not imitate_user_id or event.sender_id != imitate_user_id:
        return

    # في المجموعات فقط، التقليد يكون فقط للردود
    if event.is_group or event.is_channel:
        if not event.is_reply:
            return  # إذا ما رد على رسالة، ما يقلد

    # منع تكرار نفس الرسالة
    if last_imitated_message_id == event.id:
        return
    last_imitated_message_id = event.id

    try:
        if event.media:
            try:
                path = await event.download_media()
                await client.send_file(
                    event.chat_id,
                    path,
                    caption=event.text or "",
                    reply_to=event.reply_to_msg_id if event.is_group or event.is_channel else None
                )
                os.remove(path)
            except:
                pass  # نتخطى الوسائط التي لا يمكن تحميلها
        elif event.text:
            await client.send_message(
                event.chat_id,
                event.text,
                reply_to=event.reply_to_msg_id if event.is_group or event.is_channel else None
            )
    except Exception as e:
        print(f"[❌] خطأ بالتقليد: {e}")

# ───── أوامر الترحيب ─────
def get_welcome(chat_id):
    conf = welcome_config.setdefault(chat_id, {"enabled": False, "text": "👋 أهلاً بك {mention}"})
    return conf

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def enable_welcome(event):
    if not await is_owner(event):
        return
    conf = get_welcome(event.chat_id)
    conf["enabled"] = True
    msg = await event.edit("✅ تم تفعيل الترحيب")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def disable_welcome(event):
    if not await is_owner(event):
        return
    conf = get_welcome(event.chat_id)
    conf["enabled"] = False
    msg = await event.edit("🛑 تم تعطيل الترحيب")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def set_welcome(event):
    if
