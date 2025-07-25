# -*- coding: utf-8 -*-
"""
بوت تيليجرام متكامل (2025)
المطور: الصعب
حقوق النشر: © 2025 الصعب. جميع الحقوق محفوظة.
"""

# ─────────── الاستيراد العام ───────────
import os
import asyncio
import datetime
import random
import tempfile

from telethon import TelegramClient, events, functions, types, utils
from telethon.sessions import StringSession
from telethon.errors import FileReferenceExpiredError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.channels import EditTitleRequest

# ─────────── بيانات الاتصال ───────────
api_id = 22494292
api_hash = "0bd3915b6b1a0a64b168d0cc852a0e61"
session_string = "1ApWapzMBu2vP1lI4PdsGQ9_6rTxLliEW414P_J2ZUnVMOFMtNoxTT_cEf5OnB6eIn_nMi4qT0tNfpdFsiK7Uj841fyPrScL-HHT2o-NINEeWgp44lYy-XA_hDnjbMwDC3Ey9LuBtqOR6Ouwi0AgX5KBs5L6CCTTGlsqJEOGwaQqOBD1cXNIHwRHxVHNL79wDGIdY1NOl43p5t9T82h1xijWHKSjt7TO2nxyp2ioRncPCMWiTTbVmxqhZTK54h90RBT5zbPyFlW9CTG2xyEfaWv_x2zhtc1Nni8FUV9BHp1daoWG9c1M5ZIvRjJ_yh27GsnyCNg7kOU8pMf8UK7vZJq7PclGw3Og="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# ─────────── المتغيّرات العامة ───────────
muted_private, muted_groups = set(), {}
sleep_mode, sleep_reason, sleep_start, custom_reply = False, "", None, ""
reaction_map = {}
mention_enabled = True

