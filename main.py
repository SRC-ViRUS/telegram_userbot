# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025) – إصدار مُصحَّح
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import os, asyncio, datetime, tempfile
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FileReferenceExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import GetUserPhotosRequest

# ─────────── بيانات الاتصال ───────────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = "ضع_سلسلة_الجلسة_هنا"
client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ─────────── متغيّرات ───────────
muted_private = set()
muted_groups  = {}
imitate_targets, last_imitated = set(), {}
welcome_cfg = {}
name_task, prev_name = None, None

# ─────────── مساعدات ───────────
def baghdad_time(fmt="%I:%M %p"):
    """إرجاع الوقت الحالي في بغداد بصيغة 12 ساعة"""
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def qedit(event, txt, delay=2):
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()

async def send_media_safe(dest, media, caption=None, ttl=None):
    """إرسال وسائط مع معالجة FileReferenceExpired"""
    try:
        await client.send_file(dest, media, caption=caption, ttl=ttl)
    except FileReferenceExpiredError:
        temp = await client.download_media(media, file=tempfile.mktemp())
        await client.send_file(dest, temp, caption=caption, ttl=ttl)
        os.remove(temp)

# ─────────── الاسم المؤقت ───────────
async def loop_name():
    global prev_name
    prev_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=baghdad_time()))
        except: pass
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def name_on(event):
    if not await is_owner(event): return
    global name_task
    if name_task and not name_task.done():
        return await qedit(event, "✅ مفعل بالفعل.")
    name_task = asyncio.create_task(loop_name())
    await qedit(event, "🕒 تم تفعيل الاسم المؤقت.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def name_off(event):
    if not await is_owner(event): return
    global name_task, prev_name
    if name_task: name_task.cancel()
    name_task = None
    if prev_name:
        try: await client(UpdateProfileRequest(first_name=prev_name))
        except: pass
    await qedit(event, "🛑 تم إيقاف الاسم المؤقت.")

# ─────────── كتم وفك كتم ───────────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e:e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id,set())).add(r.sender_id)
    await qedit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e:e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id,set())).discard(r.sender_id)
    await qedit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def list_mute(event):
    if not await is_owner(event): return
    lines=[]
    if muted_private:
        lines.append("• خاص:"); lines += [f"  - {u}" for u in muted_private]
    for cid, users in muted_groups.items():
        if users:
            lines.append(f"\n• جروب {cid}:")
            lines += [f"  - {u}" for u in users]
    await qedit(event, "\n".join(lines) if lines else "لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def clear_mute(event):
    if not await is_owner(event): return
    muted_private.clear(); muted_groups.clear()
    await qedit(event, "🗑️ تم مسح الكتم.")

# ─────────── التقليد ───────────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e:e.is_reply))
async def imitate_on(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    imitate_targets.add(r.sender_id)
    last_imitated.pop(r.sender_id, None)
    await qedit(event, f"✅ تفعيل التقليد لـ {r.sender_id}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def imitate_off(event):
    if not await is_owner(event): return
    imitate_targets.clear(); last_imitated.clear()
    await qedit(event, "🛑 تم إيقاف التقليد.")

# ─────────── مُعالج موحّد لكل الرسائل الواردة ───────────
@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    uid = event.sender_id

    # 1) حذف رسائل المكتومين
    if event.is_private and uid in muted_private:
        return await event.delete()
    if event.is_group and uid in muted_groups.get(event.chat_id, set()):
        return await event.delete()

    # 2) التقليد
    if uid in imitate_targets:
        if last_imitated.get(uid) == event.id:
            return
        last_imitated[uid] = event.id

        if event.is_group:
            me = await client.get_me()
            if not (event.is_reply and (await event.get_reply_message()).sender_id == me.id or
                    f"@{me.username}" in (event.raw_text or "")):
                return

        try:
            dest = event.chat_id if event.is_group else uid
            if event.text:
                await client.send_message(dest, event.text)
            if event.media:
                ttl = getattr(event.media, "ttl_seconds", None)
                await send_media_safe(dest, event.media, event.text or None, ttl)
        except Exception as e:
            print("خطأ تقليد:", e)

    # 3) حفظ الوسائط المؤقتة
@client.on(events.NewMessage(incoming=True))
async def save_temp_media_to_saved(event):
    if not event.media:
        return
    ttl = getattr(event.media, "ttl_seconds", None)
    if not ttl:
        return
    # فقط في الخاص (تعديل حسب طلبك)
    if not event.is_private:
        return
    try:
        # تحميل الوسيط مؤقتاً
        file_path = await client.download_media(event.media, file=tempfile.mktemp())
        # إعادة رفعه للرسائل المحفوظة كملف عادي (دون ttl)
        await client.send_file("me", file_path, caption=f"📥 تم حفظ وسائط مؤقتة من {event.sender_id}")
        # حذف الملف المؤقت بعد الإرسال
        os.remove(file_path)
    except Exception as e:
        print(f"خطأ حفظ الوسائط المؤقتة في الرسائل المحفوظة: {e}")

# ─────────── الترحيب ───────────
@client.on(events.ChatAction)
async def welcome(event):
    if not (event.user_joined or event.user_added): return
    cfg = welcome_cfg.get(event.chat_id)
    if not (cfg and cfg["enabled"]): return
    user = await event.get_user(); chat = await event.get_chat()
    msg = cfg["msg"].format(الاسم=user.first_name, الايدي=user.id, القروب=chat.title)
    await client.send_message(event.chat_id, msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def w_on(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id] = {"enabled": True, "msg": "اهلا {الاسم} 🌸"}
    await qedit(event, "✅ تم تفعيل الترحيب.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def w_off(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id] = {"enabled": False, "msg": ""}
    await qedit(event, "🛑 تم تعطيل الترحيب.")

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
    await event.edit("⚡ جارٍ الفحص..."); await asyncio.sleep(2)
    await event.edit("✅ البوت شغال."); await asyncio.sleep(4); await event.delete()

@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def info(event):
    if not await is_owner(event): return
    if not event.is_group: return await qedit(event, "❌ هذا الأمر للمجموعات فقط.")
    chat = await event.get_chat()
    out = (f"🏷️ {chat.title}\n🆔 {chat.id}\n"
           f"👥 {getattr(chat, 'participants_count', '?')}\n"
           f"📛 @{getattr(chat, 'username', 'لا يوجد')}")
    await qedit(event, out, 5)

# ─────────── قائمة الأوامر ───────────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmds(event):
    if not await is_owner(event): return
    txt = """
<b>💡 الأوامر:</b>

<code>.اسم مؤقت</code> – تفعيل اسم الساعة
<code>.ايقاف الاسم</code> – إيقاف الاسم المؤقت

<code>.كتم</code> (رد) – كتم المستخدم
<code>.الغاء الكتم</code> (رد) – فك الكتم
<code>.قائمة الكتم</code> – عرض المكتومين
<code>.مسح الكتم</code> – مسح جميع المكتومين

<code>.تقليد</code> (رد) – تفعيل التقليد
<code>.ايقاف التقليد</code> – إيقاف التقليد

<code>.تفعيل الترحيب</code> – تشغيل الترحيب
<code>.تعطيل الترحيب</code> – إيقاف الترحيب
<code>.وضع ترحيب نص</code> – تخصيص رسالة الترحيب

<code>.صورة البروفايل</code> – إرسال آخر صورة بروفايل

<code>.كشف</code> – معلومات المجموعة
<code>.فحص</code> – فحص البوت
<code>.الاوامر</code> – هذه القائمة
"""
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(20); await event.delete()

# ─────────── تشغيل البوت ───────────
async def start_note():
    me = await client.get_me()
    await client.send_message("me", f"✅ البوت قيد التشغيل – @{me.username or me.first_name}")

print("🚀 البوت يعمل – المطور: الصعب")
client.start()
client.loop.run_until_complete(start_note())
client.run_until_disconnected()
