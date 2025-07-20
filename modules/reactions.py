from telethon import events, functions, types
from utils import is_owner

reaction_map = {}  # user_id: emoji


def register(client):
    @client.on(events.NewMessage(pattern=r"^\.ازعاج(.+)"))
    async def enable_reaction(event):
        if not event.is_reply:
            await event.reply(
                "❗ لازم ترد على رسالة الشخص وتكتب الأمر مع الإيموجي\nمثال: `.ازعاج😁`",
                delete_in=5,
            )
            return

        try:
            await event.delete()  # حذف رسالة الأمر فوراً
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
            await event.reply(
                "❗ لازم ترد على رسالة الشخص حتى أوقف التفاعل.", delete_in=5
            )
            return

        try:
            await event.delete()  # حذف رسالة الأمر فوراً
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
        sender = await event.get_sender()
        emoji = reaction_map.get(sender.id)
        if emoji:
            try:
                await client(
                    functions.messages.SendReactionRequest(
                        peer=event.chat_id,
                        msg_id=event.id,
                        reaction=[types.ReactionEmoji(emoticon=emoji)],
                    )
                )
            except Exception as e:
                print(f"❌ خطأ أثناء إرسال التفاعل: {e}")
