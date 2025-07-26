import json
import os
from telethon import events

FINGERPRINTS_FILE = "fingerprints.json"
MAX_FINGERPRINTS = 200


def load_fingerprints():
    if not os.path.exists(FINGERPRINTS_FILE):
        return {}
    try:
        with open(FINGERPRINTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
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
        chat_id = str(event.chat_id)
        if chat_id not in fingerprints:
            fingerprints[chat_id] = {}
        if len(fingerprints[chat_id]) >= MAX_FINGERPRINTS:
            return await event.reply(
                f"↯︙وصلت الحد الأقصى ({MAX_FINGERPRINTS}) من البصمات.")
        fingerprints[chat_id][name] = reply.id
        save_fingerprints(fingerprints)
        await event.reply(f"↯︙تم حفظ البصمة باسم `{name}`.")

    @client.on(events.NewMessage(pattern=r'^\.(\S+)$'))
    async def send_fingerprint(event):
        name = event.pattern_match.group(1).strip()
        chat_id = str(event.chat_id)

        if chat_id not in fingerprints or name not in fingerprints[chat_id]:
            # allow other commands to proceed if name isn't a fingerprint
            return

        try:
            msg_id = fingerprints[chat_id][name]
            await client.forward_messages(event.chat_id, msg_id, chat_id)
        except Exception:
            await event.reply("↯︙فشل إرسال البصمة. قد تكون محذوفة.")

    @client.on(events.NewMessage(pattern=r'^\.بصماتي$'))
    async def list_fingerprints(event):
        chat_id = str(event.chat_id)
        names = list(fingerprints.get(chat_id, {}).keys())
        if not names:
            return await event.reply("↯︙لا توجد أي بصمات محفوظة.")
        text = "↯︙قائمة بصماتك:\n" + "\n".join(f"• {n}" for n in names)
        await event.reply(text)

    @client.on(events.NewMessage(pattern=r'^\.احذف بصمه (.+)$'))
    async def delete_fingerprint(event):
        name = event.pattern_match.group(1).strip()
        chat_id = str(event.chat_id)
        if chat_id in fingerprints and name in fingerprints[chat_id]:
            del fingerprints[chat_id][name]
            save_fingerprints(fingerprints)
            await event.reply(f"↯︙تم حذف البصمة `{name}`.")
        else:
            await event.reply("↯︙لا توجد بصمة بهذا الاسم.")

    @client.on(events.NewMessage(pattern=r'^\.عدد البصمات$'))
    async def fingerprint_count(event):
        chat_id = str(event.chat_id)
        count = len(fingerprints.get(chat_id, {}))
        await event.reply(f"↯︙عدد البصمات المحفوظة: {count}/{MAX_FINGERPRINTS}")

    @client.on(events.NewMessage(pattern=r'^\.بصمات$'))
    async def fingerprints_markdown_help(event):
        text = (
            "🔖 **قائمة أوامر البصمات**\n\n"
            "• `.اضف بصمه [الاسم]`\n"
            "  └─ لحفظ الرسالة اللي رديت عليها باسم.\n\n"
            "• `.[الاسم]`\n"
            "  └─ إرسال البصمة بكتابة اسمها مباشرة.\n\n"
            "• `.بصماتي`\n"
            "  └─ عرض كل البصمات المحفوظة.\n\n"
            "• `.احذف بصمه [الاسم]`\n"
            "  └─ حذف بصمة معينة من التخزين.\n\n"
            "• `.عدد البصمات`\n"
            "  └─ كم بصمة محفوظة حالياً.\n\n"
            "• `.بصمات`\n"
            "  └─ عرض هذه القائمة.\n\n"
            "**• الحد الأقصى:** `200 بصمة لكل محادثة` ✅"
        )
        await event.reply(text, parse_mode='md')

__all__ = ["register"]