# ─────────── دوال مساعدة ───────────
def baghdad_time(fmt="%I:%M %p"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime(fmt)

async def is_owner(event):
    me = await client.get_me()
    return event.sender_id == me.id

async def qedit(event, txt, delay=2):
    await event.edit(txt, parse_mode="html")
    await asyncio.sleep(delay)
    await event.delete()

# ─────────── أوامر بسيطة ───────────
@client.on(events.NewMessage(pattern=r'^\.فحص$'))
async def check_status(event):
    if not await is_owner(event): return
    await event.edit("✅ البوت يعمل بنجاح.")

@client.on(events.NewMessage(pattern=r'^\.ايدي$'))
async def get_id(event):
    if not await is_owner(event): return
    if event.is_reply:
        r = await event.get_reply_message()
        await qedit(event, f"🆔 <code>{r.sender_id}</code>")
    else:
        await qedit(event, f"🆔 آيديك: <code>{event.sender_id}</code>")

@client.on(events.NewMessage(pattern=r'^\.البنق$'))
async def ping(event):
    if not await is_owner(event): return
    start = datetime.datetime.now()
    m = await event.edit("🏓 جاري القياس...")
    diff = (datetime.datetime.now() - start).microseconds / 1000
    await m.edit(f"🏓 <b>{diff:.2f}ms</b>", parse_mode="html")
    await asyncio.sleep(4)
    await m.delete()

# ─────────── أوامر السكون ───────────
@client.on(events.NewMessage(pattern=r'^\.سليب(?: (.+))?$'))
async def sleep_command(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply
    if not await is_owner(event): return
    sleep_mode = True
    sleep_reason = event.pattern_match.group(1) or "غير متوفر حالياً"
    sleep_start = datetime.datetime.now()
    custom_reply = ""
    await event.delete()
    msg = await event.respond(f"🟡 تم تفعيل السكون
💬 السبب: {sleep_reason}")
    await asyncio.sleep(2)
    await msg.delete()

@client.on(events.NewMessage(pattern=r'^\.سكون(?: (.+))?$'))
async def static_sleep_command(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply
    if not await is_owner(event): return
    sleep_mode = True
    sleep_reason = "سكون ثابت"
    sleep_start = datetime.datetime.now()
    custom_reply = event.pattern_match.group(1) or "🚫 غير متاح حالياً."
    await event.delete()
    msg = await event.respond("🔕 تم تفعيل السكون برسالة ثابتة.")
    await asyncio.sleep(2)
    await msg.delete()

@client.on(events.NewMessage(incoming=True))
async def auto_reply_sleep(event):
    if not sleep_mode or await is_owner(event): return
    if event.is_group or event.is_channel: return
    if custom_reply:
        await event.reply(custom_reply)
    else:
        elapsed = datetime.datetime.now() - sleep_start
        total = int(elapsed.total_seconds())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        elapsed_str = f"{h} ساعة و {m} دقيقة و {s} ثانية" if h else f"{m} دقيقة و {s} ثانية"
        text = f"🔕 المستخدم غير نشط منذ {elapsed_str}
💬 السبب: {sleep_reason}"
        await event.reply(text)

@client.on(events.NewMessage(outgoing=True))
async def cancel_sleep(event):
    global sleep_mode, sleep_reason, sleep_start, custom_reply
    if not sleep_mode: return
    if event.raw_text.startswith(".سليب") or event.raw_text.startswith(".سكون"): return
    sleep_mode = False
    await client.send_message("me", f"🔔 تم إلغاء السكون
📝 السبب: {sleep_reason}")

# ─────────── الكتم ───────────
@client.on(events.NewMessage(pattern=r'^\.كتم$', func=lambda e: e.is_reply))
async def mute_user(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.setdefault(event.chat_id, set())).add(r.sender_id)
    await qedit(event, "🔇 تم كتمه.")

@client.on(events.NewMessage(pattern=r'^\.الغاء الكتم$', func=lambda e: e.is_reply))
async def unmute_user(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    (muted_private if event.is_private else muted_groups.get(event.chat_id, set())).discard(r.sender_id)
    await qedit(event, "🔊 تم فك الكتم.")

@client.on(events.NewMessage(incoming=True))
async def auto_delete_muted(event):
    if (event.is_private and event.sender_id in muted_private) or        (event.chat_id in muted_groups and event.sender_id in muted_groups[event.chat_id]):
        return await event.delete()

# ─────────── إزعاج بالإيموجي ───────────
@client.on(events.NewMessage(pattern=r'^\.ازعاج(.+)', func=lambda e: e.is_reply))
async def annoy_user(event):
    if not await is_owner(event): return
    emoji = event.pattern_match.group(1).strip()
    r = await event.get_reply_message()
    reaction_map[r.sender_id] = emoji
    await qedit(event, f"✅ تم تفعيل الإزعاج بـ {emoji}")

@client.on(events.NewMessage(pattern=r'^\.لاتزعج$', func=lambda e: e.is_reply))
async def stop_annoy_user(event):
    if not await is_owner(event): return
    r = await event.get_reply_message()
    if reaction_map.pop(r.sender_id, None):
        await qedit(event, "🛑 تم إيقاف الإزعاج لهذا الشخص.")
    else:
        await qedit(event, "ℹ️ هذا الشخص غير مفعّل عليه إزعاج.")

@client.on(events.NewMessage)
async def auto_react(event):
    emoji = reaction_map.get(event.sender_id)
    if emoji:
        try:
            await client(functions.messages.SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)],
            ))
        except: pass

# ─────────── المنشن الجماعي ───────────
mention_messages = [
    "هلا بالغالي 🌸", "نورتنا 🌟", "شلونك اليوم؟ 💬", "حيّاك الله 🖤",
    "أهلاً وسهلاً ☕", "وينك مختفي؟ 👀", "يلا تعال سولف 😁"
]

@client.on(events.NewMessage(pattern=r'^\.منشن$'))
async def mention_all(event):
    if not await is_owner(event): return
    if not event.is_group:
        return await qedit(event, "❌ هذا الأمر فقط للمجموعات")
    users = [u async for u in client.iter_participants(event.chat_id) if not u.bot and not u.deleted]
    if not users:
        return await qedit(event, "⚠️ لا يوجد أعضاء.")
    await event.edit(f"🚀 منشن {len(users)} عضو جاري...")
    for user in users:
        msg = random.choice(mention_messages)
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name or 'عضو'}</a>"
        try:
            await client.send_message(event.chat_id, f"{msg} {mention}", parse_mode="html")
            await asyncio.sleep(4)
        except:
            continue
    await event.respond("✅ انتهى المنشن.")

# ─────────── حفظ الوسائط المؤقتة تلقائيًا ───────────
@client.on(events.NewMessage(incoming=True))
async def save_temporary_media(event):
    if not event.is_private: return
    media = event.media
    if not media: return
    if getattr(media, 'ttl_seconds', None):
        try:
            await client.send_file("me", media, caption="📥 تم حفظ الوسائط المؤقتة تلقائيًا.")
        except Exception as e:
            print("⚠️ فشل في الحفظ المؤقت:", e)

# ─────────── تشغيل البوت ───────────
async def main():
    print("🔌 جاري تشغيل البوت...")
    await client.start()
    print("✅ البوت يعمل الآن.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
