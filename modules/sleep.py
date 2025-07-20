import asyncio
import datetime
from telethon import events
from utils import is_owner, delete_after

sleep_mode = False
sleep_reason = ""
sleep_start = None
custom_reply = ""


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.سليب(?: (.+))?$"))
    async def sleep_command(event):
        global sleep_mode, sleep_reason, sleep_start, custom_reply

        if not await is_owner(client, event):
            return

        sleep_mode = True
        sleep_reason = event.pattern_match.group(1) or "غير متوفر حالياً"
        sleep_start = datetime.datetime.now()
        custom_reply = ""

        await event.delete()
        msg = await event.respond(
            f"""🟡 <b>تم تفعيل وضع السليب</b>
💬 <b>السبب:</b> {sleep_reason}
⏱️ <b>منذ:</b> 0 دقيقة و 0 ثانية""",
            parse_mode="html",
        )
        asyncio.create_task(delete_after(msg, 2))

    @client.on(events.NewMessage(pattern=r"^\.سكون(?: (.+))?$"))
    async def static_sleep_command(event):
        global sleep_mode, sleep_reason, sleep_start, custom_reply

        if not await is_owner(client, event):
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

        if not sleep_mode or await is_owner(client, event):
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
                elapsed_str = (
                    f"{h} ساعة و {m} دقيقة و {s} ثانية"
                    if h
                    else f"{m} دقيقة و {s} ثانية"
                )
                text = (
                    f"🔕 المستخدم غير نشط منذ {elapsed_str}\n💬 السبب: {sleep_reason}"
                )

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
        elapsed_str = (
            f"{h} ساعة و {m} دقيقة و {s} ثانية" if h else f"{m} دقيقة و {s} ثانية"
        )

        await client.send_message(
            "me",
            f"""🔔 <b>تم إلغاء وضع السكون</b>
📝 <b>السبب:</b> {sleep_reason}
⏱️ <b>استمر:</b> {elapsed_str}
👤 <b>تم الإلغاء بإرسال رسالة.</b>""",
            parse_mode="html",
        )

        sleep_mode = False
        sleep_reason = ""
        sleep_start = None
        custom_reply = ""

        msg = await event.respond("❌ تم إلغاء السكون.")
        asyncio.create_task(delete_after(msg, 2))
