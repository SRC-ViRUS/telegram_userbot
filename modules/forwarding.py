import asyncio
from telethon import events, functions
from config import TEMP_USER

private_group = None
group_group = None


def register(client):
    @client.on(events.NewMessage)
    async def auto_forward(event):
        global private_group, group_group

        try:
            sender = await event.get_sender()
            if not sender or sender.bot:
                return  # تجاهل البوتات

            if not private_group or not group_group:
                me = await client.get_me()

                # إنشاء كروب "خاص"
                if not private_group:
                    try:
                        result = await client(
                            functions.messages.CreateChatRequest(
                                users=[TEMP_USER], title="خاص"
                            )
                        )
                        await asyncio.sleep(1)
                        await client(
                            functions.messages.DeleteChatUserRequest(
                                chat_id=result.chats[0].id, user_id=TEMP_USER
                            )
                        )
                        private_group = result.chats[0]
                    except Exception as e:
                        print(f"⚠️ خطأ في إنشاء كروب خاص: {e}")
                        return

                # إنشاء كروب "كروبات"
                if not group_group:
                    try:
                        result = await client(
                            functions.messages.CreateChatRequest(
                                users=[TEMP_USER], title="كروبات"
                            )
                        )
                        await asyncio.sleep(1)
                        await client(
                            functions.messages.DeleteChatUserRequest(
                                chat_id=result.chats[0].id, user_id=TEMP_USER
                            )
                        )
                        group_group = result.chats[0]
                    except Exception as e:
                        print(f"⚠️ خطأ في إنشاء كروب كروبات: {e}")
                        return

            # --- من الكروبات ---
            if event.is_group:
                try:
                    sender = await event.get_sender()
                    name = sender.first_name or "مجهول"
                    link = (
                        f"https://t.me/c/{str(event.chat_id)[4:]}/{event.id}"
                        if str(event.chat_id).startswith("-100")
                        else "❌ لا يوجد رابط"
                    )
                    msg = f"📥 رسالة من كروب:\n👤 <b>{name}</b>\n🔗 <a href='{link}'>رابط الرسالة</a>"
                    await client.send_message(
                        group_group.id, msg, parse_mode="html"
                    )
                    await client.forward_messages(group_group.id, event.message)
                except Exception as e:
                    print(f"⚠️ خطأ في تحويل كروب: {e}")

            # --- من الخاص ---
            elif event.is_private:
                try:
                    name = sender.first_name or "مجهول"
                    msg = f"📨 رسالة خاصة:\n👤 <b>{name}</b>"
                    await client.send_message(
                        private_group.id, msg, parse_mode="html"
                    )
                    await client.forward_messages(private_group.id, event.message)
                except Exception as e:
                    print(f"⚠️ خطأ في تحويل خاص: {e}")

        except Exception as err:
            print(f"⚠️ خطأ عام: {err}")
