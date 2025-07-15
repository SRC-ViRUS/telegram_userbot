# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import os, asyncio, datetime, tempfile
from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.errors import FileReferenceExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.channels import EditTitleRequest

# ─────────── بيانات الاتصال ───────────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHPHEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgKVts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEghyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="
client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ─────────── متغيّرات ───────────
muted_private = set()
muted_groups = {}
imitate_targets = set()
last_imitated = {}
welcome_cfg = {}
name_task = None
prev_name = None
group_name_tasks = {}
original_titles = {}

# ─────────── مساعدات ───────────
def baghdad_time(fmt="%I:%M %p"):
    """توقيت بغداد 12 ساعة"""
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def qedit(event, txt, delay=2):
    """تعديل رسالة ثم حذفها بعد delay ثانية"""
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()

async def send_media_safe(dest, media, caption=None, ttl=None):
    """إرسال وسائط مع التعامل مع انتهاء المرجعية"""
    try:
        await client.send_file(dest, media, caption=caption, ttl=ttl)
    except FileReferenceExpiredError:
        f = await client.download_media(media, file=tempfile.mktemp())
        await client.send_file(dest, f, caption=caption, ttl=ttl)
        os.remove(f)

## ─────────── الاسم المؤقت للحساب (12 ساعة – بغداد – بدون حروف) ───────────

name_task = None
prev_name = None

@client.on(events.NewMessage(pattern=r"^\.مؤقت$"))
async def cmd_name_on(event):
    if not await is_owner(event): return
    global name_task, prev_name

    if name_task and not name_task.done():
        return await qedit(event, "✅ الاسم المؤقت مفعل مسبقًا.")

    if not prev_name:
        try:
            me = await client.get_me()
            prev_name = me.first_name
        except Exception as e:
            print("⚠️ فشل في جلب الاسم الأصلي:", e)
            prev_name = "حسابي"

    async def update_name_loop():
        while True:
            try:
                # توقيت بغداد بصيغة 12 ساعة بدون AM/PM
                baghdad_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime('%I:%M')
                await client(UpdateProfileRequest(first_name=baghdad_time))
                print(f"✅ الاسم الحالي: {baghdad_time}")
            except Exception as e:
                print("❌ خطأ أثناء تغيير الاسم:", e)
            await asyncio.sleep(60)

    name_task = asyncio.create_task(update_name_loop())
    await qedit(event, "🕒 تم تفعيل الاسم المؤقت للحساب.")

@client.on(events.NewMessage(pattern=r"^\.مؤقت توقف$"))
async def cmd_name_off(event):
    if not await is_owner(event): return
    global name_task, prev_name

    if name_task:
        name_task.cancel()
        name_task = None
    else:
        return await qedit(event, "⚠️ الاسم المؤقت غير مفعل.")

    if prev_name:
        try:
            await client(UpdateProfileRequest(first_name=prev_name))
            await qedit(event, "🛑 تم إيقاف الاسم المؤقت وإرجاع الاسم الأصلي.")
        except Exception as e:
            print("⚠️ فشل في إرجاع الاسم:", e)
            await qedit(event, "❌ لم يتم إرجاع الاسم تلقائيًا.")
    else:
        await qedit(event, "🛑 تم الإيقاف، لا يوجد اسم محفوظ.")
async def update_group_title(chat_id):
    while True:
        try:
            new_title = f"🕒 {baghdad_time()}"
            await client(EditTitleRequest(chat_id, new_title))
        except Exception as e:
            print(f"خطأ تغيير اسم القروب {chat_id}:", e)
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت قروب$"))
async def start_group_name_loop(event):
    if not await is_owner(event): return
    if not event.is_group: 
        return await qedit(event, "❌ هذا الأمر فقط في القروبات أو القنوات.")
    cid = event.chat_id
    if cid in group_name_tasks:
        return await qedit(event, "✅ مفعل مسبقًا.")
    chat = await event.get_chat()
    original_titles[cid] = chat.title
    task = asyncio.create_task(update_group_title(cid))
    group_name_tasks[cid] = task
    await qedit(event, "🕒 تم تفعيل الاسم المؤقت للقروب.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم القروب$"))
async def stop_group_name_loop(event):
    if not await is_owner(event): return
    cid = event.chat_id
    task = group_name_tasks.pop(cid, None)
    if task:
        task.cancel()
    if cid in original_titles:
        try:
            await client(EditTitleRequest(cid, original_titles[cid]))
        except Exception as e:
            print(f"خطأ إرجاع اسم القروب {cid}:", e)
        original_titles.pop(cid)
    await qedit(event, "🛑 تم إيقاف الاسم المؤقت للقروب.")

