# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import os, asyncio, datetime, random, tempfile
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
muted_private, muted_groups = set(), {}
imitate_targets, last_imitated = set(), {}
welcome_cfg, group_name_tasks, original_titles = {}, {}, {}
name_task, prev_name, repeat_task = None, None, None

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
        tmp = await client.download_media(media, file=tempfile.mktemp())
        await client.send_file(dest, tmp, caption=caption, ttl=ttl)
        os.remove(tmp)

# ─────────── الاسم المؤقت للحساب ───────────
@client.on(events.NewMessage(pattern=r"^\.مؤقت$"))
async def cmd_name_on(event):
    if not await is_owner(event): return
    global name_task, prev_name
    if name_task and not name_task.done():
        return await qedit(event, "✅ الاسم المؤقت مفعل مسبقًا.")

    if not prev_name:
        prev_name = (await client.get_me()).first_name or "حسابي"

    async def update_name_loop():
        while True:
            try:
                t = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime('%I:%M')
                await client(UpdateProfileRequest(first_name=t))
            except Exception as e:
                print("❌ خطأ تغيير الاسم:", e)
            await asyncio.sleep(60)

    name_task = asyncio.create_task(update_name_loop())
    await qedit(event, "🕒 تم تفعيل الاسم المؤقت للحساب.")

@client.on(events.NewMessage(pattern=r"^\.مؤقت توقف$"))
async def cmd_name_off(event):
    if not await is_owner(event): return
    global name_task, prev_name
    if name_task:
        name_task.cancel(); name_task = None
    else:
        return await qedit(event, "⚠️ الاسم المؤقت غير مفعل.")
    try:
        await client(UpdateProfileRequest(first_name=prev_name))
        await qedit(event, "🛑 تم إرجاع الاسم الأصلي.")
    except Exception:
        await qedit(event, "❌ فشل إرجاع الاسم.")

# ─────────── اسم مؤقت للقروب ───────────
async def update_group_title(chat_id):
    while True:
        try:
            await client(EditTitleRequest(chat_id, f"🕒 {baghdad_time()}"))
        except Exception as e:
            print(f"خطأ تغيير اسم القروب {chat_id}:", e)
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.اسم مؤقت قروب$"))
async def start_group_name_loop(event):
    if not await is_owner(event) or not event.is_group:
        return await qedit(event, "❌ فقط داخل القروبات.")
    cid = event.chat_id
    if cid in group_name_tasks:
        return await qedit(event, "✅ مفعل مسبقًا.")
    original_titles[cid] = (await event.get_chat()).title
    task = asyncio.create_task(update_group_title(cid))
    group_name_tasks[cid] = task
    await qedit(event, "🕒 تم تفعيل الاسم المؤقت للقروب.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف اسم القروب$"))
async def stop_group_name_loop(event):
    if not await is_owner(event): return
    cid = event.chat_id
    task = group_name_tasks.pop(cid, None)
    if task: task.cancel()
    if cid in original_titles:
        try:
            await client(EditTitleRequest(cid, original_titles.pop(cid)))
        except Exception as e:
            print(f"خطأ إرجاع اسم القروب {cid}:", e)
    await qedit(event, "🛑 تم إيقاف الاسم المؤقت للقروب.")

# ─────────── الكتم ───────────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def cmd_mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id,set())).add(r.sender_id)
    await qedit(event,"🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.الغاء الكتم$", func=lambda e: e.is_reply))
async def cmd_unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id,set())).discard(r.sender_id)
    await qedit(event,"🔊 تم فك الكتم.")

@client.on(events.NewMessage(pattern=r"^\.قائمة الكتم$"))
async def cmd_mlist(event):
    if not await is_owner(event): return
    lines=[]
    if muted_private: lines+=["• خاص:"]+[f"  - {u}" for u in muted_private]
    for cid,users in muted_groups.items():
        if users: lines+= [f"\n• جروب {cid}:"]+[f"  - {u}" for u in users]
    await qedit(event,"\n".join(lines) if lines else "لا يوجد مكتومين.")

@client.on(events.NewMessage(pattern=r"^\.مسح الكتم$"))
async def cmd_mclear(event):
    if not await is_owner(event): return
    muted_private.clear(); muted_groups.clear()
    await qedit(event,"🗑️ تم المسح.")

