import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
import os, datetime

# بيانات الاتصال
api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session_string = "1ApWapzMBuyTr7Rk9WbYIM9E-iV4GSACk3dJ48htXIBKOyxDPQNnTcVadWGL67EEoISuOdE4Ki_UL_n6DK5dd2xpyc9fowjBJAW_6Kis1o_36oNVcj9AxEkZKSZ40oxQvkWpnCfOCRVhvkSNGB74x7QhwtwcV8yc69JCOgQmpcwWCXMyfMbFeapSZZnLRbytp0SnqyqUY2N8tpghnkja4q1uYRFLefrfbmmRj4576rIXlT2nM7ePzvpqQPrs7GCcGtigzGwGrxguVi20D3tjGQMaQaNeGMWFCvfYw-GCLJYXvEXmtNbrxJcszdBSWo2V35TeFjfQ03fqPlUo_tYgNKpHuJXtoD00="

client = TelegramClient(StringSession(session_string), api_id, api_hash)
os.makedirs("downloads", exist_ok=True)

# المتغيرات
muted_private = set()
muted_groups = {}
welcome_enabled = {}
welcome_message = {}
clone_list = set()
auto_name = True  # متغير التحكم بتشغيل الاسم التلقائي

# --------- تحديث الاسم الوقتي (بتوقيت العراق) ---------
async def update_name_loop():
    while True:
        if auto_name:
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            name = now.strftime('%I:%M')
            try:
                await client(UpdateProfileRequest(first_name=name))
            except Exception:
                pass
        await asyncio.sleep(60)

