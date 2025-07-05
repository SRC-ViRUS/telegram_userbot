from telethon import TelegramClient, events
from datetime import datetime
import os

api_id = 11765349
api_hash = '67d3351652cc42239a42df8c17186d49'
session = 'userbot'

client = TelegramClient(session, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def save_auto(event):
    if not event.is_private or not event.media:
        return

    try:
        sender = await event.get_sender()
        if getattr(sender, 'bot', False):
            return

        # تحميل كامل ومحلي لتجنب مشاكل الجزئية
        file_path = await event.download_media()
        if not file_path or not os.path.exists(file_path):
            return

        # معلومات المرسل
        name = sender.first_name or "غير معروف"
        user_id = sender.id
        username = f"@{sender.username}" if sender.username else "لا يوجد"
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S'
        )

        caption = f"""📥 وسائط واردة:
👤 الاسم: {name}
🆔 الرقم: {user_id}
🔗 يوزر: {username}
🕓 الوقت: {time_str}
"""

        await client.send_message("me", caption)
        await client.send_file("me", file_path)

        # حذف الملف بعد الإرسال مباشرة
        os.remove(file_path)

    except Exception as e:
        print(f"❌ خطأ أثناء الإرسال: {e}")

print("🚀 البوت يعمل الآن بدقة وسرعة وبدون أخطاء تحميل.")
client.start()
client.run_until_disconnected()