@client.on(events.NewMessage(incoming=True))
async def auto_del(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()

# ─────────── التقليد ───────────
@client.on(events.NewMessage(pattern=r"^\.تقليد$", func=lambda e:e.is_reply))
async def cmd_imitate_on(event):
    if not await is_owner(event): return
    r=await event.get_reply_message()
    imitate_targets.add(r.sender_id); last_imitated.pop(r.sender_id,None)
    await qedit(event,f"✅ تفعيل التقليد لـ {r.sender_id}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def cmd_imitate_off(event):
    if not await is_owner(event): return
    imitate_targets.clear(); last_imitated.clear()
    await qedit(event,"🛑 تم إيقاف التقليد.")

@client.on(events.NewMessage(incoming=True))
async def imitate(event):
    uid=event.sender_id
    if uid not in imitate_targets or last_imitated.get(uid)==event.id: return
    last_imitated[uid]=event.id
    if event.is_group:
        me=await client.get_me()
        if not ((event.is_reply and (await event.get_reply_message()).sender_id==me.id) or f"@{me.username}" in (event.raw_text or "")): return
    try:
        if event.text: await client.send_message(event.chat_id if event.is_group else uid, event.text)
        if event.media:
            ttl=getattr(event.media,"ttl_seconds",None)
            await send_media_safe(event.chat_id if event.is_group else uid,event.media,event.text or None,ttl=ttl)
    except Exception as e:
        print("خطأ تقليد:",e)

# ─────────── حفظ الوسائط المؤقتة ───────────
@client.on(events.NewMessage(incoming=True))
async def handle_incoming(event):
    if (event.is_private and event.sender_id in muted_private) or \
       (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()
    if event.is_private and event.media and getattr(event.media,'ttl_seconds',None):
        try:
            p=await event.download_media("downloads/")
            await client.send_file("me",p,caption="📸 تم حفظ البصمة."); os.remove(p)
        except Exception: pass

# ─────────── الترحيب ───────────
@client.on(events.ChatAction)
async def welcome(event):
    if not (event.user_joined or event.user_added): return
    cfg=welcome_cfg.get(event.chat_id)
    if not(cfg and cfg["enabled"]): return
    user,chat=await event.get_user(),await event.get_chat()
    msg=cfg["msg"].format(الاسم=user.first_name, الايدي=user.id, القروب=chat.title)
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
    photos=await client(GetUserPhotosRequest(me.id,offset=0,max_id=0,limit=1))
    if photos.photos:
        await send_media_safe("me",photos.photos[0],"🖼️ آخر صورة بروفايل")
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
    if not await is_owner(event) or not event.is_group:
        return await qedit(event,"❌ هذا الأمر للمجموعات فقط.")
    chat=await event.get_chat()
    out=f"🏷️ {chat.title}\n🆔 {chat.id}\n👥 {getattr(chat,'participants_count','?')}\n📛 @{getattr(chat,'username','لا يوجد')}"
    await qedit(event,out,5)

# ─────────── ايدي ───────────
@client.on(events.NewMessage(pattern=r"^\.ايدي$"))
async def get_id(event):
    if not await is_owner(event): return
    if event.is_reply:
        r=await event.get_reply_message()
        await qedit(event,f"🆔 <code>{r.sender_id}</code>")
    else:
        await qedit(event,f"🆔 آيديك: <code>{event.sender_id}</code>")

# ─────────── البنق ───────────
@client.on(events.NewMessage(pattern=r"^\.البنق$"))
async def ping(event):
    if not await is_owner(event): return
    start=datetime.datetime.now(); m=await event.edit("🏓 ...")
    diff=(datetime.datetime.now()-start).microseconds/1000
    await m.edit(f"🏓 <b>{diff:.2f}ms</b>",parse_mode="html"); await asyncio.sleep(5); await m.delete()

# ─────────── تكرار تلقائي ───────────
@client.on(events.NewMessage(pattern=r"^\.تكرار تلقائي (\d+) (.+)$"))
async def auto_repeat(event):
    if not await is_owner(event): return
    global repeat_task
    seconds=int(event.pattern_match.group(1)); text=event.pattern_match.group(2)
    if repeat_task and not repeat_task.done(): repeat_task.cancel()
    async def loop():
        while True:
            try: await client.send_message(event.chat_id,text)
            except Exception as e: print("خطأ تكرار:",e)
            await asyncio.sleep(seconds)
    repeat_task=asyncio.create_task(loop())
    await qedit(event,f"🔁 بدأ التكرار كل {seconds} ث.")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التكرار$"))
async def stop_repeat(event):
    if not await is_owner(event): return
    global repeat_task
    if repeat_task: repeat_task.cancel(); repeat_task=None; await qedit(event,"⛔ أوقفنا التكرار.")
    else: await qedit(event,"⚠️ لا يوجد تكرار فعال.")

# ─────────── نظام المنشن ───────────
mention_messages = [  # القائمة كما هي
    "ﻣـسٱ۽ آࢦخـيࢪ يصـاك🫀🤍🍯.","عـࢪفنـه ؏ـليـك؟ 🌚💗","مـن وين آݪحـ̷ِْــٰــ۫͜ݪو 🌝","نتـَٰــۘ❀ـَٰـعرف بــݪطــف",
    "كافي نوم 🤍","هَــْهلااا حـيلي 🤍","ياصـف؟ 🗿","مِمجَࢪډ شعوٚࢪ 🧘🏾‍♀️.","نـايـم ڪـاعد🫦؟",
    "اللطف مخلوق حياتي 💖","ويـنك 🙄🤍","هل تقبل الزواج مني🥲","ويـن طـامـس 🙄♥.","صبـاح اݪخـير 🫂♥.","اكلتك المفضلهہَ شننۅ ؟..",
    "هـلا حٝـب 💙","بݪشش اتصال تع يحلو ✨🤍","⌁︙ممكن نتعرفف🙂🍭","أصبح علئ صوتك🫦.",
    "اެحَسَسَ اެخذت ڪِلبي ححَࢪفياا 😣ِْ🤍 𓍲 .","شِكد ععَدډ الي منطِيهم بلۅك؟.. 🥹","ۿهلا يععَمࢪي 🏷َِ💗",
    "مسس يـَפــَݪۄ  💞🫶🏻 ","صــح ألــنــوم يــحـلو 💕😴","صباحوو توت بالقشطه 🦋🍒","شونك يحلو 😉 ••","مس يحلو 🌚👀 ••",
    "ويــــن طامس يحلو/ه😒 ••","هاذا الحلو كاتلني يعمه ❤️","ييحٍحٍ مۆشُ نــفــر عٍآفَيَهّ وُرٍبَي🥺💞🦋","شلخبار 🚶🏿‍♂️..🙂",
    "شكد طولك🌝؟","مـشتاق لعيونك. 🌝🍫.",
]
mention_enabled=True

@client.on(events.NewMessage(pattern=r"^\.منشن$"))
async def mention_all(event):
    global mention_enabled
    if not await is_owner(event): return
    if not event.is_group: return await qedit(event,"❌ للڨروبات فقط.")
    if not mention_enabled: return await qedit(event,"🚫 المنشن متوقف.")
    await event.edit("🔄 تجميع الأعضاء ...")
    users=[u async for u in client.iter_participants(event.chat_id) if not u.bot and not u.deleted]
    if not users: return await qedit(event,"⚠️ ماكو أعضاء.")
    await event.edit(f"🚀 جارٍ منشن {len(users)} عضو...")
    used=set()
    for u in users:
        if not mention_enabled: return await event.respond("⛔ أُوقف المنشن.")
        avail=[m for m in mention_messages if m not in used] or mention_messages
        msg=random.choice(avail); used.add(msg)
        mention=f"<a href='tg://user?id={u.id}'>{u.first_name or 'صديق'}</a>"
        try: await client.send_message(event.chat_id,f"{msg} {mention}",parse_mode="html"); await asyncio.sleep(5)
        except Exception as e: print("خطأ منشن:",e)
    await event.respond("✅ انتهى المنشن.")

@client.on(events.NewMessage(pattern=r"^\.لاتمنشن$"))
async def disable_mention(event):
    global mention_enabled
    if not await is_owner(event): return
    mention_enabled=False; await qedit(event,"🛑 أوقفنا المنشن.")

@client.on(events.NewMessage(pattern=r"^\.منشن تفعيل$"))
async def enable_mention(event):
    global mention_enabled
    if not await is_owner(event): return
    mention_enabled=True; await qedit(event,"✅ فعّلنا المنشن.")

@client.on(events.NewMessage(pattern=r"^\.منشن حالة$"))
async def mention_status(event):
    if not await is_owner(event): return
    await qedit(event,f"📍 المنشن: {'✅ مفعل' if mention_enabled else '🛑 متوقف'}")
# ======= START: بايو روتيتور متطور أقصى حد مع بايو واسم وقتي =======
# © 2025 الصعب | Developer: الصعب | All rights reserved.
# Tag: #الصعب
# =======

import asyncio
from telethon import events, functions
import datetime

class UltimateBioRotator:
    def __init__(self, client, default_interval=60):
        self.client = client
        self.bio_list = []
        self.bio_index = 0
        self.interval = default_interval  # بالثواني، قابل للتعديل
        self.task = None
        self.is_running = False

        # البايو و الاسم الوقتي
        self.temp_bio_task = None
        self.temp_bio_active = False
        self.original_first_name = None
        self.original_last_name = None
        self.original_bio = None

    async def change_bio_periodically(self):
        while self.is_running:
            if not self.bio_list:
                await asyncio.sleep(self.interval)
                continue

            bio = self.bio_list[self.bio_index]
            try:
                await self.client(functions.account.UpdateProfileRequest(about=bio))
            except Exception as e:
                print(f"خطأ بتغيير البايو: {e}")

            self.bio_index = (self.bio_index + 1) % len(self.bio_list)
            await asyncio.sleep(self.interval)

    async def start(self, event):
        if self.is_running:
            await event.reply("⚠️ تغيير البايو التلقائي شغّال بالفعل.")
            return
        if not self.bio_list:
            await event.reply("⚠️ لا توجد بايوهات مضافة، أضف بايوهات أولاً باستخدام `.اضف_بايو`.")
            return
        self.is_running = True
        self.task = asyncio.create_task(self.change_bio_periodically())
        await event.reply(f"✅ بدأ تغيير البايو تلقائيًا كل {self.interval} ثانية.")

    async def stop(self, event):
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
                self.task = None
            await event.reply("🛑 تم إيقاف تغيير البايو التلقائي.")
        else:
            await event.reply("⚠️ التغيير التلقائي غير مفعل.")

    async def add_bio(self, event):
        text = event.pattern_match.group(1).strip()
        if not text:
            await event.reply("❌ لا يمكن إضافة بايو فارغ.")
            return
        self.bio_list.append(text)
        await event.reply(f"✅ تم إضافة البايو: «{text}»\nمجموع البايوهات: {len(self.bio_list)}")

    async def show_bios(self, event):
        if not self.bio_list:
            await event.reply("⚠️ قائمة البايوهات فارغة.")
            return
        msg = "📋 قائمة البايوهات بالتسلسل:\n\n"
        for i, bio in enumerate(self.bio_list, 1):
            msg += f"{i}. {bio}\n"
        await event.reply(msg)

    async def clear_bios(self, event):
        self.bio_list.clear()
        self.bio_index = 0
        await event.reply("🗑️ تم مسح كل البايوهات.")

    async def set_interval(self, event):
        try:
            sec = int(event.pattern_match.group(1))
            if sec < 5:
                await event.reply("❌ الفترة قصيرة جداً، يرجى تحديد 5 ثواني أو أكثر.")
                return
            self.interval = sec
            await event.reply(f"⏳ تم تعيين فترة تغيير البايو إلى {self.interval} ثانية.")
            if self.is_running:
                await self.stop(event)
                await self.start(event)
        except:
            await event.reply("❌ يرجى إدخال رقم صحيح للثواني. مثال: `.مدة_بايو 60`")

    async def remove_bio(self, event):
        try:
            index = int(event.pattern_match.group(1)) - 1
            if 0 <= index < len(self.bio_list):
                removed = self.bio_list.pop(index)
                await event.reply(f"🗑️ تم حذف البايو رقم {index+1}: «{removed}»")
                if self.bio_index >= len(self.bio_list):
                    self.bio_index = 0
            else:
                await event.reply("❌ رقم غير صالح.")
        except:
            await event.reply("❌ استخدم الأمر بهذا الشكل: `.حذف_بايو 2`")

    async def jump_to(self, event):
        try:
            index = int(event.pattern_match.group(1)) - 1
            if 0 <= index < len(self.bio_list):
                self.bio_index = index
                await event.reply(f"➡️ تم الانتقال للبايو رقم {index+1}.")
            else:
                await event.reply("❌ رقم غير صالح.")
        except:
            await event.reply("❌ استخدم الأمر بهذا الشكل: `.اذهب_لبايو 3`")

    # ======= بايو واسم وقتي مع حفظ النسخ الأصلية =======
    async def set_temp_bio(self, event):
        if self.temp_bio_active:
            await event.reply("⚠️ بايو واسم وقتي يعمل حالياً، أوقفه أولاً باستخدام `.ايقاف_بايو_وقتي`.")
            return

        text = event.pattern_match.group(1).strip()
        if '/' not in text:
            await event.reply("❌ استخدم الصيغة: `.بايو_وقتي نص_البايو /MM:SS`")
            return

        bio_part, time_part = text.rsplit('/', 1)
        bio_part = bio_part.strip()
        time_part = time_part.strip()

        try:
            m, s = time_part.split(':')
            duration_sec = int(m)*60 + int(s)
        except:
            await event.reply("❌ صيغة الوقت خاطئة، يجب أن تكون MM:SS مثل 01:15")
            return

        # حفظ النسخة الأصلية مرة واحدة فقط
        if self.original_first_name is None:
            try:
                user = await self.client.get_me()
                self.original_first_name = user.first_name or ""
                self.original_last_name = user.last_name or ""
                self.original_bio = user.about or ""
            except Exception as e:
                await event.reply(f"❌ خطأ بالحصول على بيانات الحساب: {e}")
                return

        # تحديث الاسم والبايو المؤقت (نغير الاسم الأول والبايو فقط)
        new_first = bio_part
        new_last = ""  # يمكن تعديل هذا لو تريد
        try:
            await self.client(functions.account.UpdateProfileRequest(
                first_name=new_first,
                last_name=new_last,
                about=bio_part
            ))
        except Exception as e:
            await event.reply(f"❌ خطأ بتعيين الاسم والبايو المؤقت: {e}")
            return

        self.temp_bio_active = True
        await event.reply(f"✅ تم تعيين الاسم والبايو المؤقت لمدة {duration_sec} ثانية.")

        async def revert_profile():
            await asyncio.sleep(duration_sec)
            try:
                await self.client(functions.account.UpdateProfileRequest(
                    first_name=self.original_first_name,
                    last_name=self.original_last_name,
                    about=self.original_bio
                ))
                self.temp_bio_active = False
                self.original_first_name = None
                self.original_last_name = None
                self.original_bio = None
                await event.respond("⏰ انتهى الوقت! تم استرجاع الاسم والبايو الأصلي.")
            except Exception as e:
                print(f"خطأ بإرجاع الاسم والبايو الأصلي: {e}")

        self.temp_bio_task = asyncio.create_task(revert_profile())

    async def stop_temp_bio(self, event):
        if not self.temp_bio_active:
            await event.reply("⚠️ لا يوجد بايو واسم وقتي يعمل حالياً.")
            return
        if self.temp_bio_task:
            self.temp_bio_task.cancel()
            self.temp_bio_task = None
        self.temp_bio_active = False

        try:
            await self.client(functions.account.UpdateProfileRequest(
                first_name=self.original_first_name or "",
                last_name=self.original_last_name or "",
                about=self.original_bio or ""
            ))
            self.original_first_name = None
            self.original_last_name = None
            self.original_bio = None

            await event.reply("🛑 تم إيقاف البايو والاسم المؤقت وتم استرجاع القيم الأصلية.")
        except Exception as e:
            await event.reply(f"❌ خطأ بإيقاف البايو والاسم المؤقت: {e}")

# ======= END: بايو روتيتور متطور أقصى حد مع بايو واسم وقتي =======
# © 2025 الصعب | Developer: الصعب | All rights reserved.
# Tag: #الصعب

# ======= START: ربط أوامر UltimateBioRotator مع اليوزر بوت =======
# © 2025 الصعب | Developer: الصعب | All rights reserved.
# Tag: #الصعب

bio_rotator = UltimateBioRotator(client, default_interval=60)

@client.on(events.NewMessage(pattern=r'^\.اضف_بايو (.+)'))
async def handler_add_bio(event):
    await bio_rotator.add_bio(event)

@client.on(events.NewMessage(pattern=r'^\.عرض_البايوهات$'))
async def handler_show_bios(event):
    await bio_rotator.show_bios(event)

@client.on(events.NewMessage(pattern=r'^\.تشغيل_البايو$'))
async def handler_start_bio(event):
    await bio_rotator.start(event)

@client.on(events.NewMessage(pattern=r'^\.ايقاف_البايو$'))
async def handler_stop_bio(event):
    await bio_rotator.stop(event)

@client.on(events.NewMessage(pattern=r'^\.مسح_البايوهات$'))
async def handler_clear_bios(event):
    await bio_rotator.clear_bios(event)

@client.on(events.NewMessage(pattern=r'^\.مدة_بايو (\d+)$'))
async def handler_set_interval(event):
    await bio_rotator.set_interval(event)

@client.on(events.NewMessage(pattern=r'^\.حذف_بايو (\d+)$'))
async def handler_remove_bio(event):
    await bio_rotator.remove_bio(event)

@client.on(events.NewMessage(pattern=r'^\.اذهب_لبايو (\d+)$'))
async def handler_jump_to_bio(event):
    await bio_rotator.jump_to(event)

@client.on(events.NewMessage(pattern=r'^\.بايو_وقتي (.+)$'))
async def handler_temp_bio(event):
    await bio_rotator.set_temp_bio(event)

@client.on(events.NewMessage(pattern=r'^\.ايقاف_بايو_وقتي$'))
async def handler_stop_temp_bio(event):
    await bio_rotator.stop_temp_bio(event)

# ======= END: ربط أوامر UltimateBioRotator مع اليوزر بوت =======
# © 2025 الصعب | Developer: الصعب | All rights reserved.
# Tag: #الصعب
# ─────────── قائمة الأوامر ───────────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmds(event):
    if not await is_owner(event):
        return

    txt = """<b>💡 الأوامر:</b>
.اضف_بايو [نص البايو]
  ➤ إضافة بايو جديد لقائمة البايوات.

.عرض_البايوهات
  ➤ عرض كل البايوات المحفوظة.

.تشغيل_البايو
  ➤ بدء التغيير التلقائي للبايو بالتسلسل.

.ايقاف_البايو
  ➤ إيقاف التغيير التلقائي.

.مسح_البايوهات
  ➤ مسح جميع البايوات.

.مدة_بايو [ثواني]
  ➤ تعيين فترة التغيير بين البايوات (5 ثواني كحد أدنى).

.حذف_بايو [رقم]
  ➤ حذف بايو حسب رقمه في القائمة.

.اذهب_لبايو [رقم]
  ➤ تخطي فوراً إلى بايو معين.

.بايو_وقتي [نص البايو /MM:SS]
  ➤ تعيين بايو واسم مؤقتين لمدة معينة. مثال: `.بايو_وقتي الصعب كاسحكم /01:15`

.ايقاف_بايو_وقتي
  ➤ إيقاف البايو والاسم المؤقت واسترجاع القيم الأصلية. 
<code>.ايدي</code> – عرض الآيدي والمعلومات
<code>.البنق</code> – سرعة البوت ومدة التشغيل

<b>📝 أوامر المنشن:</b>
.منشن
↳ منشن كل أعضاء القروب برسائل ترحيب (واحدة كل 5 ثواني)

.لاتمنشن
↳ إيقاف أمر المنشن نهائياً

.منشن تفعيل
↳ تفعيل أمر المنشن بعد الإيقاف

.منشن حالة
↳ عرض حالة المنشن (مفعل ✅ / معطل 🛑) 

<code>.مؤقت توقف</code> – إيقاف الاسم المؤقت للحساب

<code>.اسم مؤقت قروب</code> – تفعيل اسم الوقت للقروب/القناة
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
# ─────────── تشغيل البوت ───────────
async def start_note():
    me=await client.get_me()
    await client.send_message("me",f"✅ البوت قيد التشغيل – @{me.username or me.first_name}")

print("🚀 البوت يعمل – المطور: الصعب")
client.start()
client.loop.run_until_complete(start_note())
client.run_until_disconnected()
