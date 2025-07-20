import inspect
from telethon import events
from utils import is_owner

COMMANDS = {}


def command(name, description, usage=None):
    def decorator(func):
        async def wrapper(event):
            if not await is_owner(event.client, event):
                return
            await func(event)

        COMMANDS[name] = {
            "description": description,
            "usage": usage,
            "function": wrapper,
        }
        return wrapper

    return decorator


def register(client):
    for name, cmd in COMMANDS.items():
        client.on(events.NewMessage(pattern=rf"^\.{name}$"))(cmd["function"])

    @client.on(events.NewMessage(pattern=r"^\.الاوامر$"))
    async def list_commands(event):
        if not await is_owner(client, event):
            return

        txt = "<b>💡 الأوامر:</b>\n\n"
        for name, cmd in sorted(COMMANDS.items()):
            txt += f"<code>.{name}</code>"
            if cmd["usage"]:
                txt += f" {cmd['usage']}"
            txt += f" - {cmd['description']}\n"

        await event.edit(txt, parse_mode="html")