# ─────────── الكتم ───────────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e:e.is_reply))
async def cmd_mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    if event.is_private:
        muted_private.add(r.sender_id)
    else:
        muted_groups.setdefault(event.chat_id,set()).add(r.sender_id)
    await qedit(event,"🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e:e.is_reply))
async def cmd_unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    if event.is_private:
        muted_private.discard(r.sender_id)
    else:
        muted_groups.get(event.chat_id,set()).discard(r.sender_id)
    await qedit(event,"🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def cmd_mlist(event):
    if not await is_owner(event): return
    lines = []
    if muted_private:
        lines.append("• خاص:")
        lines += [f"  - {u}" for u in muted_private]
    for cid, users in muted_groups.items():
        if users:
            lines.append(f"\n• جروب {cid}:")
            lines += [f"  - {u}" for u in users]
    await qedit(event, "\n".join(lines) if lines else "لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def cmd_mclear(event):
    if not await is_owner(event): return
    muted_private.clear()
    muted_groups.clear()
    await qedit(event, "🗑️ تم المسح.")

@client.on(events.NewMessage(incoming=True))
async def auto_del(event):
    if event.is_private and event.sender_id in muted_private:
        return await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]:
        return await event.delete()

# ─────────── التقليد ───────────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e:e.is_reply))
async def cmd_imitate_on(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    imitate_targets.add(r.sender_id)
    last_imitated.pop(r.sender_id, None)
    await qedit(event, f"✅ تفعيل التقليد لـ {r.sender_id}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def cmd_imitate_off(event):
    if not await is_owner(event): return
    imitate_targets.clear()
    last_imitated.clear()
    await qedit(event, "🛑 تم إيقاف التقليد.")

@client.on(events.NewMessage(incoming=True))
async def imitate(event):
    uid = event.sender_id
    if uid not in imitate_targets: 
        return
    if last_imitated.get(uid) == event.id:
        return
    last_imitated[uid] = event.id
    try:
        if event.is_group:
            me = await client.get_me()
            # فقط يقلد اذا رد أو ذكر اسمه
            if not (event.is_reply and (await event.get_reply_message()).sender_id == me.id) and f"@{me.username}" not in (event.raw_text or ""):
                return
        if event.text:
            await client.send_message(event.chat_id if event.is_group else uid, event.text)
        if event.media:
            ttl = getattr(event.media, "ttl_seconds", None)
            await send_media_safe(event.chat_id if event.is_group else uid, event.media, event.text or None, ttl=ttl)
    except Exception as e:
        print("خطأ تقليد:", e)

# ─────────── حفظ الوسائط المؤقتة في الرسائل المحفوظة ───────────
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()
    if event.is_private and event.media and getattr(event.media, 'ttl_seconds', None):
        try:
            path = await event.download_media("downloads/")
            await client.send_file("me", path, caption="📸 تم حفظ البصمة.")
            os.remove(path)
        except Exception:
            pass

# ─────────── الترحيب ───────────
@client.on(events.ChatAction)
async def welcome(event):
    if not (event.user_joined or event.user_added): 
        return
    cfg = welcome_cfg.get(event.chat_id)
    if not (cfg and cfg["enabled"]): 
        return
    user = await event.get_user()
    chat = await event.get_chat()
    msg = cfg["msg"].format(الاسم=user.first_name, الايدي=user.id, القروب=chat.title)
    await client.send_message(event.chat_id, msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def w_on(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id] = {"enabled": True, "msg": "اهلا {الاسم} 🌸"}
    await qedit(event, "✅ تم التفعيل.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def w_off(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id] = {"enabled": False, "msg": " "}
    await qedit(event, "🛑 تم التعطيل.")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def w_set(event):
    if not await is_owner(event): return
    txt = event.pattern_match.group(1)
    welcome_cfg[event.chat_id] = {"enabled": True, "msg": txt}
    await qedit(event, "📩 تم تحديث الترحيب.")

# ─────────── صورة البروفايل ───────────
@client.on(events.NewMessage(pattern=r"^\.صورة البروفايل$"))
async def profile_photo(event):
    if not await is_owner(event): return
    me = await client.get_me()
    photos = await client(GetUserPhotosRequest(me.id, offset=0, max_id=0, limit=1))
    if photos.photos:
        await send_media_safe("me", photos.photos[0], "🖼️ آخر صورة بروفايل")
        await qedit(event, "✅ أُرسلت الصورة إلى الرسائل المحفوظة.")
    else:
        await qedit(event, "❌ لا توجد صورة بروفايل.")

# ─────────── فحص وكشف ───────────
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check(event):
    if not await is_owner(event): return
    await event.edit("⚡ جارٍ الفحص...")
    await asyncio.sleep(2)
    await event.edit("✅ البوت شغال.")
    await asyncio.sleep(5)
    await event.delete()

@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def info(event):
    if not await is_owner(event): return
    if not event.is_group:
        return await qedit(event, "❌ هذا الأمر للمجموعات فقط.")
    chat = await event.get_chat()
    out = (
        f"🏷️ {chat.title}\n"
        f"🆔 {chat.id}\n"
        f"👥 {getattr(chat,'participants_count','?')}\n"
        f"📛 @{getattr(chat,'username','لا يوجد')}"
    )
    await qedit(event, out, 5)

# ─────────── ايدي ───────────
@client.on(events.NewMessage(pattern=r"^\.ايدي$"))
async def get_id(event):
    if not await is_owner(event): return
    if event.is_reply:
        r = await event.get_reply_message()
        await qedit(event, f"🆔 آيدي الشخص: <code>{r.sender_id}</code>")
    else:
        await qedit(event, f"🆔 آيديك: <code>{event.sender_id}</code>")

# ─────────── البنق (Ping) ───────────
@client.on(events.NewMessage(pattern=r"^\.البنق$"))
async def ping(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    m = await event.edit("🏓 بنق ...")
    end = datetime.datetime.now()
    diff = (end - start).microseconds / 1000
    await m.edit(f"🏓 السرعة: <b>{diff:.2f}ms</b>", parse_mode="html")
    await asyncio.sleep(5)
    await m.delete()

# ─────────── تكرار تلقائي ───────────
repeat_task = None

@client.on(events.NewMessage(pattern=r"^\.تكرار تلقائي (\d+) (.+)$"))
async def auto_repeat(event):
    if not await is_owner(event): return
    global repeat_task
    seconds = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)

    if repeat_task and not repeat_task.done():
        repeat_task.cancel()

    async def loop():
        while True:
            try:
                await client.send_message(event.chat_id, text)
            except Exception as e:
                print("خطأ في التكرار:", e)
            await asyncio.sleep(seconds)

    repeat_task = asyncio.create_task(loop())
    await qedit(event, f"🔁 بدأ التكرار كل {seconds} ثانية.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التكرار$"))
async def stop_repeat(event):
    if not await is_owner(event): return
    global repeat_task
    if repeat_task:
        repeat_task.cancel()
        repeat_task = None
        await qedit(event, "⛔ تم إيقاف التكرار.")
    else:
        await qedit(event, "⚠️ لا يوجد تكرار فعال.")

# ──────── كود منشن متطور ────────
# المطور: الصعب © 2025

import asyncio
import random
from telethon import events

# قائمة رسائل الترحيب
mention_messages = [
    "ﻣـسٱ۽ آࢦخـيࢪ يصـاك🫀🤍🍯.",
    "عـࢪفنـه ؏ـليـك؟ 🌚💗",
    "مـن وين آݪحـ̷ِْــٰــ۫͜ݪو 🌝",
    "نتـَٰــۘ❀ـَٰـعرف بــݪطــف",
    "كافي نوم 🤍",
    "هَــْهلااا حـيلي 🤍",
    "ياصـف؟ 🗿",
    "مِمجَࢪډ شعوٚࢪ 🧘🏾‍♀️.",
    "نـايـم ڪـاعد🫦؟",
    "اللطف مخلوق حياتي 💖",
    "ويـنك 🙄🤍",
    "هل تقبل الزواج مني🥲",
    "ويـن طـامـس 🙄♥.",
    "صبـاح اݪخـير 🫂♥.",
    "اكلتك المفضلهہَ شننۅ ؟..",
    "هـلا حٝـب 💙",
    "بݪشش اتصال تع يحلو ✨🤍",
    "⌁︙ممكن نتعرفف🙂🍭",
    "أصبح علئ صوتك🫦.",
    "اެحَسَسَ اެخذت ڪِلبي ححَࢪفياا 😣ِْ🤍 𓍲 .",
    "شِكد ععَدډ الي منطِيهم بلۅك؟.. 🥹",
    "ۿهلا يععَمࢪي 🏷َِ💗",
    "مسس يـَפــَݪۄ  💞🫶🏻 ",
    "صــح ألــنــوم يــحـلو 💕😴",
    "صباحوو توت بالقشطه 🦋🍒",
    "شونك يحلو 😉 ••",
    "مس يحلو 🌚👀 ••",
    "ويــــن طامس يحلو/ه😒 ••",
    "هاذا الحلو كاتلني يعمه ❤️",
    "ييحٍحٍ مۆشُ نــفــر عٍآفَيَهّ وُرٍبَي🥺💞🦋",
    "شلخبار 🚶🏿‍♂️..🙂",
    "شكد طولك🌝؟",
    "مـشتاق لعيونك. 🌝🍫.",
]

# تأكد أن صاحب الحساب هو من يستدعي الأمر
async def is_owner(event, client):
    me = await client.get_me()
    return event.sender_id == me.id

# الحدث الأساسي: أمر .منشن
@events.register(events.NewMessage(pattern=r"^\.منشن$"))
async def mention_all(event):
    if not await is_owner(event, event.client):
        return

    if not event.is_group:
        return await event.edit("❌ هذا الأمر يعمل داخل القروبات فقط.")

    await event.edit("🔄 جاري جمع أعضاء المجموعة...")

    users = []
    async for user in event.client.iter_participants(event.chat_id):
        if not user.bot and not user.deleted:
            users.append(user)

    if not users:
        return await event.edit("⚠️ لم يتم العثور على أعضاء للمنشن.")

    await event.edit(f"🚀 بدأ منشن {len(users)} عضو...")

    used_msgs = set()
    for user in users:
        # اختر رسالة ترحيب غير مكررة
        texts = [m for m in mention_messages if m not in used_msgs] or mention_messages
        msg = random.choice(texts)
        used_msgs.add(msg)

        name = user.first_name or "صديق"
        mention = f"<a href='tg://user?id={user.id}'>{name}</a>"

        try:
            await event.client.send_message(
                event.chat_id,
                f"{msg} {mention}",
                parse_mode="html"
            )
            await asyncio.sleep(5)  # تأخير 5 ثواني بين كل رسالة
        except Exception as e:
            print(f"⚠️ خطأ أثناء المنشن: {e}")

    await event.respond("✅ تم منشن كل الأعضاء بنجاح.")

# ─────────── قائمة الأوامر ───────────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmds(event):
    if not await is_owner(event): return
    txt = """
<b>💡 الأوامر:</b>

<code>.ايدي</code> – عرض الآيدي والمعلومات

<code>.البنق</code> – سرعة البوت ومدة التشغيل

<code>.تكرار تلقائي [ث] [نص]</code> – إرسال النص دوريًّا

<code>.ايقاف التكرار</code> – إيقاف التكرار

<b>📝 أوامر منشن متقدمة:</b>
.منشن
↳ منشن كل أعضاء القروب برسائل ترحيب (واحدة كل 5 ثواني)

.لاتمنشن
↳ إيقاف أمر المنشن نهائياً

.منشن تفعيل
↳ تفعيل أمر المنشن بعد الإيقاف

.منشن حالة
↳ عرض حالة المنشن (مفعل ✅ / معطل 🛑) 

<code>.مؤقت توقف</code> – إيقاف الاسم المؤقت للحساب

<code>.اسم مؤقت يلكروب</code> – تفعيل اسم الوقت للقروب/القناة
<code>.ايقاف اسم القروب</code> – إيقاف الاسم المؤقت للقروب

<code>.كتم</code> (رد) – كتم
<code>.الغاء الكتم</code> (رد) – فك كتم
<code>.قائمة الكتم</code> – عرض الكتم
<code>.مسح الكتم</code> – مسح الكتم

<code>.تقليد</code> (رد) – تفعيل التقليد
<code>.ايقاف التقليد</code> – إيقاف التقليد

<code>.تفعيل الترحيب</code> – تشغيل الترحيب
<code>.تعطيل الترحيب</code> – إيقاف الترحيب
<code>.وضع ترحيب نص</code> – تغيير نص الترحيب

<code>.صورة البروفايل</code> – إرسال صورة البروفايل
<code>.كشف</code> – معلومات القروب
<code>.فحص</code> – فحص البوت
<code>.الاوامر</code> – عرض قائمة الأوامر
"""
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(600)
    # *** هنا لم نحذف رسالة الأوامر أبداً كما طلبت ***

# ─────────── تشغيل البوت ───────────
async def start_note():
    me = await client.get_me()
    await client.send_message("me", f"✅ البوت قيد التشغيل – @{me.username or me.first_name}")

print("🚀 البوت يعمل – المطور: الصعب")
client.start()
client.loop.run_until_complete(start_note())
client.run_until_disconnected()
