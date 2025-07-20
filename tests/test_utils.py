import unittest
from unittest.mock import AsyncMock, MagicMock
import asyncio
from utils import is_owner, qedit, send_media_safe, delete_after


class TestUtils(unittest.TestCase):
    def test_is_owner(self):
        client = AsyncMock()
        event = MagicMock()
        event.sender_id = 123
        client.get_me = AsyncMock(return_value=MagicMock(id=123))
        self.assertTrue(asyncio.run(is_owner(client, event)))

    def test_is_not_owner(self):
        client = AsyncMock()
        event = MagicMock()
        event.sender_id = 456
        client.get_me = AsyncMock(return_value=MagicMock(id=123))
        self.assertFalse(asyncio.run(is_owner(client, event)))

    def test_qedit(self):
        event = AsyncMock()
        asyncio.run(qedit(event, "test"))
        event.edit.assert_called_with("test", parse_mode="html")
        event.delete.assert_called_once()

    def test_send_media_safe(self):
        client = AsyncMock()
        asyncio.run(send_media_safe(client, "dest", "media"))
        client.send_file.assert_called_with("dest", "media", caption=None, ttl=None)

    def test_delete_after(self):
        msg = AsyncMock()
        asyncio.run(delete_after(msg, 0.1))
        msg.delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
