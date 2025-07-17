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
api_id = 22494292
api_hash = "0bd3915b6b1a0a64b168d0cc852a0e61"
session_string = "1ApWapzMBuwhnB7Yb5_vQy1Alft2Px4dlmXcxsJuldgBe_RfIYV3zFbF2JoP51Hf5qqPA94f2xZIeufurE-DnjKozg0QTQjSxKEUPeHYu8Yv2QxcfzE9tzDc7RqUBgcGfu57K5EEHomrfp51R9S_Hb3Cu2-w8bNZFnyNSFDKxiKUq733Y1XgrQk7COzYd4UIiHk-VX8mOI37RSvM9YsGUKMiQ544MguM6UWNVYS4sDccxjJe4RTjdMYbc8sGPT_d1lvkq_k9rbC1XC_3cMAbzeQpYnWSQLdL4YuBz1xuwRWhQaFGQn8zxuOmdS1SAOZx5KHo2WNRELKqTMXEQGGysGUdiynD2quk="
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
        #_______ازعاج ايموجي ________
from telethon import events
import asyncio

# تخزين المستخدمين مع الإيموجي (حتى 50 مستخدم فقط)
reactions_db = dict()
MAX_ANNOY = 50

@client.on(events.NewMessage(pattern=r"\.ازعاج (.+)"))
async def start_annoying(event):
    if not event.is_reply:
        return await event.reply("↯ الرجاء الرد على رسالة المستخدم لتفعيل الإزعاج.")
    
    if len(reactions_db) >= MAX_ANNOY:
        await event.edit(f"⚠️ الحد الأقصى للمستخدمين المزعجين هو {MAX_ANNOY}.")
        await asyncio.sleep(1)
        await event.delete()
        return

    emoji = event.pattern_match.group(1).strip()
    replied_msg = await event.get_reply_message()
    user_id = replied_msg.sender_id

    if user_id in reactions_db:
        await event.edit("⚠️ هذا المستخدم مفعّل عليه الإزعاج بالفعل.")
        await asyncio.sleep(1)
        await event.delete()
        return

    reactions_db[user_id] = emoji
    await event.edit(f"✅ تم تفعيل الإزعاج على المستخدم: <a href='tg://user?id={user_id}'>هنا</a> بالإيموجي: {emoji}", parse_mode="html")
    await asyncio.sleep(1)
    await event.delete()

@client.on(events.NewMessage(pattern=r"\.لاتزعج"))
async def stop_annoying(event):
    if not event.is_reply:
        return await event.reply("↯ الرجاء الرد على رسالة المستخدم لإلغاء الإزعاج.")
    
    replied_msg = await event.get_reply_message()
    user_id = replied_msg.sender_id
    
    if user_id in reactions_db:
        reactions_db.pop(user_id)
        await event.edit(f"✅ تم إلغاء الإزعاج عن المستخدم: <a href='tg://user?id={user_id}'>هنا</a>", parse_mode="html")
        await asyncio.sleep(1)
        await event.delete()
    else:
        await event.edit("⚠️ هذا المستخدم غير مفعّل عليه الإزعاج.")
        await asyncio.sleep(1)
        await event.delete()

@client.on(events.NewMessage)
async def react_to_annoyed_users(event):
    user_id = event.sender_id
    emoji = reactions_db.get(user_id)
    if emoji:
        try:
            await event.react(emoji)
        except Exception:
            pass  # تجاهل الأخطاء المحتملة
# ───────── اسم مؤقت  ───────────

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
# ======= START: بايو روتيتور مطور 🔁 مع بايو واسم وقتي - تاج راسي الصعب =======
# © 2025 الصعب | Developer: الصعب | جميع الحقوق محفوظة
# Tag: #الصعب
# =======

import asyncio
from telethon import events, functions

