# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

import os, asyncio, datetime, random, tempfile
from moviepy.editor import VideoFileClip
from telethon import TelegramClient, events, utils, types
from telethon.sessions import StringSession
from telethon.errors import FileReferenceExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.channels import EditTitleRequest
from utils import get_dialog_counts, estimate_creation_date, load_json, save_json
from fingerprints import register as register_fingerprints

# ─────────── بيانات الاتصال ───────────
api_id = 22494292
api_hash = "0bd3915b6b1a0a64b168d0cc852a0e61"
session_string = "1ApWapzMBu2vP1lI4PdsGQ9_6rTxLliEW414P_J2ZUnVMOFMtNoxTT_cEf5OnB6eIn_nMi4qT0tNfpdFsiK7Uj841fyPrScL-HHT2o-NINEeWgp44lYy-XA_hDnjbMwDC3Ey9LuBtqOR6Ouwi0AgX5KBs5L6CCTTGlsqJEOGwaQqOBD1cXNIHwRHxVHNL79wDGIdY1NOl43p5t9T82h1xijWHKSjt7TO2nxyp2ioRncPCMWiTTbVmxqhZTK54h90RBT5zbPyFlW9CTG2xyEfaWv_x2zhtc1Nni8FUV9BHp1daoWG9c1M5ZIvRjJ_yh27GsnyCNg7kOU8pMf8UK7vZJq7PclGw3Og="
client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)
register_fingerprints(client)

# ─────────── متغيّرات ───────────
STATE_FILE = "state.json"
_state = load_json(STATE_FILE, {})
muted_private = set(_state.get("muted_private", []))
muted_groups = {int(k): set(v) for k, v in _state.get("muted_groups", {}).items()}
reaction_map = _state.get("reaction_map", {})  # user_id -> emoji
imitate_targets, last_imitated = set(_state.get("imitate_targets", [])), {}
welcome_cfg, group_name_tasks, original_titles = {}, {}, {}
name_task, prev_name, repeat_task = None, None, None

def save_state():
    data = {
        "muted_private": list(muted_private),
        "muted_groups": {str(k): list(v) for k, v in muted_groups.items()},
        "reaction_map": reaction_map,
        "imitate_targets": list(imitate_targets),
    }
    save_json(STATE_FILE, data)

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
#_____________امر تجربه___________
import asyncio
import random
from telethon import events

@client.on(events.NewMessage(pattern=r'^\.تهكير(?: (.+))?'))
async def ultra_long_scary_hack(event):
    target = event.pattern_match.group(1)

    if event.is_reply and not target:
        replied = await event.get_reply_message()
        if replied.sender:
            user = replied.sender
        else:
            user = None
    elif target:
        try:
            user = await client.get_entity(target)
        except:
            user = None
    else:
        user = None

    if not user:
        return await event.reply("❌ لم يتم العثور على المستخدم. رد على شخص أو اكتب يوزره.\nمثال: `.تهكير @username`")

    name = user.first_name or "شخص"
    username = f"@{user.username}" if user.username else name

    fake_ip = ".".join(str(random.randint(10, 255)) for _ in range(4))
    fake_country = random.choice(["الولايات المتحدة الأمريكية 🇺🇸", "روسيا 🇷🇺", "كوريا الشمالية 🇰🇵", "الصين 🇨🇳", "إيران 🇮🇷"])
    fake_phone = "+9647" + "".join(str(random.randint(0, 9)) for _ in range(8))

    long_scary_codes = [
        "▂▃▄▅▆▇█▓▒░ INITIALIZING SYSTEM BREACH ░▒▓█▇▆▅▄▃▂",
        "↳ Connecting to dark net nodes...",
        "↳ Establishing secure shell tunnels...",
        "↳ Launching zero-day exploits...",
        "↳ Scanning ports [1-65535]...",
        "↳ Injecting malicious payloads...",
        "↳ Bypassing firewall and antivirus...",
        "↳ Decrypting stored passwords (RSA-4096)...",
        "↳ Capturing keystrokes and mouse movements...",
        "↳ Accessing camera and microphone streams...",
        "↳ Extracting private chats and media files...",
        "↳ Downloading contacts and browsing history...",
        "↳ Uploading data to dark web server...",
        "↳ Encrypting logs to avoid detection...",
        "↳ Generating fake traffic to mask activity...",
        "↳ Zero-trace data wipe in progress...",
        "↳ Executing remote commands...",
        "↳ SYSTEM BREACH SUCCESSFUL!",
        "↳ Target IP: {}".format(fake_ip),
        "↳ Location: {}".format(fake_country),
        "↳ Phone number linked: {}".format(fake_phone),
        "▂▃▄▅▆▇█▓▒░ BREACH COMPLETE ░▒▓█▇▆▅▄▃▂"
    ]

    try:
        msg = event.message

        await msg.edit(f"💀 بدء تهكير {username} ...\n")
        await asyncio.sleep(2)

        for code in long_scary_codes:
            # نعرض الكود مع تأثير أسطر مشفرة عشوائية
            fake_encrypted = ''.join(random.choice('0123456789ABCDEF') for _ in range(40))
            display = f"<pre>{code}\n{fake_encrypted}</pre>"
            await msg.edit(display, parse_mode="html")
            await asyncio.sleep(3)  # زيادة الوقت عشان تطول الرعب

        # بعد عرض الأكواد
        await msg.edit("⚠️ <b>تم تهكير الحساب بنجاح</b> ⚠️\n")
        await asyncio.sleep(2)
        await msg.edit("⏳ جاري سحب الصور ...")
        await asyncio.sleep(3)
        await msg.edit("✅ تم سحب الصور")
        await asyncio.sleep(2)
        await msg.edit("⏳ جاري سحب جميع معلومات الجهاز ...")
        await asyncio.sleep(3)
        await msg.edit("✅ تم سحب جميع معلومات الجهاز")
        await asyncio.sleep(2)
        await msg.edit("⏳ جاري نشر الصور ...")
        await asyncio.sleep(3)
        await msg.edit("✅ تم نشر الصور")
        await asyncio.sleep(2)

        fake_link = "http://darkweb-secret-site.onion/fake-leak"
        await msg.edit(f"🚨 جاري رفع الصور إلى الموقع التالي:\n<a href='{fake_link}'>{fake_link}</a>", parse_mode="html", link_preview=False)
        await asyncio.sleep(4)

        await msg.edit("🔥 جارييييي فرمتتت التلفون ...")
        await asyncio.sleep(6)

        await msg.delete()

    except Exception as e:
        print("خطأ في التهكير:", e)
