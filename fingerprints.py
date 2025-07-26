import json
import os
from telethon import events
from telethon.errors import FileReferenceExpiredError
from utils import send_media_safe

FINGERPRINTS_FILE = "fingerprints.json"
MAX_FINGERPRINTS = 200


def load_fingerprints():
    if not os.path.exists(FINGERPRINTS_FILE):
        return {}
    try:
        with open(FINGERPRINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # migrate old structure {chat_id: {name: id}}
        if data and all(isinstance(v, dict) for v in data.values()):
            first = next(iter(data.values()))
            if first and isinstance(next(iter(first.values()), None), int):
                migrated = {}
                for chat, vals in data.items():
                    for n, i in vals.items():
                        migrated[n] = {"chat": int(chat), "id": i}
                data = migrated
        return data
    except Exception:
        return {}


def save_fingerprints(data):
    with open(FINGERPRINTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register(client):
    fingerprints = load_fingerprints()

    @client.on(events.NewMessage(pattern=r'^\.اضف بصمه (.+)$'))
    async def add_fingerprint(event):
        name = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("↯︙رد على الرسالة اللي تريد تحفظها كبصمة.")
        if len(fingerprints) >= MAX_FINGERPRINTS:
            return await event.reply(
                f"↯︙وصلت الحد الأقصى ({MAX_FINGERPRINTS}) من البصمات.")
        fingerprints[name] = {"chat": reply.chat_id, "id": reply.id}
        save_fingerprints(fingerprints)
        await event.reply(f"↯︙تم حفظ البصمة باسم `{name}`.")

    @client.on(events.NewMessage(pattern=r'^\.اسم البصمه (.+)$'))
    async def send_fingerprint(event):
        name = event.pattern_match.group(1).strip()
        if name not in fingerprints:
            await event.reply(f"↯︙لا توجد بصمة بهذا الاسم: `{name}`.")
            return await event.delete()

        data = fingerprints[name]
        try:
            msg = await client.get_messages(data["chat"], ids=data["id"])
            if msg.media:
                try:
                    await msg.forward_to(event.chat_id)
                except FileReferenceExpiredError:
                    await send_media_safe(client, event.chat_id, msg.media, caption=msg.message or None)
            else:
                await client.send_message(event.chat_id, msg.message or "")
        except Exception:
            await event.reply("↯︙فشل إرسال البصمة. قد تكون محذوفة.")
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.بصماتي$'))
    async def list_fingerprints(event):
        names = list(fingerprints.keys())
        if not names:
            return await event.reply("↯︙لا توجد أي بصمات محفوظة.")
        text = "↯︙قائمة بصماتك:\n" + "\n".join(f"• {n}" for n in names)
        await event.reply(text)

    @client.on(events.NewMessage(pattern=r'^\.احذف بصمه (.+)$'))
    async def delete_fingerprint(event):
        name = event.pattern_match.group(1).strip()
        if name in fingerprints:
            del fingerprints[name]
            save_fingerprints(fingerprints)
            await event.reply(f"↯︙تم حذف البصمة `{name}`.")
        else:
            await event.reply("↯︙لا توجد بصمة بهذا الاسم.")

    @client.on(events.NewMessage(pattern=r'^\.عدد البصمات$'))
    async def fingerprint_count(event):
        count = len(fingerprints)
        await event.reply(f"↯︙عدد البصمات المحفوظة: {count}/{MAX_FINGERPRINTS}")

    @client.on(events.NewMessage(pattern=r'^\.بصمات$'))
    async def fingerprints_markdown_help(event):
        text = (
            "🔖 **قائمة أوامر البصمات**\n\n"
            "• `.اضف بصمه [الاسم]`\n"
            "  └─ لحفظ الرسالة اللي رديت عليها باسم.\n\n"
            "• `.اسم البصمه [الاسم]`\n"
            "  └─ إرسال البصمة حسب الاسم.\n\n"
            "• `.بصماتي`\n"
            "  └─ عرض كل البصمات المحفوظة.\n\n"
            "• `.احذف بصمه [الاسم]`\n"
            "  └─ حذف بصمة معينة من التخزين.\n\n"
            "• `.عدد البصمات`\n"
            "  └─ كم بصمة محفوظة حالياً.\n\n"
            "• `.بصمات`\n"
            "  └─ عرض هذه القائمة.\n\n"
            "**• الحد الأقصى:** `200 بصمة محفوظة` ✅"
        )
        await event.reply(text, parse_mode='md')

__all__ = ["register"]
