import asyncio
from telethon import events, functions
from utils import is_owner


class BioRotator:
    def __init__(self, client, interval=60):
        self.client = client
        self.bios = []
        self.index = 0
        self.interval = interval
        self.task = None
        self.running = False
        self.temp_task = None
        self.temp_active = False
        self.original = {}

    async def edit_del(self, event, text, delay=3):
        await event.edit(text)
        await asyncio.sleep(delay)
        await event.delete()

    async def start(self, event):
        if self.running:
            return await self.edit_del(event, "⚠️ شغّال من قبل.")
        if not self.bios:
            return await self.edit_del(event, "⚠️ لا توجد بايوهات.")
        self.running = True
        self.task = asyncio.create_task(self.loop_bio())
        await self.edit_del(event, f"✅ بدأ التغيير كل {self.interval} ثانية.")

    async def stop(self, event):
        if not self.running:
            return await self.edit_del(event, "⚠️ غير مفعل.")
        self.running = False
        self.task.cancel()
        await self.edit_del(event, "🛑 تم الإيقاف.")

    async def loop_bio(self):
        while self.running:
            try:
                await self.client(
                    functions.account.UpdateProfileRequest(about=self.bios[self.index])
                )
                self.index = (self.index + 1) % len(self.bios)
            except:
                pass
            await asyncio.sleep(self.interval)

    async def add(self, event):
        bio = event.pattern_match.group(1).strip()
        if not bio:
            return await self.edit_del(event, "❌ لا يمكن إضافة بايو فارغ.")
        self.bios.append(bio)
        await self.edit_del(
            event, f"✅ تم إضافة البايو\nعدد البايوهات: {len(self.bios)}"
        )

    async def show(self, event):
        if not self.bios:
            return await self.edit_del(event, "⚠️ القائمة فارغة.")
        msg = "\n".join([f"{i+1}. {x}" for i, x in enumerate(self.bios)])
        await event.edit(f"📋 البايوهات:\n\n{msg}")
        await asyncio.sleep(10)
        await event.delete()

    async def clear(self, event):
        self.bios.clear()
        self.index = 0
        await self.edit_del(event, "🗑️ تم المسح.")

    async def interval_set(self, event):
        try:
            sec = int(event.pattern_match.group(1))
            if sec < 5:
                return await self.edit_del(event, "❌ أقل شيء 5 ثواني.")
            self.interval = sec
            if self.running:
                await self.stop(event)
                await self.start(event)
            else:
                await self.edit_del(event, f"⏱️ المدة الآن {sec} ثانية.")
        except:
            await self.edit_del(event, "❌ استخدم: `.مدة_بايو 60`")

    async def remove(self, event):
        try:
            i = int(event.pattern_match.group(1)) - 1
            if i < 0 or i >= len(self.bios):
                return await self.edit_del(event, "❌ رقم غير صالح.")
            removed = self.bios.pop(i)
            await self.edit_del(event, f"🗑️ حذف: {removed}")
        except:
            await self.edit_del(event, "❌ استخدم: `.حذف_بايو 2`")

    async def jump(self, event):
        try:
            i = int(event.pattern_match.group(1)) - 1
            if i < 0 or i >= len(self.bios):
                return await self.edit_del(event, "❌ رقم غير صالح.")
            self.index = i
            await self.edit_del(event, f"↪️ بدأ من البايو {i+1}")
        except:
            await self.edit_del(event, "❌ استخدم: `.اذهب_لبايو 3`")

    async def temp(self, event):
        if self.temp_active:
            return await self.edit_del(event, "⚠️ بايو مؤقت مفعل، أوقفه أولاً.")
        text = event.pattern_match.group(1)
        if "/" not in text:
            return await self.edit_del(event, "❌ استخدم `.بايو_وقتي نص /MM:SS`")
        bio, t = text.rsplit("/", 1)
        try:
            m, s = map(int, t.split(":"))
            sec = m * 60 + s
        except:
            return await self.edit_del(event, "❌ وقت غير صحيح.")

        user = await self.client.get_me()
        self.original = {
            "first": user.first_name or "",
            "last": user.last_name or "",
            "bio": user.about or "",
        }

        try:
            await self.client(
                functions.account.UpdateProfileRequest(
                    first_name=bio, last_name="", about=bio
                )
            )
            await self.edit_del(event, f"✅ تم التعيين مؤقتًا لمدة {sec} ثانية.")
        except Exception as e:
            return await self.edit_del(event, f"❌ {e}")

        self.temp_active = True

        async def revert():
            await asyncio.sleep(sec)
            try:
                await self.client(
                    functions.account.UpdateProfileRequest(
                        first_name=self.original["first"],
                        last_name=self.original["last"],
                        about=self.original["bio"],
                    )
                )
            except:
                pass
            self.temp_active = False

        self.temp_task = asyncio.create_task(revert())

    async def stop_temp(self, event):
        if not self.temp_active:
            return await self.edit_del(event, "⚠️ لا يوجد بايو مؤقت.")
        if self.temp_task:
            self.temp_task.cancel()
        try:
            await self.client(
                functions.account.UpdateProfileRequest(
                    first_name=self.original["first"],
                    last_name=self.original["last"],
                    about=self.original["bio"],
                )
            )
        except:
            pass
        self.temp_active = False
        await self.edit_del(event, "🛑 تم إيقاف البايو المؤقت.")


def register(client):
    bio = BioRotator(client)

    @client.on(events.NewMessage(pattern=r"^\.اضف_بايو (.+)"))
    async def _(e):
        await bio.add(e)

    @client.on(events.NewMessage(pattern=r"^\.عرض_البايوهات$"))
    async def _(e):
        await bio.show(e)

    @client.on(events.NewMessage(pattern=r"^\.تشغيل_البايو$"))
    async def _(e):
        await bio.start(e)

    @client.on(events.NewMessage(pattern=r"^\.ايقاف_البايو$"))
    async def _(e):
        await bio.stop(e)

    @client.on(events.NewMessage(pattern=r"^\.مسح_البايوهات$"))
    async def _(e):
        await bio.clear(e)

    @client.on(events.NewMessage(pattern=r"^\.مدة_بايو (\d+)$"))
    async def _(e):
        await bio.interval_set(e)

    @client.on(events.NewMessage(pattern=r"^\.حذف_بايو (\d+)$"))
    async def _(e):
        await bio.remove(e)

    @client.on(events.NewMessage(pattern=r"^\.اذهب_لبايو (\d+)$"))
    async def _(e):
        await bio.jump(e)

    @client.on(events.NewMessage(pattern=r"^\.بايو_وقتي (.+)$"))
    async def _(e):
        await bio.temp(e)

    @client.on(events.NewMessage(pattern=r"^\.ايقاف_بايو_وقتي$"))
    async def _(e):
        await bio.stop_temp(e)