# --------- تشغيل/ايقاف تحديث الاسم ---------
@client.on(events.NewMessage(pattern=r"\.تشغيل الاسم"))
async def start_auto_name(event):
    global auto_name
    auto_name = True
    msg = await event.edit("✅ تم تشغيل الاسم الوقتي.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"\.ايقاف الاسم"))
async def stop_auto_name(event):
    global auto_name
    auto_name = False
    msg = await event.edit("🛑 تم إيقاف الاسم الوقتي.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- أمر فحص ---------
@client.on(events.NewMessage(pattern=r"\.فحص"))
async def ping(event):
    msg = await event.edit("✅ البوت شغال وبأفضل حال!")
    try:
        await client.send_message("me", "✨ حياتي الصعب، البوت شغال.")
    except Exception:
        pass
    await asyncio.sleep(10)
    await msg.delete()

# --------- أمر كشف معلومات القروب أو القناة ---------
@client.on(events.NewMessage(pattern=r"\.كشف"))
async def cmd_kashf(event):
    chat = await event.get_chat()
    if chat:
        try:
            if getattr(chat, 'megagroup', False) or getattr(chat, 'broadcast', False):
                full = await client(GetFullChannelRequest(chat))
                title = full.chats[0].title
                id_ = full.chats[0].id
                members_count = full.full_chat.participants_count
                about = full.full_chat.about or "لا يوجد وصف"
            else:
                full = await client(GetFullChatRequest(chat))
                title = full.chats[0].title
                id_ = full.chats[0].id
                members_count = len(full.full_chat.participants)
                about = full.full_chat.about or "لا يوجد وصف"
        except Exception:
            title = getattr(chat, 'title', 'لا يمكن جلب الاسم')
            id_ = getattr(chat, 'id', 'لا يمكن جلب الايدي')
            members_count = "لا يمكن جلب العدد"
            about = "لا يمكن جلب الوصف"
        text = (f"📊 معلومات:\n"
                f"🔹 الاسم: {title}\n"
                f"🔹 الايدي: `{id_}`\n"
                f"🔹 عدد الأعضاء: {members_count}\n"
                f"🔹 الوصف:\n{about}")
        await event.reply(text)
    else:
        await event.reply("❌ لم أتمكن من الحصول على معلومات هذه المحادثة.")

# --------- قائمة الأوامر المطورة ---------
@client.on(events.NewMessage(pattern=r"\.اوامر"))
async def list_commands(event):
    commands_text = (
        "🧠 قائمة أوامر البوت - نسخة المطورين:\n\n"
        "🔹 .فحص\n"
        "  - التأكد من أن البوت يعمل.\n\n"
        "🔹 .كشف\n"
        "  - كشف معلومات القروب أو القناة (الاسم، الايدي، عدد الأعضاء، الوصف).\n\n"
        "🔹 .كتم (بالرد)\n"
        "  - كتم المستخدم للرد عليه في الخاص أو المجموعات.\n\n"
        "🔹 .الغاء الكتم (بالرد)\n"
        "  - فك الكتم عن المستخدم.\n\n"
        "🔹 .قائمة الكتم\n"
        "  - عرض قائمة المستخدمين المكتومين (خاص ومجموعات).\n\n"
        "🔹 .مسح الكتم\n"
        "  - مسح جميع المكتومين من القوائم.\n\n"
        "🔹 .تفعيل الترحيب\n"
        "  - تفعيل رسالة الترحيب في القروب.\n\n"
        "🔹 .تعطيل الترحيب\n"
        "  - تعطيل رسالة الترحيب.\n\n"
        "🔹 .وضع ترحيب [النص]\n"
        "  - حفظ نص الترحيب (يمكن استخدام {الاسم} و {يوزر}).\n\n"
        "🔹 .تقليد (بالرد)\n"
        "  - تفعيل التقليد لمستخدم معين (يرد على كل رسائله).\n\n"
        "🔹 .تقليد تعطيل (بالرد)\n"
        "  - تعطيل التقليد عن المستخدم.\n\n"
        "🔹 .تشغيل الاسم\n"
        "  - تشغيل تحديث الاسم التلقائي بالوقت.\n\n"
        "🔹 .ايقاف الاسم\n"
        "  - إيقاف تحديث الاسم التلقائي.\n\n"
    )
    await event.respond(commands_text)

# --------- كتم المستخدم ---------
@client.on(events.NewMessage(pattern=r"\.كتم$", func=lambda e: e.is_reply))
async def mute_user(event):
    reply = await event.get_reply_message()
    if not reply:
        msg = await event.edit("❌ لازم ترد على رسالة.")
        await asyncio.sleep(1)
        return await msg.delete()
    uid, cid = reply.sender_id, event.chat_id
    (muted_private if event.is_private else muted_groups.setdefault(cid, set())).add(uid)
    msg = await event.edit("🔇 تم الكتم.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- فك الكتم ---------
@client.on(events.NewMessage(pattern=r"\.الغاء الكتم$", func=lambda e: e.is_reply))
async def unmute_user(event):
    reply = await event.get_reply_message()
    if not reply:
        msg = await event.edit("❌ لازم ترد على رسالة.")
        await asyncio.sleep(1)
        return await msg.delete()
    uid, cid = reply.sender_id, event.chat_id
    (muted_private if event.is_private else muted_groups.get(cid, set())).discard(uid)
    msg = await event.edit("🔊 تم فك الكتم.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- حذف رسائل المكتومين + حفظ الصور المؤقتة ---------
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

# --------- قائمة الكتم ---------
@client.on(events.NewMessage(pattern=r"\.قائمة الكتم$"))
async def list_muted(event):
    text = "📋 المكتومين:\n\n"
    for uid in muted_private:
        try:
            user = await client.get_entity(uid)
            text += f"🔹 خاص: {user.first_name}\n"
        except Exception:
            continue
    for cid, users in muted_groups.items():
        if not users:
            continue
        try:
            chat = await client.get_entity(cid)
            text += f"\n🔸 {chat.title}:\n"
        except Exception:
            continue
        for uid in users:
            try:
                user = await client.get_entity(uid)
                text += f" - {user.first_name}\n"
            except Exception:
                continue
    await event.respond(text or "📭 لا يوجد مكتومين.")

# --------- مسح الكتم ---------
@client.on(events.NewMessage(pattern=r"\.مسح الكتم$"))
async def clear_mutes(event):
    muted_private.clear()
    muted_groups.clear()
    msg = await event.edit("🗑️ تم مسح المكتومين.")
    await asyncio.sleep(1)
    await msg.delete()

# --------- الترحيب ---------
@client.on(events.NewMessage(pattern=r"\.تفعيل الترحيب"))
async def enable_w(event):
    welcome_enabled[event.chat_id] = True
    msg = await event.edit("✅ تم تفعيل الترحيب.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"\.تعطيل الترحيب"))
async def disable_w(event):
    welcome_enabled[event.chat_id] = False
    msg = await event.edit("❌ تم تعطيل الترحيب.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"\.وضع ترحيب (.+)"))
async def set_welcome(event):
    welcome_message[event.chat_id] = event.pattern_match.group(1)
    await event.edit("💬 تم حفظ الترحيب.")
    await asyncio.sleep(1)
    await event.delete()

@client.on(events.ChatAction(func=lambda e: e.user_joined or e.user_added))
async def welcome_user(event):
    if not welcome_enabled.get(event.chat_id):
        return
    user = await event.get_user()
    name = user.first_name or "صديق"
    username = f"@{user.username}" if user.username else "بدون يوزر"
    msg = welcome_message.get(event.chat_id, "أهلاً {الاسم} {يوزر} في القروب 🌹")
    text = msg.replace("{الاسم}", name).replace("{يوزر}", username)
    await event.reply(text)

# --------- التقليد ---------
@client.on(events.NewMessage(pattern=r"\.تقليد$", func=lambda e: e.is_reply))
async def start_clone(event):
    reply = await event.get_reply_message()
    if not reply:
        msg = await event.edit("❌ لازم ترد على رسالة.")
        await asyncio.sleep(1)
        return await msg.delete()
    clone_list.add(reply.sender_id)
    msg = await event.edit("🤖 تم تفعيل التقليد.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(pattern=r"\.تقليد تعطيل$", func=lambda e: e.is_reply))
async def stop_clone(event):
    reply = await event.get_reply_message()
    if not reply:
        msg = await event.edit("❌ لازم ترد على رسالة.")
        await asyncio.sleep(1)
        return await msg.delete()
    clone_list.discard(reply.sender_id)
    msg = await event.edit("🛑 تم تعطيل التقليد.")
    await asyncio.sleep(1)
    await msg.delete()

@client.on(events.NewMessage(incoming=True))
async def handle_clone(event):
    if event.sender_id in clone_list:
        try:
            if event.text:
                await event.reply(event.text)
            elif event.media:
                await event.reply(file=await event.download_media())
        except Exception:
            pass

# --------- بدء اللوب ---------
async def main():
    await client.start()
    asyncio.create_task(update_name_loop())  # تشغيل اللوب في الخلفية
    print("🚀 البوت شغال...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
