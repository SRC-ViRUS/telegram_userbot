# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import os, asyncio, datetime, re, tempfile
from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.errors import FileReferenceExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import GetUserPhotosRequest

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

# ─────────── مساعدات ───────────
def baghdad_time(fmt="%I:%M %p"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def qedit(event, txt, delay=2):
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()

async def send_media_safe(dest, media, caption=None, ttl=None):
    try:
        await client.send_file(dest, media, caption=caption, ttl=ttl)
    except FileReferenceExpiredError:
        f = await client.download_media(media, file=tempfile.mktemp())
        await client.send_file(dest, f, caption=caption, ttl=ttl)
        os.remove(f)

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
async def cmd_name_on(event):
    if not await is_owner(event): return
    global name_task
    if name_task and not name_task.done():
        return await qedit(event, "✅ مفعل مسبقاً.")
    name_task = asyncio.create_task(loop_name())
    await qedit(event, "🕒 تم التفعيل.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def cmd_name_off(event):
    if not await is_owner(event): return
    global name_task, prev_name
    if name_task:
        name_task.cancel(); name_task=None
    if prev_name:
        try: await client(UpdateProfileRequest(first_name=prev_name))
        except: pass
    await qedit(event, "🛑 تم الإيقاف.")

# ─────────── الكتم ───────────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e:e.is_reply))
async def cmd_mute(event):
    if not await is_owner(event): return
    r=await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id,set())).add(r.sender_id)
    await qedit(event,"🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e:e.is_reply))
async def cmd_unmute(event):
    if not await is_owner(event): return
    r=await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id,set())).discard(r.sender_id)
    await qedit(event,"🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def cmd_mlist(event):
    if not await is_owner(event): return
    lines=[]
    if muted_private:
        lines.append("• خاص:"); lines+= [f"  - {u}" for u in muted_private]
    for cid,users in muted_groups.items():
        if users: lines.append(f"\n• جروب {cid}:"); lines+= [f"  - {u}" for u in users]
    await qedit(event,"\n".join(lines) if lines else "لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def cmd_mclear(event):
    if not await is_owner(event): return
    muted_private.clear(); muted_groups.clear()
    await qedit(event,"🗑️ تم المسح.")

@client.on(events.NewMessage(incoming=True))
async def auto_del(event):
    if event.is_private and event.sender_id in muted_private: return await event.delete()
    if event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]: return await event.delete()

# ─────────── التقليد ───────────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e:e.is_reply))
async def cmd_imitate_on(event):
    if not await is_owner(event): return
    r=await event.get_reply_message()
    imitate_targets.add(r.sender_id)
    last_imitated.pop(r.sender_id,None)
    await qedit(event, f"✅ تفعيل التقليد لـ {r.sender_id}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def cmd_imitate_off(event):
    if not await is_owner(event): return
    imitate_targets.clear(); last_imitated.clear()
    await qedit(event,"🛑 تم إيقاف التقليد.")

@client.on(events.NewMessage(incoming=True))
async def imitate(event):
    uid=event.sender_id
    if uid not in imitate_targets: return
    if last_imitated.get(uid)==event.id: return
    last_imitated[uid]=event.id
    try:
        if event.is_group:
            me=await client.get_me()
            if not (event.is_reply and (await event.get_reply_message()).sender_id==me.id or f"@{me.username}" in (event.raw_text or "")):
                return
        if event.text:
            await client.send_message(event.chat_id if event.is_group else uid, event.text)
        if event.media:
            ttl=getattr(event.media,"ttl_seconds",None)
            await send_media_safe(event.chat_id if event.is_group else uid, event.media, event.text or None, ttl=ttl)
    except Exception as e:
        print("خطأ تقليد:",e)

# ─────────── حفظ الوسائط المؤقتة ───────────
@client.on(events.NewMessage(incoming=True))
async def save_ttl(event):
    if not event.media: return
    ttl=getattr(event.media,"ttl_seconds",None)
    if not ttl: return
    sender=await event.get_sender()
    cap=f"📥 وسائط مؤقتة من {(sender.username or sender.first_name)} ({ttl}s)"
    await send_media_safe("me", event.media, cap, ttl)

# ─────────── الترحيب ───────────
@client.on(events.ChatAction)
async def welcome(event):
    if not (event.user_joined or event.user_added): return
    cfg=welcome_cfg.get(event.chat_id)
    if not (cfg and cfg["enabled"]): return
    user=await event.get_user(); chat=await event.get_chat()
    msg=cfg["msg"].format(الاسم=user.first_name,الايدي=user.id,القروب=chat.title)
    await client.send_message(event.chat_id,msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def w_on(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id]={"enabled":True,"msg":"اهلا {الاسم} 🌸"}
    await qedit(event,"✅ تم التفعيل.")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def w_off(event):
    if not await is_owner(event): return
    welcome_cfg[event.chat_id]={"enabled":False,"msg":" "}
    await qedit(event,"🛑 تم التعطيل.")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def w_set(event):
    if not await is_owner(event): return
    txt=event.pattern_match.group(1)
    welcome_cfg[event.chat_id]={"enabled":True,"msg":txt}
    await qedit(event,"📩 تم تحديث الترحيب.")

# ─────────── صورة البروفايل ───────────
@client.on(events.NewMessage(pattern=r"^\.صورة البروفايل$"))
async def profile_photo(event):
    if not await is_owner(event): return
    me=await client.get_me()
    photos = await client(GetUserPhotosRequest(me.id, offset=0, max_id=0, limit=1))
    if photos.photos:
        await send_media_safe("me", photos.photos[0], "🖼️ آخر صورة بروفايل")
        await qedit(event,"✅ أُرسلت الصورة إلى الرسائل المحفوظة.")
    else:
        await qedit(event,"❌ لا توجد صورة بروفايل.")

# ─────────── فحص وكشف ───────────
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check(event):
    if not await is_owner(event): return
    await event.edit("⚡ جارٍ الفحص..."); await asyncio.sleep(2)
    await event.edit("✅ البوت شغال."); await asyncio.sleep(5); await event.delete()

@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def info(event):
    if not await is_owner(event): return
    if not event.is_group: return await qedit(event,"❌ هذا الأمر للمجموعات فقط.")
    chat=await event.get_chat()
    out=f"🏷️ {chat.title}\n🆔 {chat.id}\n👥 {getattr(chat,'participants_count','?')}\n📛 @{getattr(chat,'username','لا يوجد')}"
    await qedit(event,out,5)

# ─────────── قائمة الأوامر ───────────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmds(event):
    if not await is_owner(event): return
    txt="""
<b>💡 الأوامر:</b>

<code>.اسم مؤقت</code> – تفعيل اسم الوقت
<code>.ايقاف الاسم</code> – إيقافه

<code>.كتم</code> (رد) – كتم
<code>.الغاء الكتم</code> (رد) – فك كتم
<code>.قائمة الكتم</code> – عرض الكتم
<code>.مسح الكتم</code> – مسح الكتم

<code>.تقليد</code> (رد) – تفعيل التقليد
<code>.ايقاف التقليد</code> – إيقافه

<code>.تفعيل الترحيب</code> – تشغيل الترحيب
<code>.تعطيل الترحيب</code> – إيقافه
<code>.وضع ترحيب نص</code> – تغيير الترحيب

<code>.صورة البروفايل</code> – إرسال صورة الحساب

<code>.كشف</code> – معلومات القروب
<code>.فحص</code> – فحص البوت
<code>.الاوامر</code> – هذه القائمة
"""
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(20); await event.delete()

# ─────────── تشغيل البوت ───────────
async def start_note():
    me=await client.get_me()
    await client.send_message("me", f"✅ البوت قيد التشغيل – @{me.username or me.first_name}")

print("🚀 البوت يعمل – المطور: الصعب")
client.start()
client.loop.run_until_complete(start_note())
client.run_until_disconnected()