class BioRotator:
    def __init__(self, client, interval=60):
        self.client = client
        self.bios = []
        self.index = 0
        self.interval = interval
        self.task = None
        self.running = False
        self.temp_task = None
        self.temp_active = False
        self.original = {}

    async def edit_del(self, event, text, delay=3):
        await event.edit(text)
        await asyncio.sleep(delay)
        await event.delete()

    async def start(self, event):
        if self.running:
            return await self.edit_del(event, "⚠️ شغّال من قبل.")
        if not self.bios:
            return await self.edit_del(event, "⚠️ لا توجد بايوهات.")
        self.running = True
        self.task = asyncio.create_task(self.loop_bio())
        await self.edit_del(event, f"✅ بدأ التغيير كل {self.interval} ثانية.")

    async def stop(self, event):
        if not self.running:
            return await self.edit_del(event, "⚠️ غير مفعل.")
        self.running = False
        self.task.cancel()
        await self.edit_del(event, "🛑 تم الإيقاف.")

    async def loop_bio(self):
        while self.running:
            try:
                await self.client(functions.account.UpdateProfileRequest(about=self.bios[self.index]))
                self.index = (self.index + 1) % len(self.bios)
            except: pass
            await asyncio.sleep(self.interval)

    async def add(self, event):
        bio = event.pattern_match.group(1).strip()
        if not bio:
            return await self.edit_del(event, "❌ لا يمكن إضافة بايو فارغ.")
        self.bios.append(bio)
        await self.edit_del(event, f"✅ تم إضافة البايو\nعدد البايوهات: {len(self.bios)}")

    async def show(self, event):
        if not self.bios:
            return await self.edit_del(event, "⚠️ القائمة فارغة.")
        msg = "\n".join([f"{i+1}. {x}" for i, x in enumerate(self.bios)])
        await event.edit(f"📋 البايوهات:\n\n{msg}")
        await asyncio.sleep(10)
        await event.delete()

    async def clear(self, event):
        self.bios.clear()
        self.index = 0
        await self.edit_del(event, "🗑️ تم المسح.")

    async def interval_set(self, event):
        try:
            sec = int(event.pattern_match.group(1))
            if sec < 5:
                return await self.edit_del(event, "❌ أقل شيء 5 ثواني.")
            self.interval = sec
            if self.running:
                await self.stop(event)
                await self.start(event)
            else:
                await self.edit_del(event, f"⏱️ المدة الآن {sec} ثانية.")
        except:
            await self.edit_del(event, "❌ استخدم: `.مدة_بايو 60`")

    async def remove(self, event):
        try:
            i = int(event.pattern_match.group(1)) - 1
            if i < 0 or i >= len(self.bios):
                return await self.edit_del(event, "❌ رقم غير صالح.")
            removed = self.bios.pop(i)
            await self.edit_del(event, f"🗑️ حذف: {removed}")
        except:
            await self.edit_del(event, "❌ استخدم: `.حذف_بايو 2`")

    async def jump(self, event):
        try:
            i = int(event.pattern_match.group(1)) - 1
            if i < 0 or i >= len(self.bios):
                return await self.edit_del(event, "❌ رقم غير صالح.")
            self.index = i
            await self.edit_del(event, f"↪️ بدأ من البايو {i+1}")
        except:
            await self.edit_del(event, "❌ استخدم: `.اذهب_لبايو 3`")

    async def temp(self, event):
        if self.temp_active:
            return await self.edit_del(event, "⚠️ بايو مؤقت مفعل، أوقفه أولاً.")
        text = event.pattern_match.group(1)
        if '/' not in text:
            return await self.edit_del(event, "❌ استخدم `.بايو_وقتي نص /MM:SS`")
        bio, t = text.rsplit('/', 1)
        try:
            m, s = map(int, t.split(':'))
            sec = m*60 + s
        except:
            return await self.edit_del(event, "❌ وقت غير صحيح.")

        user = await self.client.get_me()
        self.original = {
            "first": user.first_name or "",
            "last": user.last_name or "",
            "bio": user.about or ""
        }

        try:
            await self.client(functions.account.UpdateProfileRequest(
                first_name=bio, last_name="", about=bio
            ))
            await self.edit_del(event, f"✅ تم التعيين مؤقتًا لمدة {sec} ثانية.")
        except Exception as e:
            return await self.edit_del(event, f"❌ {e}")

        self.temp_active = True

        async def revert():
            await asyncio.sleep(sec)
            try:
                await self.client(functions.account.UpdateProfileRequest(
                    first_name=self.original["first"],
                    last_name=self.original["last"],
                    about=self.original["bio"]
                ))
            except: pass
            self.temp_active = False

        self.temp_task = asyncio.create_task(revert())

    async def stop_temp(self, event):
        if not self.temp_active:
            return await self.edit_del(event, "⚠️ لا يوجد بايو مؤقت.")
        if self.temp_task:
            self.temp_task.cancel()
        try:
            await self.client(functions.account.UpdateProfileRequest(
                first_name=self.original["first"],
                last_name=self.original["last"],
                about=self.original["bio"]
            ))
        except: pass
        self.temp_active = False
        await self.edit_del(event, "🛑 تم إيقاف البايو المؤقت.")

