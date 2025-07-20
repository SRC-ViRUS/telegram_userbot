import asyncio
import random
from telethon import events
from utils import is_owner, qedit

mention_messages = [
    "ﻣـسٱ۽ آࢦخـيࢪ يصـاك🫀🤍🍯.",
    "عـࢪفنـه ؏ـليـك؟ 🌚💗",
    "مـن وين آݪحـ̷ِْــٰــ۫͜ݪو 🌝",
    "نتـَٰــۘ❀ـَٰـعرف بــݪطــف",
    "كافي نوم 🤍",
    "هَــْهلااا حـيلي 🤍",
    "ياصـف؟ 🗿",
    "مِمجَࢪډ شعوٚࢪ 🧘🏾‍♀️.",
    "نـايـم ڪـاعد🫦؟",
    "اللطف مخلوق حياتي 💖",
    "ويـنك 🙄🤍",
    "هل تقبل الزواج مني🥲",
    "ويـن طـامـس 🙄♥.",
    "صبـاح اݪخـير 🫂♥.",
    "اكلتك المفضلهہَ شننۅ ؟..",
    "هـلا حٝـب 💙",
    "بݪشش اتصال تع يحلو ✨🤍",
    "⌁︙ممكن نتعرفف🙂🍭",
    "أصبح علئ صوتك🫦.",
    "اެحَسَسَ اެخذت ڪِلبي ححَࢪفياا 😣ِْ🤍 𓍲 .",
    "شِكد ععَدډ الي منطِيهم بلۅك؟.. 🥹",
    "ۿهلا يععَمࢪي 🏷َِ💗",
    "مسس يـَפــَݪۄ  💞🫶🏻 ",
    "صــح ألــنــوم يــحـلو 💕😴",
    "صباحوو توت بالقشطه 🦋🍒",
    "شونك يحلو 😉 ••",
    "مس يحلو 🌚👀 ••",
    "ويــــن طامس يحلو/ه😒 ••",
    "هاذا الحلو كاتلني يعمه ❤️",
    "ييحٍحٍ مۆشُ نــفــر عٍآفَيَهّ وُرٍبَي🥺💞🦋",
    "شلخبار 🚶🏿‍♂️..🙂",
    "شكد طولك🌝؟",
    "مـشتاق لعيونك. 🌝🍫.",
]
mention_enabled = True


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.منشن$"))
    async def mention_all(event):
        global mention_enabled
        if not await is_owner(client, event):
            return
        if not event.is_group:
            return await qedit(event, "❌ للڨروبات فقط.")
        if not mention_enabled:
            return await qedit(event, "🚫 المنشن متوقف.")
        await event.edit("🔄 تجميع الأعضاء ...")
        users = [
            u
            async for u in client.iter_participants(event.chat_id)
            if not u.bot and not u.deleted
        ]
        if not users:
            return await qedit(event, "⚠️ ماكو أعضاء.")
        await event.edit(f"🚀 جارٍ منشن {len(users)} عضو...")
        used = set()
        for u in users:
            if not mention_enabled:
                return await event.respond("⛔ أُوقف المنشن.")
            avail = [m for m in mention_messages if m not in used] or mention_messages
            msg = random.choice(avail)
            used.add(msg)
            mention = f"<a href='tg://user?id={u.id}'>{u.first_name or 'صديق'}</a>"
            try:
                await client.send_message(
                    event.chat_id, f"{msg} {mention}", parse_mode="html"
                )
                await asyncio.sleep(5)
            except Exception as e:
                print("خطأ منشن:", e)
        await event.respond("✅ انتهى المنشن.")

    @client.on(events.NewMessage(pattern=r"^\.لاتمنشن$"))
    async def disable_mention(event):
        global mention_enabled
        if not await is_owner(client, event):
            return
        mention_enabled = False
        await qedit(event, "🛑 أوقفنا المنشن.")

    @client.on(events.NewMessage(pattern=r"^\.منشن تفعيل$"))
    async def enable_mention(event):
        global mention_enabled
        if not await is_owner(client, event):
            return
        mention_enabled = True
        await qedit(event, "✅ فعّلنا المنشن.")

    @client.on(events.NewMessage(pattern=r"^\.منشن حالة$"))
    async def mention_status(event):
        if not await is_owner(client, event):
            return
        await qedit(event, f"📍 المنشن: {'✅ مفعل' if mention_enabled else '🛑 متوقف'}")