#_______ازعاج ايموجي ________from telethon import TelegramClient, events
from telethon import events, functions, types

reaction_map = {}  # user_id: emoji

@client.on(events.NewMessage(pattern=r"^\.ازعاج(.+)"))
async def enable_reaction(event):
    if not event.is_reply:
        await event.reply("❗ لازم ترد على رسالة الشخص وتكتب الأمر مع الإيموجي\nمثال: `.ازعاج😁`", delete_in=5)
        return

    try:
        await event.delete()
    except:
        pass

    emoji = event.pattern_match.group(1).strip()
    replied = await event.get_reply_message()
    user_id = replied.sender_id

    reaction_map[user_id] = emoji
    await event.reply(f"✅ تم تفعيل الإزعاج بـ {emoji} لهذا المستخدم.", delete_in=3)

@client.on(events.NewMessage(pattern=r"^\.لاتزعج$"))
async def disable_reaction(event):
    if not event.is_reply:
        await event.reply("❗ لازم ترد على رسالة الشخص حتى أوقف التفاعل.", delete_in=5)
        return

    try:
        await event.delete()
    except:
        pass

    replied = await event.get_reply_message()
    user_id = replied.sender_id

    if user_id in reaction_map:
        del reaction_map[user_id]
        await event.reply("🛑 تم إيقاف الإزعاج لهذا الشخص.", delete_in=3)
    else:
        await event.reply("ℹ️ هذا الشخص ما مفعّل عليه إزعاج.", delete_in=3)

@client.on(events.NewMessage)
async def auto_reaction(event):
    try:
        if event.out or not event.sender_id:
            return

        emoji = reaction_map.get(event.sender_id)
        if emoji:
            await client(functions.messages.SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[types.InputReactionEmoji(emoticon=emoji)],
            ))
    except Exception as e:
        print(f"❌ خطأ أثناء إرسال التفاعل: {e}")
#_______________________
from telethon import TelegramClient, events
import datetime

# تعريف client هنا
# client = TelegramClient("session_name", api_id, api_hash)

sleep_mode = False
sleep_reason = ""
sleep_start = None
custom_reply = ""

async def is_owner(event):
    return (await client.get_me()).id == event.sender_id

