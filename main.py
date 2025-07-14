# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل فائق التطوير
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.

◆ المزايا المدمجة:
────────────────────────────────────────
1) كتم دائم ومؤقّت (s / m / h / d) مع فك تلقائي   
2) تقليد ذكي (خاص دائماً – كروب عند منشن أو رد)  
3) اسم مؤقّت (الساعة فقط) للحساب – بدون رموز   
4) ترحيب متغيّرات {الاسم}{الايدي}{القروب}   
5) حفظ الوسائط المؤقتة وبصمات TTL   
6) قائمة أوامر منسّقة وسهلة النسخ   
7) سجل أخطاء يُرسل لـ Saved Messages   
8) متوافق مع Telethon 1.40.0 وبيئة Zeabur
────────────────────────────────────────
"""

import os
import re
import asyncio
import datetime
from collections import defaultdict

from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import ChatAdminRequiredError

# ───── بيانات الاتصال ─────
api_id = 20507759
api_hash = "225d3a24d84c637b3b816d13cc7bd766"
session_string = "1ApWapzMBu6vOgZU6ORszv7oDvb1YG3qw4PPoXdP1vaUkL6RH7lWG3Rj3Vt3-ai2kyID0DGo-ZZVtB-fMlRd-nD-AO2-w1Q9qqO3qqp1TzJ21CvwJwL6yo2yavX2BHPHEBiWrEDiHqO01g1zY4t_Kf7dA-01qZqBCzRmDir6htC1VmFkY-GUXUQSqRgskQu3mz42hC-GHQmp-6sc-GRDgOQj_p5CcziJQNUg8wxoMdQlr8tAGBySMM_EPkUXSgKVts4iphZ3jVf_bLnBoj2DiugSN9VKJUhEA7R0cOvlpuC88huj4mUypaJ5OnO-aEghyN5--kFl3hrVVBtmLnGOBuRRloAKxZsY="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ═════════════════ المتغيّرات ═════════════════
muted_private = set()
muted_groups = defaultdict(set)
timed_unmutes = {}
taqleed_targets = set()
last_taqleed_id = {}
change_name_task = None
previous_name = None
welcome_config = {}
HELP = {}
EDIT_DELAY = 1

# ═════════════════ المساعدات ═════════════════
def now_baghdad(fmt="%I:%M %p"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def quick_edit(event, text, delay=EDIT_DELAY):
    await event.edit(text, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()

def parse_duration(text):
    m = re.fullmatch(r"(\d+)([smhd])", text.lower())
    if not m:
        return None
    v, u = int(m.group(1)), m.group(2)
    return v * {"s":1,"m":60,"h":3600,"d":86400}[u]

def help_add(cmd, desc):
    HELP[cmd] = desc

async def log_error(exc, where):
    await client.send_message("me", f"⚠️ <b>{where}</b>\n<code>{repr(exc)}</code>", parse_mode="html")

# ═════════════════ الاسم المؤقّت ═════════════════
async def loop_name():
    global previous_name
    previous_name = (await client.get_me()).first_name
    while True:
        try:
            await client(UpdateProfileRequest(first_name=now_baghdad()))
        except Exception as e:
            await log_error(e, "loop_name")
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت$"))
async def start_temp_name(event):
    if not await is_owner(event): return
    global change_name_task
    if change_name_task and not change_name_task.done():
        return await quick_edit(event, "✅ الاسم المؤقت مفعل مسبقاً.")
    change_name_task = asyncio.create_task(loop_name())
    await quick_edit(event, "🕒 تم تفعيل الاسم المؤقت.")
help_add(".اسم مؤقت","تفعيل الاسم المؤقت (الوقت فقط)")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الاسم$"))
async def stop_temp_name(event):
    if not await is_owner(event): return
    global change_name_task, previous_name
    if change_name_task:
        change_name_task.cancel()
        change_name_task = None
    if previous_name:
        try: await client(UpdateProfileRequest(first_name=previous_name))
        except Exception as e: await log_error(e,"stop_temp_name")
    await quick_edit(event, "🛑 تم إيقاف الاسم المؤقت.")
help_add(".ايقاف الاسم","إيقاف الاسم المؤقت")

# ═════════════════ الكتم ═════════════════
async def schedule_unmute(chat_id,user_id,sec):
    await asyncio.sleep(sec)
    (muted_private if chat_id is None else muted_groups[chat_id]).discard(user_id)
    timed_unmutes.pop((chat_id,user_id),None)

@client.on(events.NewMessage(pattern=r"^\.كتم(?: (\d+[smhd]))?$", func=lambda e:e.is_reply))
async def mute(event):
    if not await is_owner(event): return
    dur_txt = event.pattern_match.group(1)
    r = await event.get_reply_message()
    if not r: return await quick_edit(event,"❗️رد على شخص.")
    chat_id = None if event.is_private else event.chat_id
    target = muted_private if chat_id is None else muted_groups[chat_id]
    target.add(r.sender_id)
    if dur_txt:
        seconds=parse_duration(dur_txt)
        if not seconds: return await quick_edit(event,"⛔ صيغة مدة خطأ.")
        task=asyncio.create_task(schedule_unmute(chat_id,r.sender_id,seconds))
        timed_unmutes[(chat_id,r.sender_id)]=task
        await quick_edit(event,f"🔇 كتم مؤقت {dur_txt}.")
    else:
        await quick_edit(event,"🔇 تم الكتم.")
help_add(".كتم","كتم دائم أو مؤقت (.كتم 10m)")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e:e.is_reply))
async def unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    if not r: return await quick_edit(event,"❗️رد على شخص.")
    chat_id = None if event.is_private else event.chat_id
    (muted_private if chat_id is None else muted_groups[chat_id]).discard(r.sender_id)
    t=timed_unmutes.pop((chat_id,r.sender_id),None)
    if t: t.cancel()
    await quick_edit(event,"🔊 تم فك الكتم.")
help_add(".الغاء الكتم","فك الكتم (رد)")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def list_mute(event):
    if not await is_owner(event): return
    lines=[]
    if muted_private:
        lines.append("• خاص:")
        lines.extend(f"  - {u}" for u in muted_private)
    for cid,users in muted_groups.items():
        if users:
            title=(await client.get_entity(cid)).title
            lines.append(f"\n• {title}:")
            lines.extend(f"  - {u}" for u in users)
    await quick_edit(event,"\n".join(lines) if lines else "لا يوجد مكتومين.")
help_add(".قائمة الكتم","عرض المكتومين")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def clear_mute(event):
    if not await is_owner(event): return
    muted_private.clear(); muted_groups.clear()
    for t in timed_unmutes.values(): t.cancel()
    timed_unmutes.clear()
    await quick_edit(event,"🗑️ مسح الكتم.")
help_add(".مسح الكتم","مسح كل المكتومين")

@client.on(events.NewMessage(incoming=True))
async def auto_del_muted(event):
    uid=event.sender_id
    if event.is_private and uid in muted_private:
        return await event.delete()
    if event.is_group and uid in muted_groups.get(event.chat_id,set()):
        return await event.delete()

# ═════════════════ التقليد المطوّر ═════════════════
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e:e.is_reply))
async def enable_taqleed(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    if not r: return await quick_edit(event,"❗️رد على رسالة.")
    taqleed_targets.add(r.sender_id)
    last_taqleed_id.pop(r.sender_id,None)
    await quick_edit(event,f"✅ بدأ التقليد لـ {r.sender_id}.")
help_add(".تقليد","تقليد شخص (رد)")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def disable_taqleed(event):
    if not await is_owner(event): return
    taqleed_targets.clear(); last_taqleed_id.clear()
    await quick_edit(event,"🛑 تم إيقاف التقليد.")
help_add(".ايقاف التقليد","إيقاف جميع التقليدات")

@client.on(events.NewMessage(incoming=True))
async def do_taqleed(event):
    uid = event.sender_id
    if uid not in taqleed_targets: return
    me = await client.get_me()

    # شروط التقليد في الكروب
    if event.is_group:
        if not (event.is_reply and (await event.get_reply_message()).sender_id==me.id or f"@{me.username}" in (event.raw_text or "")):
            return
        target = event.chat_id
    else:
        target = uid

    if last_taqleed_id.get(uid)==event.id: return
    last_taqleed_id[uid]=event.id

    try:
        if event.media and getattr(event.media,"ttl_seconds",None):
            await client.send_file(target,file=event.media,caption=event.text or None,ttl=event.media.ttl_seconds)
        elif event.text:
            await client.send_message(target,event.text)
        elif event.media:
            await client.send_file(target,file=event.media,caption=event.text or None)
    except Exception as e:
        print(f"⚠️ تجاهل تقليد: {e}")

# ═════════════════ الترحيب ═════════════════
@client.on(events.ChatAction)
async def welcome(event):
    if not (event.user_joined or event.user_added): return
    cfg=welcome_config.get(event.chat_id)
    if cfg and cfg.get("enabled"):
        user=await event.get_user()
        chat=await event.get_chat()
        msg=cfg["message"].format(الاسم=user.first_name,الايدي=user.id,القروب=chat.title)
        await client.send_message(event.chat_id,msg)

@client.on(events.NewMessage(pattern=r"^\.تفعيل الترحيب$"))
async def en_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id]={"enabled":True,"message":"اهلاً {الاسم} 🌸"}
    await quick_edit(event,"✅ تم تفعيل الترحيب.")
help_add(".تفعيل الترحيب","تفعيل الترحيب")

@client.on(events.NewMessage(pattern=r"^\.تعطيل الترحيب$"))
async def dis_welcome(event):
    if not await is_owner(event): return
    welcome_config[event.chat_id]={"enabled":False}
    await quick_edit(event,"🛑 تم تعطيل الترحيب.")
help_add(".تعطيل الترحيب","تعطيل الترحيب")

@client.on(events.NewMessage(pattern=r"^\.وضع ترحيب (.+)$"))
async def set_welcome(event):
    if not await is_owner(event): return
    txt=event.pattern_match.group(1)
    welcome_config[event.chat_id]={"enabled":True,"message":txt}
    await quick_edit(event,"📩 تم تحديث الترحيب.")
help_add(".وضع ترحيب","تخصيص الترحيب")

# ═════════════════ فحص وكشف ═════════════════
@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check(event):
    if not await is_owner(event): return
    await event.edit("⚡ جارٍ الفحص...")
    await asyncio.sleep(2)
    await event.edit("✅ البوت شغّال 💯")
    await asyncio.sleep(8)
    await event.delete()
help_add(".فحص","فحص البوت")

@client.on(events.NewMessage(pattern=r"^\.كشف$"))
async def info(event):
    if not await is_owner(event): return
    if not event.is_group: return await quick_edit(event,"❌ للمجموعات فقط.")
    chat=await event.get_chat()
    out=(f"🏷️ العنوان: {chat.title}\n"
         f"🆔 المعرّف: {chat.id}\n"
         f"👥 الأعضاء: {getattr(chat,'participants_count','?')}\n"
         f"📛 اسم المستخدم: @{getattr(chat,'username','لا يوجد')}")
    await quick_edit(event,out,delay=10)
help_add(".كشف","معلومات القروب")

# ═════════════════ حفظ الوسائط TTL ═════════════════
@client.on(events.NewMessage(incoming=True))
async def save_ttl(event):
    if not event.media: return
    ttl=getattr(event.media,"ttl_seconds",None)
    if not ttl: return
    try:
        sender=await event.get_sender()
        name=f"@{sender.username}" if sender.username else sender.first_name
        cap=f"📥 وسائط مؤقتة من {name} ({ttl}s)"
        await client.send_file("me",file=event.media,caption=cap)
    except Exception as e:
        await log_error(e,"save_ttl")

# ═════════════════ قائمة الأوامر ═════════════════
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def commands(event):
    if not await is_owner(event): return
    txt=["<b>🎛️ الأوامر:</b>\n"]
    for k,v in sorted(HELP.items()):
        txt.append(f"<code>{k}</code> – {v}")
    await event.edit("\n".join(txt),parse_mode="html")
    await asyncio.sleep(15)
    await event.delete()

# ═════════════ بدء التشغيل ═════════════
async def notify_start():
    try:
        me=await client.get_me()
        await client.send_message("me",f"✅ البوت قيد التشغيل – @{me.username or me.first_name}")
    except Exception: pass

print("🚀 تم تشغيل البوت بنجاح – المطور: الصعب")
client.start()
client.loop.run_until_complete(notify_start())
client.run_until_disconnected()
