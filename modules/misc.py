import asyncio
import datetime
import os
import random
from telethon import events
from telethon.tl.functions.photos import GetUserPhotosRequest
from utils import is_owner, qedit, send_media_safe

repeat_task = None


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.صورة البروفايل$"))
    async def profile_photo(event):
        if not await is_owner(client, event):
            return
        me = await client.get_me()
        photos = await client(GetUserPhotosRequest(me.id, offset=0, max_id=0, limit=1))
        if photos.photos:
            await send_media_safe(
                client, "me", photos.photos[0], "🖼️ آخر صورة بروفايل"
            )
            await qedit(event, "✅ أُرسلت الصورة إلى الرسائل المحفوظة.")
        else:
            await qedit(event, "❌ لا توجد صورة بروفايل.")

    @client.on(events.NewMessage(pattern=r"^\.كشف$"))
    async def info(event):
        if not await is_owner(client, event) or not event.is_group:
            return await qedit(event, "❌ هذا الأمر للمجموعات فقط.")
        chat = await event.get_chat()
        out = f"🏷️ {chat.title}\n🆔 {chat.id}\n👥 {getattr(chat,'participants_count','?')}\n📛 @{getattr(chat,'username','لا يوجد')}"
        await qedit(event, out, 5)

    @client.on(events.NewMessage(pattern=r"^\.ايدي$"))
    async def get_id(event):
        if not await is_owner(client, event):
            return
        if event.is_reply:
            r = await event.get_reply_message()
            await qedit(event, f"🆔 <code>{r.sender_id}</code>")
        else:
            await qedit(event, f"🆔 آيديك: <code>{event.sender_id}</code>")

    @client.on(events.NewMessage(pattern=r"^\.البنق$"))
    async def ping(event):
        if not await is_owner(client, event):
            return
        start = datetime.datetime.now()
        m = await event.edit("🏓 ...")
        diff = (datetime.datetime.now() - start).microseconds / 1000
        await m.edit(f"🏓 <b>{diff:.2f}ms</b>", parse_mode="html")
        await asyncio.sleep(5)
        await m.delete()

    @client.on(events.NewMessage(pattern=r"^\.تكرار تلقائي (\d+) (.+)$"))
    async def auto_repeat(event):
        if not await is_owner(client, event):
            return
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
                    print("خطأ تكرار:", e)
                await asyncio.sleep(seconds)

        repeat_task = asyncio.create_task(loop())
        await qedit(event, f"🔁 بدأ التكرار كل {seconds} ث.")

    @client.on(events.NewMessage(pattern=r"^\.ايقاف التكرار$"))
    async def stop_repeat(event):
        if not await is_owner(client, event):
            return
        global repeat_task
        if repeat_task:
            repeat_task.cancel()
            repeat_task = None
            await qedit(event, "⛔ أوقفنا التكرار.")
        else:
            await qedit(event, "⚠️ لا يوجد تكرار فعال.")

    @client.on(events.NewMessage(pattern=r"^\.تهكير(?: (.+))?"))
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
            return await event.reply(
                "❌ لم يتم العثور على المستخدم. رد على شخص أو اكتب يوزره.\nمثال: `.تهكير @username`"
            )

        name = user.first_name or "شخص"
        username = f"@{user.username}" if user.username else name

        fake_ip = ".".join(str(random.randint(10, 255)) for _ in range(4))
        fake_country = random.choice(
            [
                "الولايات المتحدة الأمريكية 🇺🇸",
                "روسيا 🇷🇺",
                "كوريا الشمالية 🇰🇵",
                "الصين 🇨🇳",
                "إيران 🇮🇷",
            ]
        )
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
            f"↳ Target IP: {fake_ip}",
            f"↳ Location: {fake_country}",
            f"↳ Phone number linked: {fake_phone}",
            "▂▃▄▅▆▇█▓▒░ BREACH COMPLETE ░▒▓█▇▆▅▄▃▂",
        ]

        try:
            msg = event.message

            await msg.edit(f"💀 بدء تهكير {username} ...\n")
            await asyncio.sleep(2)

            for code in long_scary_codes:
                # نعرض الكود مع تأثير أسطر مشفرة عشوائية
                fake_encrypted = "".join(
                    random.choice("0123456789ABCDEF") for _ in range(40)
                )
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
            await msg.edit(
                f"🚨 جاري رفع الصور إلى الموقع التالي:\n<a href='{fake_link}'>{fake_link}</a>",
                parse_mode="html",
                link_preview=False,
            )
            await asyncio.sleep(4)

            await msg.edit("🔥 جارييييي فرمتتت التلفون ...")
            await asyncio.sleep(6)

            await msg.delete()

        except Exception as e:
            print("خطأ في التهكير:", e)