@client.on(events.NewMessage(pattern=r'^\.سليب(?: (.+))?$'))
async def sleep_command(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply

    if not await is_owner(event):
        return

    sleep_mode = True
    sleep_reason = event.pattern_match.group(1) or "غير متوفر حالياً"
    sleep_start = datetime.datetime.now()
    custom_reply = ""

    await event.delete()
    msg = await event.respond(f"""🟡 <b>تم تفعيل وضع السليب</b>
💬 <b>السبب:</b> {sleep_reason}
⏱️ <b>منذ:</b> 0 دقيقة و 0 ثانية""", parse_mode="html")
    asyncio.create_task(delete_after(msg, 2))

@client.on(events.NewMessage(pattern=r'^\.سكون(?: (.+))?$'))
async def static_sleep_command(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply

    if not await is_owner(event):
        return

    sleep_mode = True
    custom_reply = event.pattern_match.group(1) or "🚫 غير متاح حالياً."
    sleep_reason = "سكون ثابت"
    sleep_start = datetime.datetime.now()

    await event.delete()
    msg = await event.respond("🔕 تم تفعيل السكون برسالة ثابتة.")
    asyncio.create_task(delete_after(msg, 2))

@client.on(events.NewMessage(incoming=True))
async def on_private_message(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply

    if not sleep_mode or await is_owner(event):
        return
    if event.is_group or event.is_channel:
        return

    async def reply_now():
        if custom_reply:
            text = custom_reply
        else:
            elapsed = datetime.datetime.now() - sleep_start
            total = int(elapsed.total_seconds())
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            elapsed_str = f"{h} ساعة و {m} دقيقة و {s} ثانية" if h else f"{m} دقيقة و {s} ثانية"
            text = f"🔕 المستخدم غير نشط منذ {elapsed_str}\n💬 السبب: {sleep_reason}"

        await event.reply(text)

    asyncio.create_task(reply_now())  # سريع وما يعلق

@client.on(events.NewMessage(outgoing=True))
async def cancel_sleep(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply

    if not sleep_mode:
        return

    if event.raw_text.startswith(".سليب") or event.raw_text.startswith(".سكون"):
        return  # لا تلغي السكون إذا هو أمر تفعيل

    elapsed = datetime.datetime.now() - sleep_start
    total = int(elapsed.total_seconds())
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    elapsed_str = f"{h} ساعة و {m} دقيقة و {s} ثانية" if h else f"{m} دقيقة و {s} ثانية"

    await client.send_message("me", f"""🔔 <b>تم إلغاء وضع السكون</b>
📝 <b>السبب:</b> {sleep_reason}
⏱️ <b>استمر:</b> {elapsed_str}
👤 <b>تم الإلغاء بإرسال رسالة.</b>""", parse_mode="html")

    sleep_mode = False
    sleep_reason = ""
    sleep_start = None
    custom_reply = ""

    msg = await event.respond("❌ تم إلغاء السكون.")
    asyncio.create_task(delete_after(msg, 2))

# حذف تلقائي لأي رسالة بعد وقت
async def delete_after(msg, seconds):
    await asyncio.sleep(seconds)
    try:
        await msg.delete()
    except:
        pass
# ─────────── الكتم ───────────
@client.on(events.NewMessage(pattern=r"^\.كتم$", func=lambda e: e.is_reply))
async def cmd_mute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id,set())).add(r.sender_id)
    save_state()
    await qedit(event,"🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r"^\.إلغاء الكتم$", func=lambda e: e.is_reply))
async def cmd_unmute(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id,set())).discard(r.sender_id)
    save_state()
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
    save_state()
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
    save_state()
    await qedit(event,f"✅ تفعيل التقليد لـ {r.sender_id}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف التقليد$"))
async def cmd_imitate_off(event):
    if not await is_owner(event): return
    imitate_targets.clear(); last_imitated.clear()
    save_state()
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
@client.on(events.NewMessage(pattern=r"^\.(?:الاوامر|مساعدة)$"))
async def cmds(event):
    if not await is_owner(event):
        return

    try:
        with open("COMMANDS.md", "r", encoding="utf-8") as f:
            txt = f.read()
        await event.respond(txt, parse_mode="html")
        await event.delete()
    except Exception as e:
        await event.reply(f"❌ خطأ في جلب الأوامر: {e}")
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def check(event):
    txt = "✅ البوت يعمل"
    await event.edit(txt, parse_mode="html")

# تشغيل البرنامج

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

async def main():
    print("تشغيل البوت…")
    await client.start()
    print("✅ البوت يعمل الآن.")

    # لم نعد نشغل update_name()

    await client.run_until_disconnected()


@client.on(events.NewMessage(pattern=r'^\.معلومات(?:\s+(.*))?$'))
async def user_info(event):
    if not await is_owner(event):
        return
    try:
        try:
            await event.delete()
        except Exception:
            pass

        target = event.pattern_match.group(1)
        if target:
            try:
                user = await client.get_entity(target.strip())
            except Exception:
                return await event.respond("❌ لم أستطع جلب الحساب.")
        elif event.is_reply:
            reply = await event.get_reply_message()
            user = await reply.get_sender()
        else:
            user = await client.get_me()

        me = await client.get_me()
        info_lines = [
            f"👤 <b>الاسم الكامل:</b> {utils.get_display_name(user)}",
            f"🆔 <b>ID:</b> <code>{user.id}</code>",
            f"🔗 <b>Username:</b> {('@' + user.username) if user.username else 'غير محدد'}",
            f"📞 <b>الرقم:</b> {getattr(user, 'phone', None) or 'غير متوفر'}",
        ]

        if user.id == me.id:
            groups, channels = await get_dialog_counts(client)
            info_lines.append(f"👥 <b>عدد المجموعات:</b> {groups}")
            info_lines.append(f"📢 <b>عدد القنوات:</b> {channels}")

        last_seen = "غير متوفر"
        try:
            if isinstance(user.status, types.UserStatusOnline):
                last_seen = "متصل الآن"
            elif isinstance(user.status, types.UserStatusOffline):
                last_seen = user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
        info_lines.append(f"⏱️ <b>آخر ظهور:</b> {last_seen}")

        creation = estimate_creation_date(user.id)
        info_lines.append(
            f"📅 <b>تاريخ الإنشاء التقريبي:</b> {creation.strftime('%Y-%m-%d')}"
        )

        await event.respond("\n".join(info_lines), parse_mode="html")
    except Exception as e:
        await event.respond(f"❌ خطأ في أمر معلومات: {e}")



@client.on(events.NewMessage(pattern=r'^\.غادر$'))
async def leave_group(event):
    if not await is_owner(event):
        return
    if not (event.is_group or event.is_channel):
        return

    chat = await event.get_chat()
    try:
        input_peer = await event.get_input_chat()

        try:
            if event.is_channel or getattr(chat, 'megagroup', False):
                await client(functions.channels.DeleteHistoryRequest(channel=input_peer, max_id=0))
            else:
                await client(functions.messages.DeleteHistoryRequest(peer=input_peer, max_id=0, revoke=False))
        except Exception:
            pass

        if event.is_channel or getattr(chat, 'megagroup', False):
            await client(functions.channels.LeaveChannelRequest(channel=input_peer))
        else:
            await client(functions.messages.DeleteChatUserRequest(chat_id=chat.id, user_id='me'))
    except Exception as e:
        await client.send_message("me", f"❌ فشل المغادرة: {e}")
    finally:
        await event.delete()


@client.on(events.NewMessage(pattern=r'^\.تحويل\s+(فيديو|بصمه|صوت)$'))
async def convert_media(event):
    if not await is_owner(event):
        return
    if not event.is_reply:
        return await event.reply("↯︙يجب الرد على فيديو أو صوت.")

    target = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not reply.media:
        return await event.reply("↯︙الرسالة لا تحتوي ميديا.")

    msg = await event.reply("⏳ جارٍ التحويل ...")
    src = await reply.download_media(file=tempfile.mktemp())
    dst_file = tempfile.mktemp()

    loop = asyncio.get_running_loop()

    try:
        if target == 'بصمه':
            dst_file += '.ogg'

            def convert():
                clip = VideoFileClip(src)
                clip.audio.write_audiofile(dst_file, codec='libopus', bitrate='96k')
                clip.close()

            await loop.run_in_executor(None, convert)
            await client.send_file(event.chat_id, dst_file, voice_note=True)

        elif target == 'صوت':
            dst_file += '.mp3'

            def convert():
                clip = VideoFileClip(src)
                clip.audio.write_audiofile(dst_file)
                clip.close()

            await loop.run_in_executor(None, convert)
            await client.send_file(event.chat_id, dst_file)

        else:  # فيديو
            dst_file += '.mp4'

            def convert():
                clip = VideoFileClip(src)
                clip.write_videofile(dst_file, codec='libx264', audio_codec='aac')
                clip.close()

            await loop.run_in_executor(None, convert)
            await client.send_file(event.chat_id, dst_file)

        await msg.edit("✅ تم التحويل")
        await event.delete()
    except Exception as e:
        await msg.edit(f"❌ خطأ في التحويل: {e}")
    finally:
        try:
            os.remove(src)
        except Exception:
            pass
        try:
            os.remove(dst_file)
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