# ======= END: كود الصعب 🔥 =======

# ✅ ربط الأوامر مع البوت
bio = BioRotator(client)

@client.on(events.NewMessage(pattern=r'^\.اضف_بايو (.+)'))
async def _(e): await bio.add(e)

@client.on(events.NewMessage(pattern=r'^\.عرض_البايوهات$'))
async def _(e): await bio.show(e)

@client.on(events.NewMessage(pattern=r'^\.تشغيل_البايو$'))
async def _(e): await bio.start(e)

@client.on(events.NewMessage(pattern=r'^\.ايقاف_البايو$'))
async def _(e): await bio.stop(e)

@client.on(events.NewMessage(pattern=r'^\.مسح_البايوهات$'))
async def _(e): await bio.clear(e)

@client.on(events.NewMessage(pattern=r'^\.مدة_بايو (\d+)$'))
async def _(e): await bio.interval_set(e)

@client.on(events.NewMessage(pattern=r'^\.حذف_بايو (\d+)$'))
async def _(e): await bio.remove(e)

@client.on(events.NewMessage(pattern=r'^\.اذهب_لبايو (\d+)$'))
async def _(e): await bio.jump(e)

@client.on(events.NewMessage(pattern=r'^\.بايو_وقتي (.+)$'))
async def _(e): await bio.temp(e)

@client.on(events.NewMessage(pattern=r'^\.ايقاف_بايو_وقتي$'))
async def _(e): await bio.stop_temp(e)
# ─────────── قائمة الأوامر ───────────
@client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
async def cmds(event):
    if not await is_owner(event):
        return

    txt = """<b>💡 الأوامر:</b>.اضف_بايو [نص]           ➤ إضافة بايو
.عرض_البايوهات           ➤ عرض البايوهات (يحذف بعد 10 ثواني)
.تشغيل_البايو            ➤ بدء تغيير تلقائي
.ايقاف_البايو            ➤ إيقاف التغيير
.مسح_البايوهات           ➤ حذف الكل
.مدة_بايو [ثواني]         ➤ تغيير المدة
.حذف_بايو [رقم]           ➤ حذف واحد
.اذهب_لبايو [رقم]         ➤ تخطي إلى بايو معين
.بايو_وقتي نص /MM:SS     ➤ اسم + بايو مؤقت
.ايقاف_بايو_وقتي          ➤ استرجاع الأصلي 
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

<code>.كتم</code> (رد) – كتم
<code>.الغاء الكتم</code> (رد) – فك كتم
<code>.قائمة الكتم</code> – عرض الكتم
<code>.مسح الكتم</code> – مسح الكتم
اوامر الازعاج:
.ازعاج <ايموجي>  → رد على شخص لإزعاجه بالإيموجي.
.لاتزعج         → رد على نفس الشخص لإيقاف الإزعاج.
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
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def check(event):
    txt = "✅ البوت يعمل"
    await event.edit(txt, parse_mode="html")

# تشغيل البرنامج
from telethon import events

@client.on(events.NewMessage(pattern=r"\.فحص"))
async def check(event):
    txt = "✅ البوت يعمل"
    await event.edit(txt, parse_mode="html")

# ← دالة تغيير الاسم لازم تكون موجودة قبل main()
async def update_name():
    while True:
        # هنا تضيف كود تغيير الاسم حسب رغبتك
        await asyncio.sleep(60)

# تشغيل البرنامج
import asyncio

async def main():
    print("تشغيل البوت…")
    await client.start()
    print("✅ البوت يعمل الآن.")

    asyncio.create_task(update_name())  # شغل مهمة تحديث الاسم

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
