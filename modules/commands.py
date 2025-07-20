from telethon import events
from utils import is_owner
from modules.command_handler import command


@command("الاوامر", "عرض قائمة الأوامر")
async def cmds(event):
    # This command is handled by the command_handler, so we don't need to do anything here.
    pass


@command("فحص", "فحص البوت")
async def check(event):
    txt = "✅ البوت يعمل"
    await event.edit(txt, parse_mode="html")
